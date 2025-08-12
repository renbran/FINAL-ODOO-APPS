/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class QRCodeWidget extends Component {
    static template = "account_payment_approval.QRCodeWidget";
    static props = {
        record: Object,
        name: String,
        size: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            qrCodeData: null,
            verificationUrl: null,
            isLoading: false,
            error: null,
            showModal: false,
            verificationStats: null,
        });

        onMounted(this.loadQRData);
    }

    async loadQRData() {
        this.state.isLoading = true;
        this.state.error = null;

        try {
            const record = this.props.record.data;

            // Get QR code data from record
            if (record.qr_code) {
                this.state.qrCodeData = `data:image/png;base64,${record.qr_code}`;
            }

            if (record.verification_url) {
                this.state.verificationUrl = record.verification_url;
            }

            // Load verification statistics if available
            if (record.verification_token) {
                await this.loadVerificationStats(record.verification_token);
            }
        } catch (error) {
            console.error("Error loading QR data:", error);
            this.state.error = error.message || _t("Failed to load QR code data");
        } finally {
            this.state.isLoading = false;
        }
    }

    async loadVerificationStats(token) {
        try {
            const stats = await this.orm.call("account.payment", "get_qr_verification_stats", [], { token: token });

            if (stats.success) {
                this.state.verificationStats = stats.stats;
            }
        } catch (error) {
            console.warn("Could not load verification stats:", error);
        }
    }

    async regenerateQRCode() {
        this.state.isLoading = true;

        try {
            // Trigger QR code regeneration
            await this.orm.call(this.props.record.resModel, "generate_new_qr_code", [this.props.record.resId]);

            // Reload the record
            if (this.props.record.model && this.props.record.model.load) {
                await this.props.record.model.load();
            }

            // Reload QR data
            await this.loadQRData();

            this.notification.add(_t("QR code regenerated successfully"), { type: "success" });
        } catch (error) {
            console.error("Error regenerating QR code:", error);
            this.notification.add(_t("Failed to regenerate QR code: %s", error.message), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    downloadQRCode() {
        if (!this.state.qrCodeData) {
            this.notification.add(_t("No QR code available for download"), { type: "warning" });
            return;
        }

        try {
            // Create download link
            const link = document.createElement("a");
            link.href = this.state.qrCodeData;
            link.download = `payment_${this.props.record.data.voucher_number || "unknown"}_qr.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            this.notification.add(_t("QR code downloaded"), { type: "success" });
        } catch (error) {
            console.error("Error downloading QR code:", error);
            this.notification.add(_t("Failed to download QR code"), { type: "danger" });
        }
    }

    copyVerificationUrl() {
        if (!this.state.verificationUrl) {
            this.notification.add(_t("No verification URL available"), { type: "warning" });
            return;
        }

        try {
            navigator.clipboard
                .writeText(this.state.verificationUrl)
                .then(() => {
                    this.notification.add(_t("Verification URL copied to clipboard"), { type: "success" });
                })
                .catch(() => {
                    // Fallback for older browsers
                    const textArea = document.createElement("textarea");
                    textArea.value = this.state.verificationUrl;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand("copy");
                    document.body.removeChild(textArea);

                    this.notification.add(_t("Verification URL copied to clipboard"), { type: "success" });
                });
        } catch (error) {
            console.error("Error copying URL:", error);
            this.notification.add(_t("Failed to copy URL"), { type: "danger" });
        }
    }

    openQRModal() {
        this.state.showModal = true;
    }

    closeQRModal() {
        this.state.showModal = false;
    }

    openVerificationPage() {
        if (!this.state.verificationUrl) {
            this.notification.add(_t("No verification URL available"), { type: "warning" });
            return;
        }

        window.open(this.state.verificationUrl, "_blank");
    }

    async testVerification() {
        if (!this.props.record.data.verification_token) {
            this.notification.add(_t("No verification token available"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;

        try {
            // Test verification endpoint
            const response = await fetch(`/payment/verify/api/${this.props.record.data.verification_token}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({}),
            });

            const result = await response.json();

            if (result.success) {
                this.notification.add(_t("QR verification test successful"), { type: "success" });

                // Reload verification stats
                await this.loadVerificationStats(this.props.record.data.verification_token);
            } else {
                this.notification.add(_t("QR verification test failed: %s", result.message), { type: "danger" });
            }
        } catch (error) {
            console.error("Error testing verification:", error);
            this.notification.add(_t("QR verification test failed"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    _getQRSize() {
        return this.props.size || 200;
    }

    _formatVerificationCount() {
        if (!this.state.verificationStats) return _t("No data");

        const count = this.state.verificationStats.verification_count || 0;
        return count === 1 ? _t("1 verification") : _t("%s verifications", count);
    }

    _formatLastVerification() {
        if (!this.state.verificationStats || !this.state.verificationStats.last_verification) {
            return _t("Never verified");
        }

        const date = new Date(this.state.verificationStats.last_verification);
        return _t("Last verified: %s", date.toLocaleString());
    }

    _getStatusClass() {
        const state = this.props.record.data.approval_state;
        const statusClasses = {
            draft: "text-secondary",
            submitted: "text-info",
            under_review: "text-warning",
            approved: "text-success",
            authorized: "text-primary",
            posted: "text-success",
            rejected: "text-danger",
            cancelled: "text-secondary",
        };
        return statusClasses[state] || "text-muted";
    }

    _canRegenerate() {
        // Only allow regeneration for certain states and if user has permission
        const allowedStates = ["draft", "submitted"];
        const currentState = this.props.record.data.approval_state;
        return allowedStates.includes(currentState);
    }
}

registry.category("fields").add("qr_code", QRCodeWidget);
