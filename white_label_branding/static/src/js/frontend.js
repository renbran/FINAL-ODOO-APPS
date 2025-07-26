/** @odoo-module **/

// Frontend branding replacement for website/portal
(function() {
    'use strict';

    function initializeFrontendBranding() {
        // Get company info from meta tags or global variables
        const companyName = getCompanyName();
        const shouldReplace = shouldReplaceBranding();
        
        if (shouldReplace && companyName) {
            replaceFrontendBranding(companyName);
            setupMutationObserver(companyName);
        }
    }

    function getCompanyName() {
        // Try to get from meta tag first
        const metaTag = document.querySelector('meta[name="company-name"]');
        if (metaTag) return metaTag.content;
        
        // Fallback to global variable
        if (window.companyInfo && window.companyInfo.white_label_name) {
            return window.companyInfo.white_label_name;
        }
        
        // Default fallback
        return null;
    }

    function shouldReplaceBranding() {
        const metaTag = document.querySelector('meta[name="replace-odoo-branding"]');
        if (metaTag) return metaTag.content === 'true';
        
        if (window.companyInfo) {
            return window.companyInfo.replace_odoo_branding;
        }
        
        return true; // Default to true
    }

    function replaceFrontendBranding(whiteLabelName) {
        // Replace document title
        if (document.title.includes('Odoo')) {
            document.title = document.title.replace(/Odoo/g, whiteLabelName);
        }
        
        // Replace text content in DOM
        replaceTextContent(whiteLabelName);
    }

    function replaceTextContent(whiteLabelName) {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    if (!node.textContent.includes('Odoo')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip script and style elements
                    const parent = node.parentElement;
                    if (parent && (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            },
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        textNodes.forEach(function(textNode) {
            try {
                if (textNode.textContent.includes('Powered by Odoo')) {
                    textNode.textContent = textNode.textContent.replace(
                        /Powered by Odoo/g, 
                        'Powered by ' + whiteLabelName
                    );
                } else {
                    textNode.textContent = textNode.textContent.replace(/\bOdoo\b/g, whiteLabelName);
                }
            } catch (error) {
                console.warn('Error replacing text content:', error);
            }
        });
    }

    function setupMutationObserver(whiteLabelName) {
        if (!window.MutationObserver) return;
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    setTimeout(function() {
                        replaceTextContent(whiteLabelName);
                    }, 100);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFrontendBranding);
    } else {
        initializeFrontendBranding();
    }

})();