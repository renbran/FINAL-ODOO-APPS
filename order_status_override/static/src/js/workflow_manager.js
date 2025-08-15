/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * OSUS Workflow Manager - Enterprise Sales Order Workflow Management
 * Handles status transitions, commission calculations, and user notifications
 */
export class OSUSWorkflowManager extends Component {
    static template = "order_status_override.WorkflowManagerTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");

        this.state = useState({
            isLoading: false,
            currentStatus: null,
            workflowSteps: [],
            commissionData: null,
            assignedUsers: {},
            canTransition: false,
            nextActions: [],
        });

        onWillStart(this.loadWorkflowData);
        onMounted(this.initializeWorkflow);
    }

    /**
     * Load workflow data and current status
     */
    async loadWorkflowData() {
        this.state.isLoading = true;
        try {
            const workflowData = await this.orm.call(
                "sale.order",
                "get_workflow_data",
                [this.props.record.resId]
            );
            
            this.state.currentStatus = workflowData.current_status;
            this.state.workflowSteps = workflowData.workflow_steps;
            this.state.assignedUsers = workflowData.assigned_users;
            this.state.canTransition = workflowData.can_transition;
            this.state.nextActions = workflowData.next_actions;
            
            // Load commission data if in commission stage
            if (this.state.currentStatus.code === 'commission_progress') {
                await this.loadCommissionData();
            }
            
        } catch (error) {
            this.notification.add(
                _t("Failed to load workflow data: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Load commission calculation data
     */
    async loadCommissionData() {
        try {
            this.state.commissionData = await this.orm.call(
                "sale.order",
                "get_commission_data",
                [this.props.record.resId]
            );
        } catch (error) {
            console.error("Failed to load commission data:", error);
        }
    }

    /**
     * Initialize workflow UI components
     */
    initializeWorkflow() {
        this.updateProgressBar();
        this.bindEventListeners();
    }

    /**
     * Update workflow progress bar visualization
     */
    updateProgressBar() {
        const steps = this.el.querySelectorAll('.workflow-step');
        const currentStepIndex = this.state.workflowSteps.findIndex(
            step => step.code === this.state.currentStatus.code
        );

        steps.forEach((step, index) => {
            const circle = step.querySelector('.step-circle');
            if (index < currentStepIndex) {
                circle.classList.add('completed');
                circle.classList.remove('active', 'pending');
            } else if (index === currentStepIndex) {
                circle.classList.add('active');
                circle.classList.remove('completed', 'pending');
            } else {
                circle.classList.add('pending');
                circle.classList.remove('completed', 'active');
            }
        });
    }

    /**
     * Bind event listeners for workflow interactions
     */
    bindEventListeners() {
        // Add hover effects and click handlers
        const actionButtons = this.el.querySelectorAll('.workflow-action-btn');
        actionButtons.forEach(button => {
            button.addEventListener('click', this.handleActionClick.bind(this));
        });
    }

    /**
     * Handle workflow action button clicks
     */
    async handleActionClick(event) {
        const action = event.target.dataset.action;
        const requiresConfirmation = event.target.dataset.confirm === 'true';

        if (requiresConfirmation) {
            const confirmed = await this.showConfirmationDialog(action);
            if (!confirmed) return;
        }

        await this.executeWorkflowAction(action);
    }

    /**
     * Show confirmation dialog for critical actions
     */
    async showConfirmationDialog(action) {
        return new Promise((resolve) => {
            this.dialog.add("web.ConfirmationDialog", {
                title: _t("Confirm Action"),
                body: _t("Are you sure you want to proceed with this action? This cannot be undone."),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });
    }

    /**
     * Execute workflow action
     */
    async executeWorkflowAction(action) {
        this.state.isLoading = true;
        
        try {
            const result = await this.orm.call(
                "sale.order",
                action,
                [this.props.record.resId]
            );

            if (result.success) {
                // Show success notification
                this.showNotification(result.message, 'success');
                
                // Reload workflow data
                await this.loadWorkflowData();
                
                // Trigger record reload
                await this.props.record.load();
                
                // Add transition animation
                this.addTransitionAnimation();
                
            } else {
                this.showNotification(result.message || _t("Action failed"), 'warning');
            }
            
        } catch (error) {
            this.showNotification(
                _t("Failed to execute action: %s", error.message),
                'danger'
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Show custom OSUS notification
     */
    showNotification(message, type = 'success') {
        // Create custom notification element
        const notification = document.createElement('div');
        notification.className = `osus-toast-notification ${type}`;
        notification.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">
                    ${this.getNotificationIcon(type)}
                </div>
                <div class="toast-message">${message}</div>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    ×
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Get notification icon based on type
     */
    getNotificationIcon(type) {
        const icons = {
            success: '✓',
            warning: '!',
            danger: '✗',
            info: 'i'
        };
        return icons[type] || 'i';
    }

    /**
     * Add transition animation to workflow components
     */
    addTransitionAnimation() {
        const workflowElement = this.el.querySelector('.osus-workflow-progress');
        if (workflowElement) {
            workflowElement.classList.add('osus-status-transition', 'entering');
            
            setTimeout(() => {
                workflowElement.classList.remove('entering');
            }, 300);
        }
    }

    /**
     * Handle commission calculation request
     */
    async onCalculateCommission() {
        if (this.props.readonly) return;
        
        this.state.isLoading = true;
        
        try {
            const result = await this.orm.call(
                "sale.order",
                "calculate_commission_preview",
                [this.props.record.resId]
            );
            
            if (result.success) {
                this.state.commissionData = result.data;
                this.showNotification(_t("Commission calculated successfully"), 'success');
            } else {
                this.showNotification(result.message || _t("Commission calculation failed"), 'warning');
            }
            
        } catch (error) {
            this.showNotification(
                _t("Failed to calculate commission: %s", error.message),
                'danger'
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Handle user assignment changes
     */
    async onAssignUser(role, userId) {
        if (this.props.readonly) return;
        
        try {
            await this.orm.call(
                "sale.order",
                "assign_user_to_role",
                [this.props.record.resId, role, userId]
            );
            
            this.showNotification(_t("User assigned successfully"), 'success');
            await this.loadWorkflowData();
            
        } catch (error) {
            this.showNotification(
                _t("Failed to assign user: %s", error.message),
                'danger'
            );
        }
    }

    /**
     * Get current workflow progress percentage
     */
    get workflowProgress() {
        if (!this.state.workflowSteps.length) return 0;
        
        const currentIndex = this.state.workflowSteps.findIndex(
            step => step.code === this.state.currentStatus.code
        );
        
        return Math.round(((currentIndex + 1) / this.state.workflowSteps.length) * 100);
    }

    /**
     * Get formatted commission summary
     */
    get commissionSummary() {
        if (!this.state.commissionData) return null;
        
        return {
            totalCommission: this.formatCurrency(this.state.commissionData.total_commission),
            externalCommission: this.formatCurrency(this.state.commissionData.external_commission),
            internalCommission: this.formatCurrency(this.state.commissionData.internal_commission),
            commissionRate: `${this.state.commissionData.commission_rate}%`,
        };
    }

    /**
     * Format currency values
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: this.props.record.data.currency_id?.data?.name || 'USD'
        }).format(amount || 0);
    }

    /**
     * Check if user can perform action
     */
    canPerformAction(action) {
        return this.state.nextActions.includes(action) && 
               this.state.canTransition && 
               !this.props.readonly;
    }
}

// Register the component
registry.category("fields").add("osus_workflow_manager", OSUSWorkflowManager);
