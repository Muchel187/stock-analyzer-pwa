/**
 * IndexedDB Manager for Stock Analyzer PWA
 * Provides client-side caching for stock data, historical prices, fundamentals, and API call tracking
 *
 * Database Schema:
 * - quotes: Stock quote data with TTL
 * - historical: Historical price data
 * - fundamentals: Fundamental analysis data
 * - apiTracker: API call tracking for rate limiting
 *
 * @class IndexedDBManager
 */
class IndexedDBManager {
    constructor() {
        this.dbName = 'StockAnalyzerDB';
        this.version = 1;
        this.db = null;
    }

    /**
     * Initialize IndexedDB database
     * Creates object stores if they don't exist
     * @returns {Promise<IDBDatabase>}
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => {
                console.error('[IndexedDB] Failed to open database:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('[IndexedDB] Database opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                console.log('[IndexedDB] Upgrading database schema...');

                // Store 1: Stock Quotes
                if (!db.objectStoreNames.contains('quotes')) {
                    const quoteStore = db.createObjectStore('quotes', { keyPath: 'symbol' });
                    quoteStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
                    quoteStore.createIndex('ttl', 'ttl', { unique: false });
                    console.log('[IndexedDB] Created quotes store');
                }

                // Store 2: Historical Data
                if (!db.objectStoreNames.contains('historical')) {
                    const histStore = db.createObjectStore('historical', { keyPath: 'id' });
                    histStore.createIndex('symbol', 'symbol', { unique: false });
                    histStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
                    console.log('[IndexedDB] Created historical store');
                }

                // Store 3: Fundamentals
                if (!db.objectStoreNames.contains('fundamentals')) {
                    const fundStore = db.createObjectStore('fundamentals', { keyPath: 'symbol' });
                    fundStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
                    console.log('[IndexedDB] Created fundamentals store');
                }

                // Store 4: API Call Tracker
                if (!db.objectStoreNames.contains('apiTracker')) {
                    const trackerStore = db.createObjectStore('apiTracker', { keyPath: 'id', autoIncrement: true });
                    trackerStore.createIndex('provider', 'provider', { unique: false });
                    trackerStore.createIndex('timestamp', 'timestamp', { unique: false });
                    console.log('[IndexedDB] Created apiTracker store');
                }
            };
        });
    }

    /**
     * Get item from store with TTL check
     * @param {string} storeName - Name of the object store
     * @param {string} key - Key to retrieve
     * @returns {Promise<Object|null>}
     */
    async get(storeName, key) {
        if (!this.db) {
            console.warn('[IndexedDB] Database not initialized');
            return null;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => {
                const data = request.result;

                if (!data) {
                    resolve(null);
                    return;
                }

                // Check TTL if present
                if (data.ttl && data.ttl < Date.now()) {
                    console.log(`[IndexedDB] Cache expired for ${key} in ${storeName}`);
                    resolve(null);
                } else {
                    console.log(`[IndexedDB] Cache HIT for ${key} in ${storeName}`);
                    resolve(data);
                }
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error getting ${key} from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Set item in store
     * @param {string} storeName - Name of the object store
     * @param {Object} data - Data to store (must include key field)
     * @returns {Promise<any>}
     */
    async set(storeName, data) {
        if (!this.db) {
            throw new Error('[IndexedDB] Database not initialized');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);

            request.onsuccess = () => {
                console.log(`[IndexedDB] Stored data in ${storeName}:`, data.symbol || data.id);
                resolve(request.result);
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error storing data in ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Delete item from store
     * @param {string} storeName - Name of the object store
     * @param {string} key - Key to delete
     * @returns {Promise<void>}
     */
    async delete(storeName, key) {
        if (!this.db) {
            throw new Error('[IndexedDB] Database not initialized');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => {
                console.log(`[IndexedDB] Deleted ${key} from ${storeName}`);
                resolve();
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error deleting ${key} from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Clear expired entries from a store
     * @param {string} storeName - Name of the object store
     * @returns {Promise<number>} Number of entries deleted
     */
    async clearExpired(storeName) {
        if (!this.db) {
            console.warn('[IndexedDB] Database not initialized');
            return 0;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);

            // Only clear stores with TTL index
            if (!store.indexNames.contains('ttl')) {
                resolve(0);
                return;
            }

            const index = store.index('ttl');
            const range = IDBKeyRange.upperBound(Date.now());
            const request = index.openCursor(range);

            let deletedCount = 0;

            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    cursor.delete();
                    deletedCount++;
                    cursor.continue();
                } else {
                    console.log(`[IndexedDB] Cleared ${deletedCount} expired entries from ${storeName}`);
                    resolve(deletedCount);
                }
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error clearing expired from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get all items from a store
     * @param {string} storeName - Name of the object store
     * @param {number} limit - Maximum number of items to return
     * @returns {Promise<Array>}
     */
    async getAll(storeName, limit = null) {
        if (!this.db) {
            throw new Error('[IndexedDB] Database not initialized');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = limit ? store.getAll(null, limit) : store.getAll();

            request.onsuccess = () => {
                resolve(request.result || []);
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error getting all from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Clear all data from a store
     * @param {string} storeName - Name of the object store
     * @returns {Promise<void>}
     */
    async clear(storeName) {
        if (!this.db) {
            throw new Error('[IndexedDB] Database not initialized');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => {
                console.log(`[IndexedDB] Cleared all data from ${storeName}`);
                resolve();
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error clearing ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get count of items in a store
     * @param {string} storeName - Name of the object store
     * @returns {Promise<number>}
     */
    async count(storeName) {
        if (!this.db) {
            return 0;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.count();

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                console.error(`[IndexedDB] Error counting ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get cache statistics
     * @returns {Promise<Object>} Statistics for all stores
     */
    async getStats() {
        const stores = ['quotes', 'historical', 'fundamentals', 'apiTracker'];
        const stats = {};

        for (const storeName of stores) {
            try {
                stats[storeName] = await this.count(storeName);
            } catch (error) {
                console.error(`[IndexedDB] Error getting stats for ${storeName}:`, error);
                stats[storeName] = 0;
            }
        }

        return stats;
    }

    /**
     * Close database connection
     */
    close() {
        if (this.db) {
            this.db.close();
            this.db = null;
            console.log('[IndexedDB] Database connection closed');
        }
    }
}

// Export for use in other modules
export default IndexedDBManager;
