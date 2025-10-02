/**
 * Cache Duration Configuration for Stock Analyzer PWA
 * Defines TTL (Time To Live) for different types of cached data
 *
 * Strategy:
 * - Real-time data: Short TTL (5 minutes)
 * - Intraday data: Medium TTL (15 minutes - 1 hour)
 * - Daily data: Long TTL (24 hours)
 * - Static data: Very long TTL (7 days)
 *
 * All durations in milliseconds
 */

const CACHE_DURATION = {
    // Stock Quotes
    QUOTE_REALTIME: 5 * 60 * 1000,        // 5 minutes - for real-time trading
    QUOTE_STANDARD: 15 * 60 * 1000,       // 15 minutes - for watchlist/portfolio
    QUOTE_EXTENDED: 60 * 60 * 1000,       // 1 hour - for non-critical displays

    // Fundamental Data
    FUNDAMENTALS: 24 * 60 * 60 * 1000,    // 24 hours - changes infrequently
    COMPANY_PROFILE: 7 * 24 * 60 * 60 * 1000,  // 7 days - rarely changes

    // Historical Data
    HISTORICAL_INTRADAY: 60 * 60 * 1000,       // 1 hour - intraday updates
    HISTORICAL_DAY: 24 * 60 * 60 * 1000,       // 24 hours - daily close data
    HISTORICAL_WEEK: 7 * 24 * 60 * 60 * 1000,  // 7 days - weekly data

    // Technical Indicators
    TECHNICAL: 15 * 60 * 1000,            // 15 minutes - recalculate frequently

    // News & Sentiment
    NEWS: 30 * 60 * 1000,                 // 30 minutes - news updates
    SENTIMENT: 60 * 60 * 1000,            // 1 hour - sentiment aggregation

    // AI Analysis
    AI_ANALYSIS: 6 * 60 * 60 * 1000,      // 6 hours - AI recommendations
    AI_RECOMMENDATIONS: 12 * 60 * 60 * 1000,  // 12 hours - top picks

    // Search & Metadata
    SEARCH_RESULTS: 60 * 60 * 1000,       // 1 hour - search cache
    TICKER_LIST: 24 * 60 * 60 * 1000,     // 24 hours - available tickers

    // API Call Tracking
    API_TRACKER_RETENTION: 24 * 60 * 60 * 1000,  // 24 hours - tracking data
};

/**
 * Cache key generators
 * Consistent key generation for cache storage
 */
const CACHE_KEYS = {
    quote: (ticker) => ticker.toUpperCase(),
    historical: (ticker, period) => `${ticker.toUpperCase()}_${period}`,
    fundamentals: (ticker) => `${ticker.toUpperCase()}_fund`,
    technical: (ticker) => `${ticker.toUpperCase()}_tech`,
    aiAnalysis: (ticker) => `${ticker.toUpperCase()}_ai`,
    news: (ticker) => `${ticker.toUpperCase()}_news`,
    search: (query) => `search_${query.toLowerCase()}`,
};

/**
 * Cache priority levels
 * Determines which caches to clear first when storage is full
 */
const CACHE_PRIORITY = {
    HIGH: 1,      // Keep longest (company profile, fundamentals)
    MEDIUM: 2,    // Keep medium (historical data, quotes)
    LOW: 3,       // Clear first (search results, news)
};

/**
 * Storage quota management
 * IndexedDB quotas vary by browser
 */
const STORAGE_CONFIG = {
    // Estimated storage limits (in MB)
    QUOTA_WARNING_THRESHOLD: 50,   // Warn when 50MB used
    QUOTA_CLEANUP_THRESHOLD: 80,    // Auto-cleanup when 80MB used
    MAX_ENTRIES_PER_STORE: 1000,    // Max items per object store

    // Cleanup strategy
    CLEANUP_BATCH_SIZE: 100,        // Delete this many expired items at once
    CLEANUP_INTERVAL: 60 * 60 * 1000,  // Run cleanup every hour
};

/**
 * Get TTL for a specific cache type
 * @param {string} cacheType - Type of cache (quote, historical, fundamentals, etc.)
 * @param {string} variant - Variant (realtime, standard, extended)
 * @returns {number} TTL in milliseconds
 */
function getCacheTTL(cacheType, variant = 'standard') {
    const key = `${cacheType.toUpperCase()}_${variant.toUpperCase()}`;
    return CACHE_DURATION[key] || CACHE_DURATION.QUOTE_STANDARD;
}

/**
 * Calculate expiration timestamp
 * @param {number} ttl - TTL in milliseconds
 * @returns {number} Unix timestamp when cache expires
 */
function getExpirationTime(ttl) {
    return Date.now() + ttl;
}

/**
 * Check if cache entry is expired
 * @param {number} expirationTime - Expiration timestamp
 * @returns {boolean} True if expired
 */
function isExpired(expirationTime) {
    return expirationTime < Date.now();
}

/**
 * Format cache duration for display
 * @param {number} duration - Duration in milliseconds
 * @returns {string} Formatted duration (e.g., "15 minutes", "2 hours", "1 day")
 */
function formatDuration(duration) {
    const seconds = duration / 1000;
    const minutes = seconds / 60;
    const hours = minutes / 60;
    const days = hours / 24;

    if (days >= 1) return `${Math.round(days)} day${days > 1 ? 's' : ''}`;
    if (hours >= 1) return `${Math.round(hours)} hour${hours > 1 ? 's' : ''}`;
    if (minutes >= 1) return `${Math.round(minutes)} minute${minutes > 1 ? 's' : ''}`;
    return `${Math.round(seconds)} second${seconds > 1 ? 's' : ''}`;
}

/**
 * Get cache configuration for a specific use case
 * @param {string} useCase - Use case (trading, portfolio, analysis, etc.)
 * @returns {Object} Cache configuration
 */
function getCacheConfig(useCase) {
    const configs = {
        trading: {
            quote: CACHE_DURATION.QUOTE_REALTIME,
            technical: CACHE_DURATION.TECHNICAL,
            news: CACHE_DURATION.NEWS,
        },
        portfolio: {
            quote: CACHE_DURATION.QUOTE_STANDARD,
            fundamentals: CACHE_DURATION.FUNDAMENTALS,
            historical: CACHE_DURATION.HISTORICAL_DAY,
        },
        analysis: {
            quote: CACHE_DURATION.QUOTE_EXTENDED,
            fundamentals: CACHE_DURATION.FUNDAMENTALS,
            technical: CACHE_DURATION.TECHNICAL,
            aiAnalysis: CACHE_DURATION.AI_ANALYSIS,
        },
        watchlist: {
            quote: CACHE_DURATION.QUOTE_STANDARD,
            technical: CACHE_DURATION.TECHNICAL,
        },
    };

    return configs[useCase] || configs.portfolio;
}

// Export all cache configuration
export {
    CACHE_DURATION,
    CACHE_KEYS,
    CACHE_PRIORITY,
    STORAGE_CONFIG,
    getCacheTTL,
    getExpirationTime,
    isExpired,
    formatDuration,
    getCacheConfig,
};

export default CACHE_DURATION;
