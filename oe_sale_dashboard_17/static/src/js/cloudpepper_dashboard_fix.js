/** @odoo-module **/
/**
 * CloudPepper Dashboard Module Error Fix
 * Specific fixes for dashboard modules and Chart.js errors
 */

import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";

// Global dashboard error handling
const DashboardErrorHandler = {
    
    handleChartError(error, chartType = 'Unknown') {
        console.warn(`[CloudPepper] Chart.js error in ${chartType}:`, error);
        return {
            labels: ['No Data'],
            datasets: [{
                label: 'Error Loading Data',
                data: [0],
                backgroundColor: ['#ff6b6b']
            }]
        };
    },
    
    async safeDataLoad(loader, fallback = {}) {
        try {
            return await loader();
        } catch (error) {
            console.warn('[CloudPepper] Dashboard data load error:', error);
            return fallback;
        }
    }
};

// Patch dashboard components
const dashboardComponents = [
    'SalesDashboard',
    'CRMDashboard', 
    'PaymentDashboard',
    'ExecutiveDashboard'
];

dashboardComponents.forEach(componentName => {
    try {
        // Try to patch if component exists
        const component = registry.category("views").get(componentName, null);
        if (component) {
            patch(component.prototype, {
                
                async setup() {
                    super.setup();
                    this.dashboardErrorHandler = DashboardErrorHandler;
                },
                
                async loadDashboardData() {
                    return await this.dashboardErrorHandler.safeDataLoad(
                        () => this._originalLoadDashboardData(),
                        { message: "Dashboard data temporarily unavailable" }
                    );
                },
                
                _originalLoadDashboardData() {
                    // Override in specific components
                    return {};
                }
            });
            
            console.log(`[CloudPepper] Protected dashboard component: ${componentName}`);
        }
    } catch (error) {
        console.warn(`[CloudPepper] Could not patch ${componentName}:`, error);
    }
});

console.log('[CloudPepper] Dashboard Module Error Fix Loaded');
