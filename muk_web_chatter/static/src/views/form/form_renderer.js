/* @odoo-module */

import { useState, useRef } from '@odoo/owl';
import { patch } from '@web/core/utils/patch';
import { browser } from "@web/core/browser/browser";
import { session } from '@web/session';

import { FormRenderer } from '@web/views/form/form_renderer';

patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.chatterState = useState({
            width: browser.localStorage.getItem('muk_web_chatter.width');
});
        this.chatterContainer = useRef('chatterContainer');
    },
    onStartChatterResize(ev) {
        if (ev.button !== 0) {
            return;
        }
        const initialX = ev.pageX;
        const chatterElement = this.chatterContainer.el;
        const initialWidth = chatterElement.offsetWidth;
        const resizeStoppingEvents = [
            'keydown', 'mousedown', 'mouseup'
        ];
        const resizePanel = (ev) => {
            try {
                ev.preventDefault();
                ev.stopPropagation();
                const newWidth = Math.min(
                    Math.max(50, initialWidth - (ev.pageX - initialX)),
                    Math.max(chatterElement.parentElement.offsetWidth - 250, 250)
                );
                browser.localStorage.setItem('osus_chatter.width', newWidth);
                this.chatterState.width = newWidth;
            } catch (error) {
                console.error('OSUS FormRenderer: Resize panel error', error);
            }
        };
        const stopResize = (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            if (ev.type === 'mousedown' && ev.button === 0) {
                return;
            }
            document.removeEventListener('mousemove', resizePanel, true);
            resizeStoppingEvents.forEach((stoppingEvent) => {
                document.removeEventListener(stoppingEvent, stopResize, true);
            });
            document.activeElement.blur();
        };
        document.addEventListener('mousemove', resizePanel, true);
        resizeStoppingEvents.forEach((stoppingEvent) => {
            document.addEventListener(stoppingEvent, stopResize, true);
        });
    },
    onDoubleClickChatterResize(ev) {
        try {
            browser.localStorage.removeItem('osus_chatter.width');
            this.chatterState.width = false;
        } catch (error) {
            console.error('OSUS FormRenderer: Double click resize error', error);
        }
    }
});

