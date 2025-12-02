/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted} = owl
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

/**
 * Formats a number with K/M/B abbreviations
 * @param {number} value - The number to format
 * @returns {string} - Formatted number string
 */
function formatCurrency(value) {
    if (value === null || value === undefined || value === 0) {
        return '0';
    }
    
    const absValue = Math.abs(value);
    let formatted;
    
    if (absValue >= 1000000000) {
        // Billions
        formatted = (value / 1000000000).toFixed(2) + ' B';
    } else if (absValue >= 1000000) {
        // Millions
        formatted = (value / 1000000).toFixed(2) + ' M';
    } else if (absValue >= 1000) {
        // Thousands
        formatted = (value / 1000).toFixed(2) + ' K';
    } else {
        // Less than 1000
        formatted = value.toFixed(2);
    }
    
    return formatted;
}

export class CRMDashboard extends Component {
