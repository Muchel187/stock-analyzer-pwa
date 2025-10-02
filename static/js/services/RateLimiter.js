/**
 * Rate Limiter for API Call Tracking
 * Prevents exceeding API rate limits by tracking and limiting requests
 *
 * Uses IndexedDB to store API call history
 * Implements sliding window algorithm for rate limiting
 *
 * @class RateLimiter
 */
class RateLimiter {
    constructor(cacheManager) {
        this.cache = cacheManager;

        // Rate limit configurations
        this.limits = {
            'stock_api': {
                max: 100,                    // 100 calls per window
                window: 60 * 60 * 1000      // 1 hour window
            },
            'ai_api': {
                max: 20,                     // 20 calls per window
                window: 60 * 60 * 1000      // 1 hour window
            },
            'news_api': {
                max: 50,                     // 50 calls per window
                window: 60 * 60 * 1000      // 1 hour window
            },
            'search_api': {
                max: 200,                    // 200 calls per window
                window: 60 * 60 * 1000      // 1 hour window
            }
        };
    }

    /**
     * Check if a request is allowed under rate limit
     * @param {string} provider - API provider name
     * @returns {Promise<boolean>} True if request is allowed
     */
    async checkLimit(provider) {
        const limit = this.limits[provider];
        if (!limit) {
            console.log(`[RateLimiter] No limit defined for ${provider}, allowing request`);
            return true;
        }

        const now = Date.now();
        const windowStart = now - limit.window;

        // Count calls in current window
        const calls = await this._getCallsInWindow(provider, windowStart);

        const allowed = calls.length < limit.max;
        const remaining = limit.max - calls.length;

        console.log(`[RateLimiter] ${provider}: ${calls.length}/${limit.max} calls in window (${remaining} remaining)`);

        if (!allowed) {
            console.warn(`[RateLimiter] Rate limit exceeded for ${provider}!`);
        }

        return allowed;
    }

    /**
     * Record an API call
     * @param {string} provider - API provider name
     * @param {Object} metadata - Additional metadata about the call
     * @returns {Promise<void>}
     */
    async recordCall(provider, metadata = {}) {
        const record = {
            provider: provider,
            timestamp: Date.now(),
            date: new Date().toISOString(),
            ...metadata
        };

        try {
            await this.cache.set('apiTracker', record);
            console.log(`[RateLimiter] Recorded API call for ${provider}`);
        } catch (error) {
            console.error(`[RateLimiter] Failed to record call for ${provider}:`, error);
        }
    }

    /**
     * Get remaining calls for a provider
     * @param {string} provider - API provider name
     * @returns {Promise<number>} Number of remaining calls
     */
    async getRemainingCalls(provider) {
        const limit = this.limits[provider];
        if (!limit) return Infinity;

        const now = Date.now();
        const windowStart = now - limit.window;

        const calls = await this._getCallsInWindow(provider, windowStart);
        const remaining = Math.max(0, limit.max - calls.length);

        return remaining;
    }

    /**
     * Get time until rate limit resets
     * @param {string} provider - API provider name
     * @returns {Promise<number>} Milliseconds until reset
     */
    async getTimeUntilReset(provider) {
        const limit = this.limits[provider];
        if (!limit) return 0;

        const now = Date.now();
        const windowStart = now - limit.window;

        const calls = await this._getCallsInWindow(provider, windowStart);

        if (calls.length === 0) return 0;

        // Find oldest call in window
        const oldestCall = calls.reduce((oldest, call) =>
            call.timestamp < oldest.timestamp ? call : oldest
        );

        const resetTime = oldestCall.timestamp + limit.window;
        return Math.max(0, resetTime - now);
    }

    /**
     * Get API call statistics
     * @param {string} provider - API provider name (optional)
     * @returns {Promise<Object>} Statistics
     */
    async getStats(provider = null) {
        if (provider) {
            const limit = this.limits[provider];
            if (!limit) return null;

            const now = Date.now();
            const windowStart = now - limit.window;
            const calls = await this._getCallsInWindow(provider, windowStart);

            return {
                provider: provider,
                total: calls.length,
                limit: limit.max,
                remaining: Math.max(0, limit.max - calls.length),
                windowMs: limit.window,
                resetIn: await this.getTimeUntilReset(provider),
                utilizationPercent: (calls.length / limit.max * 100).toFixed(1)
            };
        } else {
            // Get stats for all providers
            const stats = {};
            for (const prov of Object.keys(this.limits)) {
                stats[prov] = await this.getStats(prov);
            }
            return stats;
        }
    }

    /**
     * Clean up old API call records
     * Deletes records older than 24 hours
     * @returns {Promise<number>} Number of records deleted
     */
    async cleanupOldRecords() {
        const cutoff = Date.now() - (24 * 60 * 60 * 1000); // 24 hours ago

        try {
            if (!this.cache || !this.cache.db) {
                console.warn('[RateLimiter] Cache not initialized');
                return 0;
            }

            return new Promise((resolve, reject) => {
                const transaction = this.cache.db.transaction(['apiTracker'], 'readwrite');
                const store = transaction.objectStore('apiTracker');
                const request = store.openCursor();

                let deletedCount = 0;

                request.onsuccess = (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        if (cursor.value.timestamp < cutoff) {
                            cursor.delete();
                            deletedCount++;
                        }
                        cursor.continue();
                    } else {
                        console.log(`[RateLimiter] Cleaned up ${deletedCount} old API call records`);
                        resolve(deletedCount);
                    }
                };

                request.onerror = () => {
                    console.error('[RateLimiter] Error cleaning up records:', request.error);
                    reject(request.error);
                };
            });
        } catch (error) {
            console.error('[RateLimiter] Cleanup error:', error);
            return 0;
        }
    }

    /**
     * Get calls within a time window (private method)
     * @param {string} provider - API provider name
     * @param {number} windowStart - Start of time window (timestamp)
     * @returns {Promise<Array>} Array of API calls
     */
    async _getCallsInWindow(provider, windowStart) {
        if (!this.cache || !this.cache.db) {
            console.warn('[RateLimiter] Cache not initialized');
            return [];
        }

        return new Promise((resolve, reject) => {
            const transaction = this.cache.db.transaction(['apiTracker'], 'readonly');
            const store = transaction.objectStore('apiTracker');
            const index = store.index('provider');
            const range = IDBKeyRange.only(provider);
            const request = index.openCursor(range);

            const results = [];

            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    if (cursor.value.timestamp >= windowStart) {
                        results.push(cursor.value);
                    }
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };

            request.onerror = () => {
                console.error(`[RateLimiter] Error getting calls for ${provider}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Format time duration for display
     * @param {number} ms - Milliseconds
     * @returns {string} Formatted duration
     */
    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    /**
     * Check if provider is rate limited
     * @param {string} provider - API provider name
     * @returns {Promise<boolean>} True if rate limited
     */
    async isRateLimited(provider) {
        const allowed = await this.checkLimit(provider);
        return !allowed;
    }

    /**
     * Get warning level for rate limit usage
     * @param {string} provider - API provider name
     * @returns {Promise<string>} 'safe', 'warning', or 'critical'
     */
    async getWarningLevel(provider) {
        const stats = await this.getStats(provider);
        if (!stats) return 'safe';

        const utilization = parseFloat(stats.utilizationPercent);

        if (utilization >= 90) return 'critical';
        if (utilization >= 75) return 'warning';
        return 'safe';
    }
}

export default RateLimiter;
