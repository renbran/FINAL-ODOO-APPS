/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { useService } from '@web/core/utils/hooks';

import { NavBar } from '@web/webclient/navbar/navbar';
import { AppsMenu } from "@muk_web_theme/webclient/appsmenu/appsmenu";

/**
 * OSUS Properties NavBar Customization
 * Patches the standard Odoo NavBar to use custom AppsMenu component
 */

// Add app menu service to navbar prototype
patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.appMenuService = useService('app_menu');
    }
});

// Replace standard apps menu with OSUS custom component
patch(NavBar, {
    components: {
        ...NavBar.components,
        AppsMenu
    }
});
