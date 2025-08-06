/** @odoo-module **/

// Simple payment statusbar enhancement without OWL dependencies
// This ensures compatibility with Odoo 17 without complex imports

(function() {
    'use strict';

    /**
     * Enhanced Payment Statusbar for Responsive Behavior
     */
    function initializeResponsiveStatusbar() {
        const statusbars = document.querySelectorAll('.o_payment_statusbar');
        statusbars.forEach(statusbar => {
            if (!statusbar.dataset.enhanced) {
                enhanceStatusbar(statusbar);
                statusbar.dataset.enhanced = 'true';
            }
        });
    }

    function enhanceStatusbar(statusbar) {
        updateStatusbarLayout(statusbar);
        addStatusbarInteractivity(statusbar);
        addResizeListener();
    }

    function updateStatusbarLayout(statusbar) {
        if (!statusbar) return;
        
        const isMobile = window.innerWidth <= 768;
        const statuses = statusbar.querySelectorAll('.o_statusbar_status');
        
        statuses.forEach((status, index) => {
            if (isMobile) {
                // Mobile layout
                status.style.width = '100%';
                status.style.marginBottom = '4px';
                status.style.textAlign = 'center';
                status.style.borderRadius = '6px';
            } else {
                // Desktop layout
                status.style.width = 'auto';
                status.style.marginBottom = '0';
                status.style.textAlign = 'left';
            }
        });
    }

    function addStatusbarInteractivity(statusbar) {
        if (!statusbar) return;
        
        const statuses = statusbar.querySelectorAll('.o_statusbar_status');
        
        statuses.forEach(status => {
            // Add hover effects
            status.addEventListener('mouseenter', function(e) {
                if (!e.target.classList.contains('o_arrow_button_current')) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(139, 21, 56, 0.3)';
                }
            });
            
            status.addEventListener('mouseleave', function(e) {
                if (!e.target.classList.contains('o_arrow_button_current')) {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                }
            });
            
            // Add click feedback
            status.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                ripple.classList.add('ripple-effect');
                e.target.appendChild(ripple);
                
                setTimeout(function() {
                    if (ripple.parentNode) {
                        ripple.parentNode.removeChild(ripple);
                    }
                }, 600);
            });
        });
    }

    function addResizeListener() {
        if (window.paymentStatusbarResizeHandler) {
            window.removeEventListener('resize', window.paymentStatusbarResizeHandler);
        }
        
        window.paymentStatusbarResizeHandler = function() {
            const statusbars = document.querySelectorAll('.o_payment_statusbar');
            statusbars.forEach(statusbar => {
                updateStatusbarLayout(statusbar);
            });
        };
        
        window.addEventListener('resize', window.paymentStatusbarResizeHandler);
    }

    // Add CSS for ripple effect
    function addRippleStyles() {
        if (document.getElementById('payment-statusbar-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'payment-statusbar-styles';
        style.textContent = `
            .ripple-effect {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
                width: 30px;
                height: 30px;
                left: 50%;
                top: 50%;
                margin-left: -15px;
                margin-top: -15px;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            .o_statusbar_status {
                position: relative;
                overflow: hidden;
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize when DOM is ready
    function initializeWhenReady() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                addRippleStyles();
                initializeResponsiveStatusbar();
            });
        } else {
            addRippleStyles();
            initializeResponsiveStatusbar();
        }
    }

    // Initialize immediately
    initializeWhenReady();

    // Also initialize on Odoo's view changes
    if (typeof odoo !== 'undefined' && odoo.define) {
        // For Odoo environments, also listen to view changes
        document.addEventListener('DOMNodeInserted', function(e) {
            if (e.target.classList && e.target.classList.contains('o_payment_statusbar')) {
                setTimeout(function() {
                    initializeResponsiveStatusbar();
                }, 100);
            }
        });
    }

})();
