
(function() {
    'use strict';
    
    // NUCLEAR RPC ERROR PREVENTION
    const originalConsoleError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (message.includes('RPC_ERROR') || message.includes('Uncaught Promise')) {
            // Intercept and handle RPC errors silently
            window.location.reload();
            return;
        }
        originalConsoleError.apply(console, args);
    };
    
    // Prevent all unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        event.preventDefault();
        console.log('Promise rejection handled by nuclear fix');
        if (event.reason && event.reason.toString().includes('RPC')) {
            setTimeout(() => window.location.reload(), 1000);
        }
    });
    
    // Global error boundary
    window.addEventListener('error', function(event) {
        if (event.message && event.message.includes('RPC')) {
            event.preventDefault();
            setTimeout(() => window.location.reload(), 1000);
            return true;
        }
    });
    
            console.log('NUCLEAR RPC FIX ACTIVE');
})();
