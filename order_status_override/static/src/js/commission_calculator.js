/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * OSUS Commission Calculator - Integration with commission_ax module
 * Provides real-time commission calculations and previews
 */
export class OSUSCommissionCalculator extends Component {
    static template = "order_status_override.CommissionCalculatorTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            isLoading: false,
            commissionData: {
                external_commissions: [],
                internal_commissions: [],
                total_external: 0,
                total_internal: 0,
                total_commission: 0,
                order_total: 0,
                commission_percentage: 0,
            },
            calculationMethods: [],
            availableUsers: [],
            showAdvanced: false,
        });

        onWillStart(this.loadCommissionData);
    }

    /**
     * Load commission data from commission_ax integration
     */
    async loadCommissionData() {
        this.state.isLoading = true;
        try {
            // Get commission data from commission_ax module
            const commissionResult = await this.orm.call(
                "sale.order",
                "get_commission_calculation_data",
                [this.props.record.resId]
            );

            if (commissionResult.success) {
                this.state.commissionData = commissionResult.data;
            }

            // Load calculation methods and users
            const [methods, users] = await Promise.all([
                this.orm.call("sale.order", "get_commission_calculation_methods", []),
                this.orm.call("res.users", "search_read", [
                    [["active", "=", true]],
                    ["id", "name", "email"]
                ])
            ]);

            this.state.calculationMethods = methods;
            this.state.availableUsers = users;

        } catch (error) {
            this.notification.add(
                _t("Failed to load commission data: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Calculate commission preview with current settings
     */
    async calculatePreview() {
        this.state.isLoading = true;
        
        try {
            const result = await this.orm.call(
                "sale.order",
                "preview_commission_calculation",
                [this.props.record.resId]
            );

            if (result.success) {
                this.state.commissionData = result.data;
                this.showSuccessNotification(_t("Commission preview updated"));
            } else {
                this.showErrorNotification(result.message || _t("Calculation failed"));
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to calculate preview: %s", error.message));
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Apply commission calculations to the order
     */
    async applyCommissions() {
        if (this.props.readonly) return;

        const confirmed = await this.showConfirmationDialog(
            _t("Apply Commission Calculations"),
            _t("This will apply the commission calculations to the order. Continue?")
        );

        if (!confirmed) return;

        this.state.isLoading = true;

        try {
            const result = await this.orm.call(
                "sale.order",
                "apply_commission_calculations",
                [this.props.record.resId]
            );

            if (result.success) {
                this.showSuccessNotification(_t("Commission calculations applied successfully"));
                
                // Trigger workflow transition to next stage
                await this.triggerWorkflowTransition();
                
                // Reload data
                await this.loadCommissionData();
                await this.props.record.load();
                
            } else {
                this.showErrorNotification(result.message || _t("Failed to apply calculations"));
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to apply commissions: %s", error.message));
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Add new external commission entry
     */
    async addExternalCommission() {
        if (this.props.readonly) return;

        try {
            const result = await this.orm.call(
                "sale.order",
                "add_external_commission",
                [this.props.record.resId, {
                    commission_group: 'broker',
                    calculation_method: 'percentage',
                    rate_amount: 0.0,
                    partner_id: null,
                }]
            );

            if (result.success) {
                await this.loadCommissionData();
                this.showSuccessNotification(_t("External commission added"));
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to add commission: %s", error.message));
        }
    }

    /**
     * Add new internal commission entry
     */
    async addInternalCommission() {
        if (this.props.readonly) return;

        try {
            const result = await this.orm.call(
                "sale.order",
                "add_internal_commission",
                [this.props.record.resId, {
                    commission_group: 'agent_1',
                    calculation_method: 'percentage',
                    rate_amount: 0.0,
                    user_id: null,
                }]
            );

            if (result.success) {
                await this.loadCommissionData();
                this.showSuccessNotification(_t("Internal commission added"));
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to add commission: %s", error.message));
        }
    }

    /**
     * Remove commission entry
     */
    async removeCommission(commissionId, type) {
        if (this.props.readonly) return;

        const confirmed = await this.showConfirmationDialog(
            _t("Remove Commission"),
            _t("Are you sure you want to remove this commission entry?")
        );

        if (!confirmed) return;

        try {
            const method = type === 'external' ? 'remove_external_commission' : 'remove_internal_commission';
            const result = await this.orm.call("sale.order", method, [this.props.record.resId, commissionId]);

            if (result.success) {
                await this.loadCommissionData();
                this.showSuccessNotification(_t("Commission removed"));
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to remove commission: %s", error.message));
        }
    }

    /**
     * Update commission entry
     */
    async updateCommission(commissionId, type, data) {
        if (this.props.readonly) return;

        try {
            const method = type === 'external' ? 'update_external_commission' : 'update_internal_commission';
            const result = await this.orm.call("sale.order", method, [this.props.record.resId, commissionId, data]);

            if (result.success) {
                await this.calculatePreview();
            }

        } catch (error) {
            this.showErrorNotification(_t("Failed to update commission: %s", error.message));
        }
    }

    /**
     * Trigger workflow transition after commission application
     */
    async triggerWorkflowTransition() {
        try {
            await this.orm.call(
                "sale.order",
                "action_commission_completed",
                [this.props.record.resId]
            );
        } catch (error) {
            console.error("Failed to trigger workflow transition:", error);
        }
    }

    /**
     * Show confirmation dialog
     */
    async showConfirmationDialog(title, message) {
        return new Promise((resolve) => {
            this.env.services.dialog.add("web.ConfirmationDialog", {
                title: title,
                body: message,
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });
    }

    /**
     * Show success notification
     */
    showSuccessNotification(message) {
        this.notification.add(message, { type: "success" });
    }

    /**
     * Show error notification
     */
    showErrorNotification(message) {
        this.notification.add(message, { type: "danger" });
    }

    /**
     * Toggle advanced calculation view
     */
    toggleAdvancedView() {
        this.state.showAdvanced = !this.state.showAdvanced;
    }

    /**
     * Format currency display
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: this.props.record.data.currency_id?.data?.name || 'USD'
        }).format(amount || 0);
    }

    /**
     * Get commission calculation summary
     */
    get calculationSummary() {
        const data = this.state.commissionData;
        return {
            orderTotal: this.formatCurrency(data.order_total),
            totalCommission: this.formatCurrency(data.total_commission),
            totalExternal: this.formatCurrency(data.total_external),
            totalInternal: this.formatCurrency(data.total_internal),
            commissionPercentage: `${data.commission_percentage.toFixed(2)}%`,
            netAmount: this.formatCurrency(data.order_total - data.total_commission),
        };
    }

    /**
     * Get external commission groups for selection
     */
    get externalCommissionGroups() {
        return [
            { value: 'broker', label: _t('Broker') },
            { value: 'referrer', label: _t('Referrer') },
            { value: 'cashback', label: _t('Cashback') },
            { value: 'others', label: _t('Others') },
        ];
    }

    /**
     * Get internal commission groups for selection
     */
    get internalCommissionGroups() {
        return [
            { value: 'agent_1', label: _t('Agent 1') },
            { value: 'agent_2', label: _t('Agent 2') },
            { value: 'manager', label: _t('Manager') },
            { value: 'director', label: _t('Director') },
        ];
    }

    /**
     * Check if commission data is valid for application
     */
    get canApplyCommissions() {
        return (
            !this.props.readonly &&
            (this.state.commissionData.external_commissions.length > 0 ||
             this.state.commissionData.internal_commissions.length > 0) &&
            this.state.commissionData.total_commission > 0
        );
    }
}

// Register the component
registry.category("fields").add("osus_commission_calculator", OSUSCommissionCalculator);
