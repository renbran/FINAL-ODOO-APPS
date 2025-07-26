/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.companyService = useService("company");
        this._replaceBranding();
    },

    async _replaceBranding() {
        try {
            const company = this.companyService.currentCompany;
            if (company?.replace_odoo_branding && company?.white_label_name) {
                // Replace document title
                this._updateDocumentTitle(company.white_label_name);
                
                // Replace any text content with performance optimization
                this._replaceTextContent(company.white_label_name);
                
                // Set up mutation observer for dynamic content
                this._setupMutationObserver(company.white_label_name);
            }
        } catch (error) {
            console.warn('White label branding error:', error);
        }
    },

    _updateDocumentTitle(whiteLabelName) {
        if (document.title.includes('Odoo')) {
            document.title = document.title.replace(/Odoo/g, whiteLabelName);
        }
    },

    _setupMutationObserver(whiteLabelName) {
        // Use MutationObserver for better performance
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this._processNodes(mutation.addedNodes, whiteLabelName);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    _replaceTextContent(whiteLabelName) {
        this._processNodes([document.body], whiteLabelName);
    },

    _processNodes(nodes, whiteLabelName) {
        if (!nodes.length) return;
        
        const walker = document.createTreeWalker(
            nodes[0] || document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: (node) => {
                    return node.textContent.includes('Odoo') && 
                           !node.parentElement.closest('script, style, .o_debug') ?
                           NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                }
            },
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        textNodes.forEach(textNode => {
            if (textNode.textContent.includes('Powered by Odoo')) {
                textNode.textContent = textNode.textContent.replace(
                    /Powered by Odoo/g, 
                    `Powered by ${whiteLabelName}`
                );
            } else {
                textNode.textContent = textNode.textContent.replace(/\bOdoo\b/g, whiteLabelName);
            }
        });
    }
});