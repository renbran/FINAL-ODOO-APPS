/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";

import { Chatter } from "@mail/core/web/chatter";

// OSUS Properties: Enhanced Chatter with tracking toggle and CloudPepper protection
patch(Chatter.prototype, {
    setup() {
        try {
            super.setup();
            
            // Load tracking preference from localStorage
            const showTracking = browser.localStorage.getItem("osus_chatter.tracking");
            this.state.showTracking = showTracking != null ? JSON.parse(showTracking) : true;
        } catch (error) {
            console.error('OSUS Chatter: Setup error', error);
            // Fallback to default state
            if (!this.state.showTracking) {
                this.state.showTracking = true;
            }
        }
    },
    
    onClickTrackingToggle() {
        try {
            const showTracking = !this.state.showTracking;
            browser.localStorage.setItem("osus_chatter.tracking", showTracking);
            this.state.showTracking = showTracking;
        } catch (error) {
            console.error('OSUS Chatter: Toggle tracking error', error);
            // Still toggle the state even if localStorage fails
            this.state.showTracking = !this.state.showTracking;
        }
    }
});

