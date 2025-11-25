/** @odoo-module **/

import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";

import { Dialog } from "@web/core/dialog/dialog";

// OSUS Properties: Enhanced Dialog with size preferences and CloudPepper protection
patch(Dialog.prototype, {
    setup() {
        try {
            super.setup();
            
            // Initialize data object if not exists (CloudPepper compatibility)
            if (!this.data) {
                this.data = {};
            }
            
            // Set dialog size based on user preferences
            const userDialogSize = session.dialog_size || "minimize";
            this.data.size = userDialogSize !== "maximize" ? (this.props.size || "lg") : "fs";
            this.data.initialSize = this.props?.size || "lg";
        } catch (error) {
            console.error('OSUS Dialog: Setup error', error);
            // Fallback to default size
            if (!this.data) {
                this.data = {};
            }
            this.data.size = this.props?.size || "lg";
            this.data.initialSize = "lg";
        }
    }
});

