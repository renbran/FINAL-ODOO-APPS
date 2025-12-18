/** @odoo-module **/

import { useEffect } from "@odoo/owl";
import { url } from "@web/core/utils/urls";
import { useBus, useService } from "@web/core/utils/hooks";

import { Dropdown } from "@web/core/dropdown/dropdown";

/**
 * OSUS Properties Apps Menu Component
 * Enhanced dropdown menu for applications with keyboard shortcuts
 * and custom background image support
 */
export class AppsMenu extends Dropdown {
    static template = 'muk_web_theme.AppsMenu';
    static props = {
        ...Dropdown.props
    };
    
    setup() {
        super.setup();
        this.commandPaletteOpen = false;
        this.commandService = useService("command");
        this.companyService = useService('company');
        
        // OSUS Properties: Safe background image handling with error protection
        try {
            if (this.companyService.currentCompany.has_background_image) {
                this.backgroundImageUrl = url('/web/image', {
                    model: 'res.company',
                    field: 'background_image',
                    id: this.companyService.currentCompany.id
                });
            } else {
                this.backgroundImageUrl = '/muk_web_theme/static/src/img/background.png';
            }
        } catch (error) {
            console.error('OSUS AppsMenu: Error loading background image', error);
            this.backgroundImageUrl = '/muk_web_theme/static/src/img/background.png';
        }
        
        // Command palette keyboard shortcut handler with CloudPepper protection
        useEffect(
            (open) => {
                if (open) {
                    const openMainPalette = (ev) => {
                        try {
                            if (
                                !this.commandPaletteOpen && 
                                ev.key.length === 1 &&
                                !ev.ctrlKey &&
                                !ev.altKey
                            ) {
                                this.commandService.openMainPalette(
                                    { searchValue: `/${ev.key}` }, 
                                    () => { this.commandPaletteOpen = false; }
                                );
                                this.commandPaletteOpen = true;
                            }
                        } catch (error) {
                            console.error('OSUS AppsMenu: Command palette error', error);
                        }
                    };
                    
                    window.addEventListener("keydown", openMainPalette);
                    return () => {
                        window.removeEventListener("keydown", openMainPalette);
                        this.commandPaletteOpen = false;
                    };
                }
            },
            () => [this.state.open]
        );
        
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", this.close);
    }
}
