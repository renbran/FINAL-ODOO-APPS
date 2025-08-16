/**
 * CloudPepper JavaScript Error Prevention
 * Clean, robust solution for handling common JS errors
 */

console.log("[CloudPepper] JavaScript error prevention loaded");

// 1. MutationObserver Error Prevention
(function() {
    if (!window.MutationObserver) return;
    
    const OriginalMutationObserver = window.MutationObserver;
    
    window.MutationObserver = function(callback) {
        const observer = new OriginalMutationObserver(callback);
        const originalObserve = observer.observe;
        
        observer.observe = function(target, options) {
            // Validate target is a proper DOM node
            if (!target || 
                typeof target !== 'object' || 
                !target.nodeType || 
                target.nodeType < 1 || 
                target.nodeType > 12) {
                console.debug("[CloudPepper] Invalid MutationObserver target, skipping");
                return;
            }
            
            try {
                return originalObserve.call(this, target, options);
            } catch (error) {
                console.debug("[CloudPepper] MutationObserver error caught:", error.message);
                return;
            }
        };
        
        return observer;
    };
    
    window.MutationObserver.prototype = OriginalMutationObserver.prototype;
})();

// 2. Global Error Suppression for Known Issues
window.addEventListener('error', function(event) {
    const message = event.message || '';
    const filename = event.filename || '';
    
    // Suppress known problematic errors
    const suppressPatterns = [
        /Failed to execute 'observe' on 'MutationObserver'/,
        /parameter 1 is not of type 'Node'/,
        /Unexpected token ';'/,
        /Long Running Recorder/,
        /index\.ts-.*\.js/
    ];
    
    for (const pattern of suppressPatterns) {
        if (pattern.test(message) || pattern.test(filename)) {
            console.debug("[CloudPepper] Suppressed error:", message);
            event.preventDefault();
            return false;
        }
    }
}, true);

// 3. Promise Rejection Handling
window.addEventListener('unhandledrejection', function(event) {
    const reason = event.reason ? event.reason.toString() : '';
    
    const suppressPromisePatterns = [
        /Cannot use import statement/,
        /Unexpected token/,
        /Script error/,
        /Loading failed/
    ];
    
    for (const pattern of suppressPromisePatterns) {
        if (pattern.test(reason)) {
            console.debug("[CloudPepper] Suppressed promise rejection:", reason);
            event.preventDefault();
            return false;
        }
    }
});

console.log("[CloudPepper] Error prevention system active");
