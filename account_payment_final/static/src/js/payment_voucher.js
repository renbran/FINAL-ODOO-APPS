/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Payment Voucher Enhanced JavaScript Components
 * OSUS Real Estate - Payment Voucher System
 */

// Workflow Progress Widget
export class WorkflowProgressWidget extends Component {
    static template = "account_payment_final.WorkflowProgress";
    
    setup() {
        this.notification = useService("notification");
        this.state = useState({
            currentStep: this.props.record.data.workflow_step || 0,
            totalSteps: this.props.record.data.total_steps || 5,
            approvalState: this.props.record.data.approval_state || 'draft'
        });
    }

    get progressPercentage() {
        if (this.state.totalSteps === 0) return 0;
        return Math.round((this.state.currentStep / this.state.totalSteps) * 100);
    }

    get progressClass() {
        const percentage = this.progressPercentage;
        if (percentage === 100) return 'bg-success';
        if (percentage >= 80) return 'bg-info';
        if (percentage >= 60) return 'bg-warning';
        return 'bg-primary';
    }

    get stepDescription() {
        const steps = {
            0: 'Draft',
            1: 'Submitted',
            2: 'Under Review',
            3: 'For Approval',
            4: 'For Authorization',
            5: 'Posted'
        };
        return steps[this.state.currentStep] || 'Unknown';
    }
}

// QR Code Verification Widget
export class QRCodeWidget extends Component {
    static template = "account_payment_final.QRCodeWidget";
    
    setup() {
        this.notification = useService("notification");
        this.qrRef = useRef("qrCode");
    }

    async copyVerificationUrl() {
        const url = this.props.record.data.verification_url;
        if (url) {
            try {
                await navigator.clipboard.writeText(url);
                this.notification.add("Verification URL copied to clipboard!", {
                    type: "success",
                });
            } catch (err) {
                this.notification.add("Failed to copy URL", {
                    type: "warning",
                });
            }
        }
    }

    openVerification() {
        const url = this.props.record.data.verification_url;
        if (url) {
            window.open(url, '_blank');
        }
    }
}

// Signature Upload Widget
export class SignatureWidget extends Component {
    static template = "account_payment_final.SignatureWidget";
    
    setup() {
        this.notification = useService("notification");
        this.fileInput = useRef("fileInput");
        this.canvas = useRef("signatureCanvas");
        this.state = useState({
            isDrawing: false,
            signatureMode: 'upload' // 'upload' or 'draw'
        });
    }

    onMounted() {
        if (this.canvas.el) {
            this.setupCanvas();
        }
    }

    setupCanvas() {
        const canvas = this.canvas.el;
        const ctx = canvas.getContext('2d');
        
        canvas.width = 400;
        canvas.height = 200;
        
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        
        // Mouse events
        canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        canvas.addEventListener('mousemove', this.draw.bind(this));
        canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        
        // Touch events for mobile
        canvas.addEventListener('touchstart', this.handleTouch.bind(this));
        canvas.addEventListener('touchmove', this.handleTouch.bind(this));
        canvas.addEventListener('touchend', this.stopDrawing.bind(this));
    }

    startDrawing(e) {
        this.state.isDrawing = true;
        const rect = this.canvas.el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ctx = this.canvas.el.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    draw(e) {
        if (!this.state.isDrawing) return;
        
        const rect = this.canvas.el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ctx = this.canvas.el.getContext('2d');
        ctx.lineTo(x, y);
        ctx.stroke();
    }

    stopDrawing() {
        this.state.isDrawing = false;
    }

    handleTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                        e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.canvas.el.dispatchEvent(mouseEvent);
    }

    clearSignature() {
        const canvas = this.canvas.el;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    saveSignature() {
        const canvas = this.canvas.el;
        const dataURL = canvas.toDataURL('image/png');
        
        // Convert to base64 for Odoo
        const base64 = dataURL.split(',')[1];
        
        // Trigger change event to update the field
        this.props.update(base64);
        
        this.notification.add("Signature saved successfully!", {
            type: "success",
        });
    }

    switchMode(mode) {
        this.state.signatureMode = mode;
        if (mode === 'draw' && this.canvas.el) {
            this.clearSignature();
        }
    }

    handleFileUpload(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const base64 = event.target.result.split(',')[1];
                    this.props.update(base64);
                    this.notification.add("Signature uploaded successfully!", {
                        type: "success",
                    });
                };
                reader.readAsDataURL(file);
            } else {
                this.notification.add("Please select an image file", {
                    type: "warning",
                });
            }
        }
    }
}

// Workflow Action Buttons Enhancement
export class WorkflowButtons extends Component {
    static template = "account_payment_final.WorkflowButtons";
    
    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
    }

    async executeWorkflowAction(action, confirmMessage = null) {
        if (confirmMessage) {
            const confirmed = confirm(confirmMessage);
            if (!confirmed) return;
        }

        try {
            const result = await this.orm.call(
                "account.payment",
                action,
                [this.props.record.data.id]
            );

            if (result && result.type === 'ir.actions.client') {
                // Handle notification result
                this.notification.add(result.params.message, {
                    type: result.params.type,
                });
            }

            // Reload the record to update the view
            await this.props.record.load();
            
        } catch (error) {
            this.notification.add("Action failed: " + error.message, {
                type: "danger",
            });
        }
    }

    get availableActions() {
        const state = this.props.record.data.approval_state;
        const paymentType = this.props.record.data.payment_type;
        
        const actions = [];
        
        switch (state) {
            case 'draft':
                actions.push({
                    name: 'Submit for Review',
                    method: 'action_submit_for_review',
                    class: 'btn-primary',
                    confirm: 'Submit this payment voucher for review?'
                });
                break;
                
            case 'under_review':
                actions.push({
                    name: 'Review & Forward',
                    method: 'action_review_approve',
                    class: 'btn-success',
                    groups: ['account_payment_final.group_payment_voucher_reviewer']
                });
                actions.push({
                    name: 'Reject',
                    method: 'action_reject_payment',
                    class: 'btn-danger',
                    confirm: 'Are you sure you want to reject this voucher?',
                    groups: ['account_payment_final.group_payment_voucher_reviewer']
                });
                break;
                
            case 'for_approval':
                if (paymentType === 'outbound') {
                    actions.push({
                        name: 'Approve Payment',
                        method: 'action_approve_payment',
                        class: 'btn-success',
                        groups: ['account_payment_final.group_payment_voucher_approver']
                    });
                }
                actions.push({
                    name: 'Reject',
                    method: 'action_reject_payment',
                    class: 'btn-danger',
                    confirm: 'Are you sure you want to reject this voucher?',
                    groups: ['account_payment_final.group_payment_voucher_approver']
                });
                break;
                
            case 'for_authorization':
                actions.push({
                    name: 'Authorize Payment',
                    method: 'action_authorize_payment',
                    class: 'btn-warning',
                    groups: ['account_payment_final.group_payment_voucher_authorizer']
                });
                actions.push({
                    name: 'Reject',
                    method: 'action_reject_payment',
                    class: 'btn-danger',
                    confirm: 'Are you sure you want to reject this voucher?',
                    groups: ['account_payment_final.group_payment_voucher_authorizer']
                });
                break;
                
            case 'approved':
                actions.push({
                    name: 'Post to Ledger',
                    method: 'action_post_payment',
                    class: 'btn-primary',
                    groups: ['account_payment_final.group_payment_voucher_poster']
                });
                break;
        }
        
        return actions;
    }
}

// Amount in Words Formatter
export function formatAmountInWords(amount, currency) {
    // This would integrate with the Python num2words conversion
    // For now, providing a basic JavaScript implementation
    
    const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
    const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
    const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
    const thousands = ['', 'Thousand', 'Million', 'Billion'];

    function convertHundreds(num) {
        let result = '';
        
        if (num >= 100) {
            result += ones[Math.floor(num / 100)] + ' Hundred ';
            num %= 100;
        }
        
        if (num >= 20) {
            result += tens[Math.floor(num / 10)] + ' ';
            num %= 10;
        } else if (num >= 10) {
            result += teens[num - 10] + ' ';
            return result;
        }
        
        if (num > 0) {
            result += ones[num] + ' ';
        }
        
        return result;
    }

    function convertToWords(num) {
        if (num === 0) return 'Zero';
        
        let result = '';
        let thousandCounter = 0;
        
        while (num > 0) {
            if (num % 1000 !== 0) {
                result = convertHundreds(num % 1000) + thousands[thousandCounter] + ' ' + result;
            }
            num = Math.floor(num / 1000);
            thousandCounter++;
        }
        
        return result.trim();
    }

    const integerPart = Math.floor(amount);
    const decimalPart = Math.round((amount - integerPart) * 100);
    
    let result = convertToWords(integerPart);
    
    if (decimalPart > 0) {
        result += ' and ' + convertToWords(decimalPart) + ' Cents';
    }
    
    result += ' ' + (currency || 'Dollars') + ' Only';
    
    return result;
}

// Dashboard Statistics Component
export class PaymentDashboard extends Component {
    static template = "account_payment_final.Dashboard";
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            stats: {
                pending_review: 0,
                pending_approval: 0,
                pending_authorization: 0,
                approved: 0,
                posted_today: 0,
                total_amount_pending: 0
            },
            loading: true
        });
        
        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const stats = await this.orm.call(
                "account.payment",
                "get_dashboard_statistics",
                []
            );
            
            this.state.stats = stats;
            this.state.loading = false;
            
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.loading = false;
        }
    }

    async openPendingReviews() {
        // Implementation to open pending reviews
    }

    async openPendingApprovals() {
        // Implementation to open pending approvals
    }
}

// Register components
registry.category("fields").add("workflow_progress", WorkflowProgressWidget);
registry.category("fields").add("qr_code_widget", QRCodeWidget);
registry.category("fields").add("signature_widget", SignatureWidget);
registry.category("fields").add("workflow_buttons", WorkflowButtons);

// Utility functions for global use
window.PaymentVoucherUtils = {
    formatAmountInWords,
    
    // Format currency with proper symbols
    formatCurrency(amount, currency) {
        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency || 'USD',
        });
        return formatter.format(amount);
    },
    
    // Validate payment data
    validatePaymentData(data) {
        const errors = [];
        
        if (!data.partner_id) {
            errors.push('Partner is required');
        }
        
        if (!data.amount || data.amount <= 0) {
            errors.push('Amount must be greater than zero');
        }
        
        if (!data.journal_id) {
            errors.push('Journal is required');
        }
        
        if (!data.date) {
            errors.push('Payment date is required');
        }
        
        return errors;
    },
    
    // Get workflow step description
    getWorkflowStepDescription(step, paymentType) {
        const steps = {
            inbound: {
                0: 'Draft',
                1: 'Submitted for Review',
                2: 'Under Review',
                3: 'Posted'
            },
            outbound: {
                0: 'Draft',
                1: 'Submitted for Review',
                2: 'Under Review',
                3: 'For Approval',
                4: 'For Authorization',
                5: 'Posted'
            }
        };
        
        return steps[paymentType]?.[step] || 'Unknown';
    }
};

console.log('OSUS Payment Voucher Enhanced - JavaScript loaded successfully');
