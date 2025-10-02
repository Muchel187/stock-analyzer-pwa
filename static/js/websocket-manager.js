/**
 * WebSocketManager - Real-time stock price updates via Twelve Data WebSocket
 *
 * Features:
 * - Automatic connection management with reconnection logic
 * - Subscribe/unsubscribe to stock tickers for real-time updates
 * - Event-driven price updates via callback
 * - Connection state management
 *
 * Usage:
 *   const wsManager = new WebSocketManager();
 *   await wsManager.connect();
 *   wsManager.onPriceUpdate = (data) => { console.log(data); };
 *   wsManager.subscribe(['AAPL', 'GOOGL', 'MSFT']);
 */

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.apiKey = null;
        this.subscriptions = new Set(); // Track currently subscribed tickers
        this.onPriceUpdate = null; // Callback for price updates
        this.onConnectionChange = null; // Callback for connection status changes
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 5000; // 5 seconds
        this.isConnecting = false;
        this.isConnected = false;
    }

    /**
     * Establish WebSocket connection to Twelve Data
     * Fetches API key from backend and opens WebSocket connection
     */
    async connect() {
        if (this.isConnecting) {
            console.log('[WS] Connection already in progress...');
            return;
        }

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log('[WS] WebSocket is already connected.');
            this.isConnected = true;
            return;
        }

        this.isConnecting = true;
        this._notifyConnectionChange('connecting');

        try {
            // Fetch API key from backend (requires authentication)
            console.log('[WS] Fetching WebSocket API key from backend...');
            const response = await api.request('/config/ws-key');
            this.apiKey = response.apiKey;

            console.log('[WS] API key received, establishing WebSocket connection...');

            // Twelve Data WebSocket URL for real-time quotes
            const wsUrl = `wss://ws.twelvedata.com/v1/quotes/price?apikey=${this.apiKey}`;
            this.socket = new WebSocket(wsUrl);

            // WebSocket event handlers
            this.socket.onopen = () => {
                console.log('[WS] ✅ WebSocket connection established successfully.');
                this.isConnected = true;
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this._notifyConnectionChange('connected');

                // Resubscribe to all previously subscribed tickers
                this.resubscribe();
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[WS] Received message:', data);

                    // Handle different message types
                    if (data.event === 'price' && this.onPriceUpdate) {
                        // Price update event
                        this.onPriceUpdate({
                            symbol: data.symbol,
                            price: parseFloat(data.price),
                            timestamp: data.timestamp || Date.now()
                        });
                    } else if (data.event === 'subscribe-status') {
                        // Subscription confirmation
                        console.log(`[WS] Subscription status: ${data.status} for ${data.symbol}`);
                    } else if (data.event === 'heartbeat') {
                        // Heartbeat to keep connection alive
                        console.log('[WS] ❤️ Heartbeat received');
                    }
                } catch (error) {
                    console.error('[WS] Error parsing WebSocket message:', error);
                }
            };

            this.socket.onclose = (event) => {
                console.log(`[WS] WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}`);
                this.isConnected = false;
                this.isConnecting = false;
                this._notifyConnectionChange('disconnected');

                // Attempt to reconnect if not manually closed
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`[WS] Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay / 1000}s...`);
                    setTimeout(() => this.connect(), this.reconnectDelay);
                } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                    console.error('[WS] ❌ Max reconnection attempts reached. Please refresh the page.');
                    this._notifyConnectionChange('failed');
                }
            };

            this.socket.onerror = (error) => {
                console.error('[WS] WebSocket error:', error);
                this.isConnected = false;
                this._notifyConnectionChange('error');
            };

        } catch (error) {
            console.error('[WS] Could not establish WebSocket connection:', error);
            this.isConnecting = false;
            this.isConnected = false;
            this._notifyConnectionChange('error');

            // Retry connection after delay
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`[WS] Retrying connection in ${this.reconnectDelay / 1000}s...`);
                setTimeout(() => this.connect(), this.reconnectDelay);
            }
        }
    }

    /**
     * Subscribe to real-time price updates for given tickers
     * @param {Array<string>} tickers - Array of stock ticker symbols
     */
    subscribe(tickers) {
        if (!Array.isArray(tickers) || tickers.length === 0) {
            console.warn('[WS] No tickers provided for subscription');
            return;
        }

        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.warn('[WS] Cannot subscribe, socket is not open. Saving for later...');
            // Add to subscriptions set for resubscription when connected
            tickers.forEach(ticker => this.subscriptions.add(ticker.toUpperCase()));
            return;
        }

        // Add to subscriptions set
        tickers.forEach(ticker => this.subscriptions.add(ticker.toUpperCase()));

        // Send subscription message to WebSocket server
        const message = {
            action: 'subscribe',
            params: {
                symbols: tickers.join(',')
            }
        };

        this.socket.send(JSON.stringify(message));
        console.log(`[WS] 📊 Subscribed to: ${tickers.join(', ')}`);
    }

    /**
     * Unsubscribe from real-time price updates for given tickers
     * @param {Array<string>} tickers - Array of stock ticker symbols
     */
    unsubscribe(tickers) {
        if (!Array.isArray(tickers) || tickers.length === 0) {
            console.warn('[WS] No tickers provided for unsubscription');
            return;
        }

        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.warn('[WS] Cannot unsubscribe, socket is not open.');
            // Remove from subscriptions set anyway
            tickers.forEach(ticker => this.subscriptions.delete(ticker.toUpperCase()));
            return;
        }

        // Remove from subscriptions set
        tickers.forEach(ticker => this.subscriptions.delete(ticker.toUpperCase()));

        // Send unsubscription message to WebSocket server
        const message = {
            action: 'unsubscribe',
            params: {
                symbols: tickers.join(',')
            }
        };

        this.socket.send(JSON.stringify(message));
        console.log(`[WS] 🚫 Unsubscribed from: ${tickers.join(', ')}`);
    }

    /**
     * Resubscribe to all previously subscribed tickers
     * Called after reconnection
     */
    resubscribe() {
        if (this.subscriptions.size > 0) {
            console.log(`[WS] Resubscribing to ${this.subscriptions.size} tickers...`);
            this.subscribe(Array.from(this.subscriptions));
        }
    }

    /**
     * Manually close the WebSocket connection
     */
    disconnect() {
        if (this.socket) {
            console.log('[WS] Manually disconnecting WebSocket...');
            this.socket.close(1000, 'Manual disconnect');
            this.socket = null;
            this.isConnected = false;
            this.subscriptions.clear();
            this._notifyConnectionChange('disconnected');
        }
    }

    /**
     * Get current connection status
     * @returns {string} 'connected', 'connecting', 'disconnected', or 'error'
     */
    getConnectionStatus() {
        if (this.isConnected && this.socket && this.socket.readyState === WebSocket.OPEN) {
            return 'connected';
        } else if (this.isConnecting) {
            return 'connecting';
        } else if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
            return 'connecting';
        } else {
            return 'disconnected';
        }
    }

    /**
     * Get list of currently subscribed tickers
     * @returns {Array<string>}
     */
    getSubscribedTickers() {
        return Array.from(this.subscriptions);
    }

    /**
     * Notify listeners about connection status changes
     * @private
     */
    _notifyConnectionChange(status) {
        if (this.onConnectionChange) {
            this.onConnectionChange(status);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
}
