/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

// Settings page cleanup - remove rogue toggle buttons
onMounted(() => {
    // Remove any empty or "Toggle Dropdown" buttons from settings page
    const removeRogueButtons = () => {
        const settingsForm = document.querySelector('.o_form_view.o_xxl_form_view');
        if (settingsForm) {
            // Find all buttons that might be problematic
            const buttons = settingsForm.querySelectorAll('button');
            buttons.forEach(button => {
                const text = button.textContent.trim();
                const hasNoName = !button.getAttribute('name');
                const hasNoClass = !button.className || button.className === 'btn' || button.className === 'btn-secondary';
                
                // Remove if it's an empty button or says "Toggle Dropdown"
                if ((text === '' || text === 'Toggle Dropdown') && hasNoName && hasNoClass) {
                    console.log('Removing rogue button:', button);
                    button.style.display = 'none';
                    button.remove();
                }
            });
        }
    };

    // Run immediately
    removeRogueButtons();
    
    // Run again after a short delay to catch dynamically loaded content
    setTimeout(removeRogueButtons, 500);
    setTimeout(removeRogueButtons, 1000);
    setTimeout(removeRogueButtons, 2000);
    
    // Also run on any DOM mutations
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                removeRogueButtons();
            }
        });
    });
    
    const settingsContainer = document.querySelector('.o_content');
    if (settingsContainer) {
        observer.observe(settingsContainer, {
            childList: true,
            subtree: true
        });
    }
});

console.log('OSUS Settings Fixes loaded - removing rogue toggle buttons');
