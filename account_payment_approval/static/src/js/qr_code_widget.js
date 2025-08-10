/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class QRCodeWidget extends Component {
    static template = "account_payment_approval.QRCodeWidget";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
        size: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: false,
            qrCodeData: null,
            verificationToken: null,
            error: null,
        });

        onWillStart(this.loadQRCode);
    }

    async loadQRCode() {
        const qrData = this.props.record.data[this.props.name];
        const token = this.props.record.data.verification_token;
        
        if (qrData) {
            this.state.qrCodeData = qrData;
            this.state.verificationToken = token;
        }
    }

    async generateQRCode() {
        if (this.props.readonly) return;
        
        this.state.isLoading = true;
        this.state.error = null;

        try {
            const result = await this.orm.call(
                "account.payment",
                "generate_qr_code",
                [this.props.record.resId]
            );

            if (result.success) {
                this.state.qrCodeData = result.qr_code_data;
                this.state.verificationToken = result.verification_token;
                
                // Update the record
                this.props.record.update({
                    [this.props.name]: result.qr_code_data,
                    verification_token: result.verification_token
                });

                this.notification.add(_t("QR code generated successfully"), { type: "success" });
            } else {
                throw new Error(result.error || _t("Failed to generate QR code"));
            }

        } catch (error) {
            console.error("Error generating QR code:", error);
            this.state.error = error.message || _t("Failed to generate QR code");
            this.notification.add(
                _t("Error generating QR code: %s", this.state.error),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async regenerateQRCode() {
        if (this.props.readonly) return;
        
        this.state.isLoading = true;
        this.state.error = null;

        try {
            const result = await this.orm.call(
                "account.payment",
                "regenerate_qr_code",
                [this.props.record.resId]
            );

            if (result.success) {
                this.state.qrCodeData = result.qr_code_data;
                this.state.verificationToken = result.verification_token;
                
                // Update the record
                this.props.record.update({
                    [this.props.name]: result.qr_code_data,
                    verification_token: result.verification_token
                });

                this.notification.add(_t("QR code regenerated successfully"), { type: "success" });
            } else {
                throw new Error(result.error || _t("Failed to regenerate QR code"));
            }

        } catch (error) {
            console.error("Error regenerating QR code:", error);
            this.state.error = error.message || _t("Failed to regenerate QR code");
            this.notification.add(
                _t("Error regenerating QR code: %s", this.state.error),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    copyVerificationLink() {
        if (!this.state.verificationToken) {
            this.notification.add(_t("No verification token available"), { type: "warning" });
            return;
        }

        const baseUrl = window.location.origin;
        const verificationUrl = `${baseUrl}/payment/verify/${this.state.verificationToken}`;
        
        navigator.clipboard.writeText(verificationUrl).then(() => {
            this.notification.add(_t("Verification link copied to clipboard"), { type: "success" });
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = verificationUrl;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.notification.add(_t("Verification link copied to clipboard"), { type: "success" });
            } catch (err) {
                this.notification.add(_t("Failed to copy verification link"), { type: "danger" });
            }
            
            document.body.removeChild(textArea);
        });
    }

    openVerificationPage() {
        if (!this.state.verificationToken) {
            this.notification.add(_t("No verification token available"), { type: "warning" });
            return;
        }

        const baseUrl = window.location.origin;
        const verificationUrl = `${baseUrl}/payment/verify/${this.state.verificationToken}`;
        window.open(verificationUrl, '_blank');
    }

    downloadQRCode() {
        if (!this.state.qrCodeData) {
            this.notification.add(_t("No QR code available to download"), { type: "warning" });
            return;
        }

        try {
            // Create download link
            const link = document.createElement('a');
            link.href = this.state.qrCodeData;
            link.download = `Payment_QR_${this.props.record.data.voucher_number || 'DRAFT'}.png`;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.notification.add(_t("QR code downloaded successfully"), { type: "success" });
        } catch (error) {
            console.error("Error downloading QR code:", error);
            this.notification.add(_t("Failed to download QR code"), { type: "danger" });
        }
    }

    get qrCodeSize() {
        return this.props.size || 200;
    }

    get hasQRCode() {
        return !!this.state.qrCodeData;
    }

    get canGenerate() {
        return !this.props.readonly && this.props.record.resId;
    }

    get verificationUrl() {
        if (!this.state.verificationToken) return '';
        const baseUrl = window.location.origin;
        return `${baseUrl}/payment/verify/${this.state.verificationToken}`;
    }
}

// Register the QR code widget
registry.category("fields").add("qr_code_widget", QRCodeWidget);
