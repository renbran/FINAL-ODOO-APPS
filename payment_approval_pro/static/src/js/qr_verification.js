/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * QR Code Verification Component
 * 
 * Handles QR code display and verification for payment vouchers
 * Provides secure verification through token-based URLs
 */
export class QRVerificationWidget extends Component {
    static template = "payment_approval_pro.QRVerificationWidget";
    static props = {
        record: Object,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        
        this.state = useState({
            showQRCode: false,
            isVerifying: false,
            verificationResult: null,
            qrCodeData: null,
        });
    }

    /**
     * Toggle QR code display
     */
    onToggleQRCode() {
        this.state.showQRCode = !this.state.showQRCode;
        
        if (this.state.showQRCode && !this.state.qrCodeData) {
            this.loadQRCodeData();
        }
    }

    /**
     * Load QR code data from the record
     */
    async loadQRCodeData() {
        try {
            const voucherId = this.props.record.resId;
            
            if (!voucherId) {
                return;
            }
            
            const qrData = await this.orm.call(
                "payment.voucher",
                "get_qr_code_data",
                [voucherId]
            );
            
            this.state.qrCodeData = qrData;
            
        } catch (error) {
            this.notification.add(
                _t("Failed to load QR code data: %s", error.message || error),
                { type: "warning" }
            );
        }
    }

    /**
     * Verify QR code through public verification endpoint
     */
    async onVerifyQRCode() {
        if (this.state.isVerifying) return;
        
        this.state.isVerifying = true;
        this.state.verificationResult = null;
        
        try {
            const voucherId = this.props.record.resId;
            
            const result = await this.orm.call(
                "payment.voucher",
                "verify_qr_code",
                [voucherId]
            );
            
            this.state.verificationResult = result;
            
            if (result.valid) {
                this.notification.add(
                    _t("QR code verification successful"),
                    { type: "success" }
                );
            } else {
                this.notification.add(
                    _t("QR code verification failed: %s", result.message || "Invalid code"),
                    { type: "danger" }
                );
            }
            
        } catch (error) {
            this.notification.add(
                _t("QR code verification error: %s", error.message || error),
                { type: "danger" }
            );
        } finally {
            this.state.isVerifying = false;
        }
    }

    /**
     * Open verification URL in new tab
     */
    onOpenVerificationURL() {
        const qrData = this.state.qrCodeData;
        
        if (qrData && qrData.verification_url) {
            window.open(qrData.verification_url, '_blank', 'noopener,noreferrer');
        } else {
            this.notification.add(
                _t("No verification URL available"),
                { type: "warning" }
            );
        }
    }

    /**
     * Copy verification URL to clipboard
     */
    async onCopyVerificationURL() {
        const qrData = this.state.qrCodeData;
        
        if (!qrData || !qrData.verification_url) {
            this.notification.add(
                _t("No verification URL available"),
                { type: "warning" }
            );
            return;
        }
        
        try {
            await navigator.clipboard.writeText(qrData.verification_url);
            
            this.notification.add(
                _t("Verification URL copied to clipboard"),
                { type: "success" }
            );
            
        } catch (error) {
            // Fallback for browsers that don't support clipboard API
            this._fallbackCopyToClipboard(qrData.verification_url);
        }
    }

    /**
     * Fallback method for copying to clipboard
     */
    _fallbackCopyToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.notification.add(
                _t("Verification URL copied to clipboard"),
                { type: "success" }
            );
        } catch (error) {
            this.notification.add(
                _t("Failed to copy URL to clipboard"),
                { type: "warning" }
            );
        } finally {
            document.body.removeChild(textArea);
        }
    }

    /**
     * Download QR code as image
     */
    onDownloadQRCode() {
        const qrData = this.state.qrCodeData;
        
        if (!qrData || !qrData.qr_code_base64) {
            this.notification.add(
                _t("No QR code image available"),
                { type: "warning" }
            );
            return;
        }
        
        try {
            // Create download link
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${qrData.qr_code_base64}`;
            link.download = `payment_voucher_${qrData.voucher_number || 'qr_code'}.png`;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.notification.add(
                _t("QR code downloaded successfully"),
                { type: "success" }
            );
            
        } catch (error) {
            this.notification.add(
                _t("Failed to download QR code: %s", error.message || error),
                { type: "danger" }
            );
        }
    }

    /**
     * Get QR code image source
     */
    getQRCodeSrc() {
        const qrData = this.state.qrCodeData;
        
        if (qrData && qrData.qr_code_base64) {
            return `data:image/png;base64,${qrData.qr_code_base64}`;
        }
        
        return null;
    }

    /**
     * Get verification status class
     */
    getVerificationStatusClass() {
        const result = this.state.verificationResult;
        
        if (!result) {
            return '';
        }
        
        return result.valid ? 'text-success' : 'text-danger';
    }

    /**
     * Get verification status icon
     */
    getVerificationStatusIcon() {
        const result = this.state.verificationResult;
        
        if (!result) {
            return '';
        }
        
        return result.valid ? 'fa-check-circle' : 'fa-times-circle';
    }

    /**
     * Get verification status text
     */
    getVerificationStatusText() {
        const result = this.state.verificationResult;
        
        if (!result) {
            return '';
        }
        
        return result.valid 
            ? _t('QR code is valid and verified')
            : _t('QR code verification failed: %s', result.message || 'Invalid');
    }
}

// Register the QR verification widget
registry.category("fields").add("qr_verification_widget", QRVerificationWidget);

/**
 * QR Code Field Widget - Simple field display
 */
export class QRCodeField extends Component {
    static template = "payment_approval_pro.QRCodeField";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    /**
     * Get QR code image source from field value
     */
    getQRCodeSrc() {
        const fieldValue = this.props.record.data[this.props.name];
        
        if (fieldValue) {
            return `data:image/png;base64,${fieldValue}`;
        }
        
        return null;
    }

    /**
     * Check if QR code is available
     */
    hasQRCode() {
        return !!this.props.record.data[this.props.name];
    }
}

// Register the QR code field widget
registry.category("fields").add("qr_code_field", QRCodeField);
