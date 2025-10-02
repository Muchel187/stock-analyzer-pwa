/**
 * API Manager with Intelligent Caching
 * Provides cache-first API access with automatic fallback to stale cache
 *
 * Features:
 * - IndexedDB caching with TTL
 * - Rate limit enforcement
 * - Batch request optimization
 * - Stale-while-revalidate strategy
 * - Automatic cache cleanup
 *
 * @class ApiManager
 */

import CACHE_DURATION, { CACHE_KEYS, getExpirationTime } from '../cache/CacheConfig.js';
import IndexedDBManager from '../cache/IndexedDBManager.js';
import RateLimiter from './RateLimiter.js';

class ApiManager {
    constructor() {
        this.cache = null;
        this.rateLimiter = null;
        this.baseURL = '/api';
        this.initialized = false;
    }

    /**
     * Initialize API Manager with IndexedDB and Rate Limiter
     * @returns {Promise<void>}
     */
    async init() {
        try {
            console.log('[ApiManager] Initializing...');

            // Initialize IndexedDB cache
            this.cache = new IndexedDBManager();
            await this.cache.init();

            // Initialize Rate Limiter
            this.rateLimiter = new RateLimiter(this.cache);

            // Start cleanup job (every hour)
            this._startCleanupJob();

            this.initialized = true;
            console.log('[ApiManager] Initialized successfully');
        } catch (error) {
            console.error('[ApiManager] Initialization failed:', error);
            throw error;
        }
    }

    /**
     * Get stock quote with caching
     * @param {string} symbol - Stock ticker symbol
     * @param {boolean} forceRefresh - Skip cache and fetch fresh data
     * @returns {Promise<Object>} Stock data
     */
    async getQuote(symbol, forceRefresh = false) {
        console.log(`[ApiManager] getQuote: ${symbol}, forceRefresh: ${forceRefresh}`);

        const cacheKey = CACHE_KEYS.quote(symbol);

        // 1. Check cache if not forceRefresh
        if (!forceRefresh) {
            const cached = await this.cache.get('quotes', cacheKey);
            if (cached) {
                console.log(`[ApiManager] Cache HIT for ${symbol}`);
                return { ...cached.data, fromCache: true };
            }
        }

        // 2. Check rate limits
        const canCall = await this.rateLimiter.checkLimit('stock_api');
        if (!canCall) {
            console.warn('[ApiManager] Rate limit reached, using stale cache');
            const stale = await this._getStaleCache('quotes', cacheKey);
            if (stale) {
                return { ...stale.data, fromCache: true, isStale: true };
            }
            throw new Error('Rate limit reached and no cache available');
        }

        // 3. Fetch from API
        try {
            const response = await fetch(`${this.baseURL}/stock/${symbol}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            // 4. Update cache
            const cacheData = {
                symbol: cacheKey,
                data: data,
                lastUpdated: Date.now(),
                ttl: getExpirationTime(CACHE_DURATION.QUOTE_STANDARD)
            };
            await this.cache.set('quotes', cacheData);

            // 5. Record API call
            await this.rateLimiter.recordCall('stock_api', { symbol, endpoint: 'quote' });

            console.log(`[ApiManager] API call successful for ${symbol}`);
            return { ...data, fromCache: false };

        } catch (error) {
            console.error(`[ApiManager] API call failed for ${symbol}:`, error);

            // Fallback to stale cache
            const stale = await this._getStaleCache('quotes', cacheKey);
            if (stale) {
                console.warn(`[ApiManager] Using stale cache for ${symbol}`);
                return { ...stale.data, fromCache: true, isStale: true, error: error.message };
            }

            throw error;
        }
    }

    /**
     * Get historical data with caching
     * @param {string} symbol - Stock ticker symbol
     * @param {string} period - Time period (1d, 1mo, 1y, etc.)
     * @param {boolean} forceRefresh - Skip cache
     * @returns {Promise<Object>} Historical data
     */
    async getHistoricalData(symbol, period = '1y', forceRefresh = false) {
        const cacheKey = CACHE_KEYS.historical(symbol, period);

        if (!forceRefresh) {
            const cached = await this.cache.get('historical', cacheKey);
            if (cached) {
                console.log(`[ApiManager] Cache HIT for historical ${symbol} ${period}`);
                return { ...cached.data, fromCache: true };
            }
        }

        try {
            const response = await fetch(`${this.baseURL}/stock/${symbol}/history?period=${period}`);
            if (!response.ok) throw new Error(`API error: ${response.status}`);

            const data = await response.json();

            const cacheData = {
                id: cacheKey,
                symbol: symbol,
                period: period,
                data: data,
                lastUpdated: Date.now(),
                ttl: getExpirationTime(CACHE_DURATION.HISTORICAL_DAY)
            };
            await this.cache.set('historical', cacheData);

            await this.rateLimiter.recordCall('stock_api', { symbol, endpoint: 'historical', period });

            return { ...data, fromCache: false };

        } catch (error) {
            console.error(`[ApiManager] Historical data fetch failed:`, error);
            const stale = await this._getStaleCache('historical', cacheKey);
            if (stale) {
                return { ...stale.data, fromCache: true, isStale: true };
            }
            throw error;
        }
    }

    /**
     * Get fundamentals with caching
     * @param {string} symbol - Stock ticker symbol
     * @param {boolean} forceRefresh - Skip cache
     * @returns {Promise<Object>} Fundamental data
     */
    async getFundamentals(symbol, forceRefresh = false) {
        const cacheKey = CACHE_KEYS.fundamentals(symbol);

        if (!forceRefresh) {
            const cached = await this.cache.get('fundamentals', cacheKey);
            if (cached) {
                return { ...cached.data, fromCache: true };
            }
        }

        // Fundamentals are included in quote response
        const quoteData = await this.getQuote(symbol, forceRefresh);

        const fundData = {
            symbol: cacheKey,
            data: {
                pe: quoteData.fundamental_analysis?.metrics?.pe_ratio,
                eps: quoteData.fundamental_analysis?.metrics?.eps,
                marketCap: quoteData.info?.market_cap,
                sector: quoteData.info?.sector,
                industry: quoteData.info?.industry,
                ...quoteData.fundamental_analysis
            },
            lastUpdated: Date.now(),
            ttl: getExpirationTime(CACHE_DURATION.FUNDAMENTALS)
        };

        await this.cache.set('fundamentals', fundData);
        return fundData.data;
    }

    /**
     * Batch get quotes for multiple symbols
     * @param {Array<string>} symbols - Array of stock symbols
     * @returns {Promise<Array>} Array of results
     */
    async batchGetQuotes(symbols) {
        console.log(`[ApiManager] Batch fetching ${symbols.length} quotes`);

        const results = [];
        const toFetch = [];

        // 1. Check cache for all symbols
        for (const symbol of symbols) {
            const cacheKey = CACHE_KEYS.quote(symbol);
            const cached = await this.cache.get('quotes', cacheKey);
            if (cached) {
                results.push({
                    symbol,
                    data: { ...cached.data, fromCache: true },
                    success: true
                });
            } else {
                toFetch.push(symbol);
            }
        }

        // 2. Fetch missing symbols (rate limit aware)
        for (const symbol of toFetch) {
            try {
                const data = await this.getQuote(symbol);
                results.push({ symbol, data, success: true });
            } catch (error) {
                console.error(`[ApiManager] Batch fetch failed for ${symbol}:`, error);
                results.push({ symbol, error: error.message, success: false });
            }
        }

        const cacheHitRate = ((symbols.length - toFetch.length) / symbols.length * 100).toFixed(1);
        console.log(`[ApiManager] Batch complete: ${cacheHitRate}% cache hit rate`);

        return results;
    }

    /**
     * Clear all caches
     * @param {string} storeName - Specific store to clear (optional)
     * @returns {Promise<void>}
     */
    async clearCache(storeName = null) {
        if (storeName) {
            const stores = ['quotes', 'historical', 'fundamentals'];
            if (stores.includes(storeName)) {
                await this.cache.clear(storeName);
                console.log(`[ApiManager] Cleared ${storeName} cache`);
            }
        } else {
            await this.cache.clear('quotes');
            await this.cache.clear('historical');
            await this.cache.clear('fundamentals');
            console.log('[ApiManager] All caches cleared');
        }
    }

    /**
     * Get cache statistics
     * @returns {Promise<Object>} Cache stats
     */
    async getCacheStats() {
        const stats = await this.cache.getStats();
        const rateLimits = await this.rateLimiter.getStats();

        return {
            cache: stats,
            rateLimits: rateLimits,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Get API usage report
     * @returns {Promise<Object>} Usage report
     */
    async getUsageReport() {
        const stats = await this.getCacheStats();
        const report = {
            cache: {
                quotes: stats.cache.quotes || 0,
                historical: stats.cache.historical || 0,
                fundamentals: stats.cache.fundamentals || 0,
                total: (stats.cache.quotes || 0) + (stats.cache.historical || 0) + (stats.cache.fundamentals || 0)
            },
            apiCalls: {}
        };

        for (const [provider, data] of Object.entries(stats.rateLimits)) {
            report.apiCalls[provider] = {
                used: data.total,
                limit: data.limit,
                remaining: data.remaining,
                utilization: `${data.utilizationPercent}%`
            };
        }

        return report;
    }

    /**
     * Get stale cache (ignoring TTL) - private method
     * @param {string} storeName - Store name
     * @param {string} key - Cache key
     * @returns {Promise<Object|null>}
     */
    async _getStaleCache(storeName, key) {
        if (!this.cache || !this.cache.db) return null;

        return new Promise((resolve) => {
            const transaction = this.cache.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => {
                resolve(request.result || null);
            };

            request.onerror = () => {
                resolve(null);
            };
        });
    }

    /**
     * Start automatic cleanup job - private method
     */
    _startCleanupJob() {
        // Initial cleanup
        setTimeout(() => {
            this._runCleanup();
        }, 60000); // 1 minute after init

        // Periodic cleanup (every hour)
        setInterval(() => {
            this._runCleanup();
        }, 60 * 60 * 1000);

        console.log('[ApiManager] Cleanup job scheduled');
    }

    /**
     * Run cleanup tasks - private method
     */
    async _runCleanup() {
        try {
            console.log('[ApiManager] Running cleanup...');

            // Clear expired cache entries
            const quotesCleared = await this.cache.clearExpired('quotes');
            const historicalCleared = await this.cache.clearExpired('historical');

            // Clean old API tracker records
            const trackerCleared = await this.rateLimiter.cleanupOldRecords();

            console.log(`[ApiManager] Cleanup complete: ${quotesCleared + historicalCleared} cache entries, ${trackerCleared} tracker records`);
        } catch (error) {
            console.error('[ApiManager] Cleanup error:', error);
        }
    }

    /**
     * Prefetch data for symbols (background caching)
     * @param {Array<string>} symbols - Symbols to prefetch
     * @returns {Promise<void>}
     */
    async prefetch(symbols) {
        console.log(`[ApiManager] Prefetching ${symbols.length} symbols in background`);

        // Use setTimeout to avoid blocking
        setTimeout(async () => {
            for (const symbol of symbols) {
                try {
                    await this.getQuote(symbol);
                    await new Promise(resolve => setTimeout(resolve, 100)); // Throttle
                } catch (error) {
                    console.warn(`[ApiManager] Prefetch failed for ${symbol}`);
                }
            }
            console.log('[ApiManager] Prefetch complete');
        }, 1000);
    }
}

export default ApiManager;
