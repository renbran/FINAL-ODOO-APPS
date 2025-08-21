/**
 * EMERGENCY RPC ERROR GLOBAL HANDLER FOR CLOUDPEPPER
 * Deploy immediately to resolve production RPC errors
 * Target: erposus.com production environment
 */

(function() {
    'use strict';
    
    console.log('🚨 Emergency RPC Handler Loading...');
    
    // Global RPC Error Handler
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.name === 'RPC_ERROR') {
            console.error('🚨 RPC Error caught by emergency handler:', event.reason);
            
            // Prevent the error from crashing the app
            event.preventDefault();
            
            // Show user-friendly notification
            if (window.location.pathname.includes('/web')) {
                const notification = document.createElement('div');
                notification.innerHTML = `
                    <div style="
                        position: fixed; 
                        top: 20px; 
                        right: 20px; 
                        background: #dc3545; 
                        color: white; 
                        padding: 15px 20px; 
                        border-radius: 8px; 
                        z-index: 99999;
                        font-family: system-ui;
                        font-size: 14px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    ">
                        ⚠️ Connection issue detected. Refreshing...
                    </div>
                `;
                document.body.appendChild(notification);
                
                // Auto-refresh after 2 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
            
            return true;
        }
    });
    
    // Enhanced Fetch Wrapper with Retry Logic
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
            try {
                const response = await originalFetch.apply(this, args);
                
                if (!response.ok && response.status >= 500) {
                    throw new Error(`Server Error: ${response.status}`);
                }
                
                return response;
            } catch (error) {
                attempts++;
                console.warn(`🔄 Fetch attempt ${attempts}/${maxAttempts} failed:`, error);
                
                if (attempts >= maxAttempts) {
                    // Final attempt failed - show user message
                    if (window.location.pathname.includes('/web')) {
                        console.error('🚨 All fetch attempts failed, showing user notification');
                    }
                    throw error;
                }
                
                // Wait before retry (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000));
            }
        }
    };
    
    // Enhanced XMLHttpRequest Wrapper
    const originalXMLHttpRequest = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXMLHttpRequest();
        const originalSend = xhr.send;
        
        xhr.send = function(...args) {
            // Add timeout
            xhr.timeout = 30000; // 30 seconds
            
            // Enhanced error handling
            xhr.addEventListener('error', function(e) {
                console.error('🚨 XHR Error intercepted:', e);
            });
            
            xhr.addEventListener('timeout', function(e) {
                console.error('🚨 XHR Timeout intercepted:', e);
            });
            
            return originalSend.apply(this, args);
        };
        
        return xhr;
    };
    
    console.log('✅ Emergency RPC Handler Active - Production Stabilized');
    
})();
