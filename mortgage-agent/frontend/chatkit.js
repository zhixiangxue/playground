/**
 * ChatKit SDK - For embedding interactive forms/pages into chat interface
 * Version: 1.0.0
 * 
 * Usage in embedded page:
 * <script src="chatkit.js"></script>
 * <script>
 *   const kit = ChatKit.init({
 *     pageId: 'loan-form-v1',
 *     onReady: () => console.log('Connected to parent')
 *   });
 *   
 *   kit.sendData({ type: 'form_submit', data: {...} });
 *   kit.onCommand('reset', () => form.reset());
 * </script>
 */

(function(window) {
    'use strict';

    const ChatKit = {
        version: '1.0.0',
        _config: null,
        _parentOrigin: null,
        _messageQueue: [],
        _commandHandlers: {},
        _isReady: false,

        /**
         * Initialize SDK
         * @param {Object} config - Configuration object
         * @param {string} config.pageId - Unique identifier for this embedded page
         * @param {function} config.onReady - Callback when connection is established
         * @param {function} config.onError - Error handler
         * @returns {Object} SDK instance
         */
        init: function(config) {
            this._config = config || {};
            this._config.pageId = this._config.pageId || 'embed-' + Date.now();
            
            // Detect parent origin
            this._detectParentOrigin();
            
            // Setup message listener
            window.addEventListener('message', this._handleMessage.bind(this), false);
            
            // Send ready signal
            this._sendToParent({
                type: 'embed_ready',
                pageId: this._config.pageId,
                timestamp: new Date().toISOString()
            });
            
            return this;
        },

        /**
         * Send data to parent chat interface
         * @param {Object} data - Data to send
         * @param {Object} options - Display options
         */
        sendData: function(data, options) {
            const message = {
                type: 'embed_data',
                pageId: this._config.pageId,
                data: data,
                options: options || {},
                timestamp: new Date().toISOString()
            };
            
            if (this._isReady) {
                this._sendToParent(message);
            } else {
                this._messageQueue.push(message);
            }
        },

        /**
         * Send formatted message to chat
         * @param {string} text - Message text
         * @param {string} type - Message type: 'info', 'success', 'error', 'data'
         */
        sendMessage: function(text, type) {
            this.sendData({
                type: 'message',
                messageType: type || 'info',
                content: text
            });
        },

        /**
         * Register command handler from parent
         * @param {string} command - Command name
         * @param {function} handler - Handler function
         */
        onCommand: function(command, handler) {
            this._commandHandlers[command] = handler;
        },

        /**
         * Resize embedded frame
         * @param {number} height - New height in pixels
         */
        resize: function(height) {
            this._sendToParent({
                type: 'embed_resize',
                pageId: this._config.pageId,
                height: height
            });
        },

        /**
         * Auto-resize based on content
         */
        autoResize: function() {
            const height = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight
            );
            this.resize(height);
        },

        /**
         * Close/hide this embed
         */
        close: function() {
            this._sendToParent({
                type: 'embed_close',
                pageId: this._config.pageId
            });
        },

        // Internal methods
        _detectParentOrigin: function() {
            if (window.parent === window) {
                console.warn('[ChatKit] Not running in iframe');
                return;
            }
            
            // Try to detect parent origin from referrer or use wildcard
            this._parentOrigin = document.referrer ? new URL(document.referrer).origin : '*';
        },

        _sendToParent: function(message) {
            if (window.parent === window) return;
            
            try {
                window.parent.postMessage(message, this._parentOrigin);
            } catch (e) {
                console.error('[ChatKit] Failed to send message:', e);
                if (this._config.onError) {
                    this._config.onError(e);
                }
            }
        },

        _handleMessage: function(event) {
            // Validate origin (in production, check against whitelist)
            const message = event.data;
            
            if (!message || typeof message !== 'object') return;
            
            // Handle parent ready signal
            if (message.type === 'parent_ready') {
                this._isReady = true;
                
                // Flush message queue
                while (this._messageQueue.length > 0) {
                    const queued = this._messageQueue.shift();
                    this._sendToParent(queued);
                }
                
                if (this._config.onReady) {
                    this._config.onReady();
                }
            }
            
            // Handle commands from parent
            if (message.type === 'parent_command') {
                const command = message.command;
                const handler = this._commandHandlers[command];
                
                if (handler) {
                    handler(message.params);
                } else {
                    console.warn('[ChatKit] No handler for command:', command);
                }
            }
        }
    };

    // Export
    window.ChatKit = ChatKit;

})(window);
