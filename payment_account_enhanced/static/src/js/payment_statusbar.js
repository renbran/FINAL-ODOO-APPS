/** @odoo-module **/

import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Enhanced Payment Statusbar Component for Responsive Behavior
 */
export class PaymentStatusbar extends Component {
    static template = "payment_account_enhanced.PaymentStatusbar";
    
    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        
        onMounted(() => {
            this.initializeResponsiveStatusbar();
            this.addResizeListener();
        });
        
        onWillUnmount(() => {
            this.removeResizeListener();
        });
    }
    
    initializeResponsiveStatusbar() {
        const statusbar = document.querySelector('.o_payment_statusbar');
        if (statusbar) {
            this.updateStatusbarLayout();
            this.addStatusbarInteractivity();
        }
    }
    
    updateStatusbarLayout() {
        const statusbar = document.querySelector('.o_payment_statusbar');
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
    
    addStatusbarInteractivity() {
        const statusbar = document.querySelector('.o_payment_statusbar');
        if (!statusbar) return;
        
        const statuses = statusbar.querySelectorAll('.o_statusbar_status');
        
        statuses.forEach(status => {
            // Add hover effects
            status.addEventListener('mouseenter', (e) => {
                if (!e.target.classList.contains('o_arrow_button_current')) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(139, 21, 56, 0.3)';
                }
            });
            
            status.addEventListener('mouseleave', (e) => {
                if (!e.target.classList.contains('o_arrow_button_current')) {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                }
            });
            
            // Add click feedback
            status.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                ripple.classList.add('ripple-effect');
                e.target.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
    
    addResizeListener() {
        this.resizeHandler = () => {
            this.updateStatusbarLayout();
        };
        window.addEventListener('resize', this.resizeHandler);
    }
    
    removeResizeListener() {
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }
    }
    
    async onStatusChange(newState) {
        try {
            // Add smooth transition animation
            const statusbar = document.querySelector('.o_payment_statusbar');
            if (statusbar) {
                statusbar.style.opacity = '0.7';
                statusbar.style.transform = 'scale(0.98)';
                
                setTimeout(() => {
                    statusbar.style.opacity = '1';
                    statusbar.style.transform = 'scale(1)';
                }, 200);
            }
            
            // Show success notification
            this.notification.add(
                `Payment status updated to ${newState}`,
                { type: "success" }
            );
        } catch (error) {
            this.notification.add(
                `Failed to update status: ${error.message}`,
                { type: "danger" }
            );
        }
    }
}

/**
 * Initialize the enhanced statusbar when the page loads
 */
function initializeEnhancedStatusbar() {
    const statusbars = document.querySelectorAll('.o_payment_statusbar');
    statusbars.forEach(statusbar => {
        if (!statusbar.dataset.enhanced) {
            const enhancer = new PaymentStatusbar();
            enhancer.initializeResponsiveStatusbar();
            statusbar.dataset.enhanced = 'true';
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedStatusbar);
} else {
    initializeEnhancedStatusbar();
}

// Also initialize on Odoo's view reload
document.addEventListener('o_view_loaded', initializeEnhancedStatusbar);

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
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

// Export for registry if needed
registry.category("components").add("payment_statusbar", PaymentStatusbar);
