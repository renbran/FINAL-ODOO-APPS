/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class DigitalSignatureWidget extends Component {
    static template = "account_payment_approval.DigitalSignatureWidget";
    static props = { ...standardFieldProps };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            isDrawing: false,
            hasSignature: false,
            signatureData: null,
            penColor: "#000000",
            penWidth: 2,
            isReadonly: this.props.readonly || false;
});

        this.canvasRef = useRef("signatureCanvas");
        this.lastX = 0;
        this.lastY = 0;
        this.paths = [];

        onMounted(() => {
            this.setupCanvas();
            this.loadExistingSignature();
        });

        onWillUnmount(() => {
            this.cleanup();
        });
    }

    setupCanvas() {
        const canvas = this.canvasRef.el;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.strokeStyle = this.state.penColor;
        ctx.lineWidth = this.state.penWidth;

        // Set canvas dimensions
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';

        // Event listeners for drawing
        if (!this.state.isReadonly) {
            canvas.addEventListener('mousedown', this.startDrawing.bind(this));
            canvas.addEventListener('mousemove', this.draw.bind(this));
            canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
            canvas.addEventListener('mouseout', this.stopDrawing.bind(this));

            // Touch events for mobile
            canvas.addEventListener('touchstart', this.startDrawingTouch.bind(this));
            canvas.addEventListener('touchmove', this.drawTouch.bind(this));
            canvas.addEventListener('touchend', this.stopDrawing.bind(this));
        }
    }

    loadExistingSignature() {
        const signatureData = this.props.record.data[this.props.name];
        if (signatureData) {
            this.state.hasSignature = true;
            this.state.signatureData = signatureData;
            this.displaySignature(signatureData);
        }
    }

    displaySignature(data) {
        const canvas = this.canvasRef.el;
        if (!canvas || !data) return;

        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width / window.devicePixelRatio, canvas.height / window.devicePixelRatio);
        };
        img.src = `data:image/png;base64,${data}`;
    }

    getMousePos(e) {
        const canvas = this.canvasRef.el;
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top;
        };
    }

    getTouchPos(e) {
        const canvas = this.canvasRef.el;
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top;
        };
    }

    startDrawing(e) {
        if (this.state.isReadonly) return;
        
        this.state.isDrawing = true;
        const pos = this.getMousePos(e);
        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    startDrawingTouch(e) {
        e.preventDefault();
        if (this.state.isReadonly) return;
        
        this.state.isDrawing = true;
        const pos = this.getTouchPos(e);
        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    draw(e) {
        if (!this.state.isDrawing || this.state.isReadonly) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        const pos = this.getMousePos(e);

        ctx.beginPath();
        ctx.moveTo(this.lastX, this.lastY);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();

        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    drawTouch(e) {
        e.preventDefault();
        if (!this.state.isDrawing || this.state.isReadonly) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        const pos = this.getTouchPos(e);

        ctx.beginPath();
        ctx.moveTo(this.lastX, this.lastY);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();

        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    stopDrawing() {
        if (this.state.isDrawing) {
            this.state.isDrawing = false;
            this.state.hasSignature = true;
            this.saveSignature();
        }
    }

    saveSignature() {
        const canvas = this.canvasRef.el;
        if (!canvas) return;

        try {
            const dataURL = canvas.toDataURL('image/png');
            const base64Data = dataURL.split(',')[1];
            
            this.state.signatureData = base64Data;
            
            // Update the record
            this.props.record.update({
                [this.props.name]: base64Data;
            });

            this.notification.add(_t("Signature saved successfully"), {
                type: "success";
});
        } catch (error) {
            this.notification.add(_t("Error saving signature: %s", error.message), {
                type: "danger";
});
        }
    }

    clearSignature() {
        if (this.state.isReadonly) return;

        const canvas = this.canvasRef.el;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        this.state.hasSignature = false;
        this.state.signatureData = null;
        
        // Update the record
        this.props.record.update({
            [this.props.name]: false;
        });

        this.notification.add(_t("Signature cleared"), {
            type: "info";
});
    }

    cleanup() {
        const canvas = this.canvasRef.el;
        if (canvas) {
            canvas.removeEventListener('mousedown', this.startDrawing);
            canvas.removeEventListener('mousemove', this.draw);
            canvas.removeEventListener('mouseup', this.stopDrawing);
            canvas.removeEventListener('mouseout', this.stopDrawing);
            canvas.removeEventListener('touchstart', this.startDrawingTouch);
            canvas.removeEventListener('touchmove', this.drawTouch);
            canvas.removeEventListener('touchend', this.stopDrawing);
        }
    }
}

registry.category("fields").add("digital_signature", DigitalSignatureWidget);
        ctx.strokeStyle = this.state.penColor;
        ctx.lineWidth = this.state.penWidth;

        // Mouse events
        canvas.addEventListener("mousedown", this.startDrawing.bind(this));
        canvas.addEventListener("mousemove", this.draw.bind(this));
        canvas.addEventListener("mouseup", this.stopDrawing.bind(this));
        canvas.addEventListener("mouseout", this.stopDrawing.bind(this));

        // Touch events for mobile
        canvas.addEventListener("touchstart", this.handleTouch.bind(this));
        canvas.addEventListener("touchmove", this.handleTouch.bind(this));
        canvas.addEventListener("touchend", this.stopDrawing.bind(this));
    }

    loadExistingSignature() {
        if (this.props.record.data[this.props.name]) {
            const canvas = this.canvasRef.el;
            const ctx = canvas.getContext("2d");
            const img = new Image();

            img.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                this.state.hasSignature = true;
                this.state.signatureData = this.props.record.data[this.props.name];
            };

            img.src = `data:image/png;base64,${this.props.record.data[this.props.name]}`;
        }
    }

    startDrawing(e) {
        this.state.isDrawing = true;
        [this.lastX, this.lastY] = this.getMousePos(e);
    }

    draw(e) {
        if (!this.state.isDrawing) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        const [currentX, currentY] = this.getMousePos(e);

        ctx.beginPath();
        ctx.moveTo(this.lastX, this.lastY);
        ctx.lineTo(currentX, currentY);
        ctx.stroke();

        [this.lastX, this.lastY] = [currentX, currentY];
        this.state.hasSignature = true;
    }

    stopDrawing() {
        this.state.isDrawing = false;
    }

    handleTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent(;
            e.type === "touchstart" ? "mousedown" : e.type === "touchmove" ? "mousemove" : "mouseup",
            {
                clientX: touch.clientX,
                clientY: touch.clientY;
}
        );

        this.canvasRef.el.dispatchEvent(mouseEvent);
    }

    getMousePos(e) {
        const canvas = this.canvasRef.el;
        const rect = canvas.getBoundingClientRect();
        return [e.clientX - rect.left, e.clientY - rect.top];
    }

    clearSignature() {
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        this.state.hasSignature = false;
        this.state.signatureData = null;

        // Update the record
        this.props.record.update({ [this.props.name]: false });
    }

    saveSignature() {
        if (!this.state.hasSignature) return;

        const canvas = this.canvasRef.el;
        const dataURL = canvas.toDataURL("image/png");
        const base64Data = dataURL.split(",")[1];

        this.state.signatureData = base64Data;

        // Update the record
        this.props.record.update({ [this.props.name]: base64Data });

        // Show success notification
        this.env.services.notification.add("Signature saved successfully!", {
            type: "success";
});
    }

    changePenColor(color) {
        this.state.penColor = color;
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        ctx.strokeStyle = color;
    }

    changePenWidth(width) {
        this.state.penWidth = width;
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        ctx.lineWidth = width;
    }

    cleanup() {
        // Clean up event listeners if needed
    }
}

registry.category("fields").add("digital_signature", DigitalSignatureWidget);

// static/src/js/qr_code_widget.js - QR CODE WIDGET FOR ODOO 17
/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

export class QRCodeWidget extends Component {
    static template = "account_payment_approval.QRCodeWidget";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({
            qrCodeData: null,
            verificationUrl: null,
            showScanner: false,
            scannerActive: false,
            verificationResult: null,
            loading: false;
});

        this.notification = useService("notification");
        this.rpc = useService("rpc");
        this.qrDisplayRef = useRef("qrDisplay");
        this.scannerVideoRef = useRef("scannerVideo");
        this.scannerCanvasRef = useRef("scannerCanvas");

        onMounted(() => {
            this.loadQRCode();
        });
    }

    async loadQRCode() {
        if (this.props.record.data.qr_code) {
            this.state.qrCodeData = `data:image/png;base64,${this.props.record.data.qr_code}`;
        }

        if (this.props.record.data.verification_url) {
            this.state.verificationUrl = this.props.record.data.verification_url;
        }
    }

    async refreshQR() {
        this.state.loading = true;

        try {
            await this.rpc("/web/dataset/call_kw", {
                model: "account.payment",
                method: "action_regenerate_qr_code",
                args: [this.props.record.resId],
                kwargs: {}
});

            // Reload the record to get updated QR code
            await this.props.record.load();
            await this.loadQRCode();

            this.notification.add("QR code regenerated successfully!", {
                type: "success";
});
        } catch (error) {
            this.notification.add("Failed to regenerate QR code", {
                type: "danger";
});
        } finally {
            this.state.loading = false;
        }
    }

    showQRCode() {
        this.state.showScanner = false;
    }

    async toggleScanner() {
        this.state.showScanner = !this.state.showScanner;

        if (this.state.showScanner) {
            await this.startCamera();
        } else {
            this.stopCamera();
        }
    }

    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" }
});

            const video = this.scannerVideoRef.el;
            video.srcObject = stream;
            this.state.scannerActive = true;

            // Start QR detection
            this.startQRDetection();
        } catch (error) {
            this.notification.add("Camera access denied or not available", {
                type: "warning";
});
        }
    }

    stopCamera() {
        const video = this.scannerVideoRef.el;
        if (video && video.srcObject) {
            const tracks = video.srcObject.getTracks();
            tracks.forEach((track) => track.stop());
            video.srcObject = null;
        }
        this.state.scannerActive = false;
    }

    startQRDetection() {
        // This would integrate with a QR detection library
        // For now, we'll use a simple interval to check for QR codes
        const detectInterval = setInterval(() => {
            if (!this.state.scannerActive) {
                clearInterval(detectInterval);
                return;
            }

            // QR detection logic would go here
            // For production, use libraries like jsQR or QuaggaJS
        }, 100);
    }

    async validateQRCode(qrData) {
        this.state.loading = true;

        try {
            const result = await this.rpc("/payment/qr/validate", {
                qr_data: qrData;
});

            this.state.verificationResult = result;

            if (result.success) {
                this.notification.add("Payment validated successfully!", {
                    type: "success";
});
                this.stopCamera();
                this.state.showScanner = false;
            } else {
                this.notification.add(result.message || "Validation failed", {
                    type: "danger";
});
            }
        } catch (error) {
            this.notification.add("Validation error occurred", {
                type: "danger";
});
        } finally {
            this.state.loading = false;
        }
    }

    downloadQR() {
        if (this.state.qrCodeData) {
            const link = document.createElement("a");
            link.download = `payment-qr-${this.props.record.data.voucher_number || "code"}.png`;
            link.href = this.state.qrCodeData;
            link.click();
        }
    }

    copyVerificationUrl() {
        if (this.state.verificationUrl) {
            navigator.clipboard.writeText(this.state.verificationUrl).then(() => {
                this.notification.add("Verification URL copied to clipboard!", {
                    type: "info";
});
            });
        }
    }
}

registry.category("fields").add("qr_code", QRCodeWidget);

// static/src/js/payment_approval_dashboard.js - DASHBOARD WIDGET
/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PaymentApprovalDashboard extends Component {
    static template = "account_payment_approval.PaymentApprovalDashboard";

    setup() {
        this.state = useState({
            stats: {
                pending_review: 0,
                pending_approval: 0,
                pending_authorization: 0,
                total_amount: 0;
},
            recentPayments: [],
            loading: true;
});

        this.rpc = useService("rpc");
        this.action = useService("action");

        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.rpc("/web/dataset/call_kw", {
                model: "account.payment",
                method: "get_approval_dashboard_data",
                args: [],
                kwargs: {}
});

            this.state.stats = data.stats;
            this.state.recentPayments = data.recent_payments;
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    openPaymentsList(state) {
        this.action.doAction({
            name: `Payments - ${state.replace("_", " ").toUpperCase()}`,
            type: "ir.actions.act_window",
            res_model: "account.payment",
            view_mode: "tree,form",
            domain: [["voucher_state", "=", state]],
            views: [
                [false, "list"],
                [false, "form"]
]
});
    }

    openPayment(paymentId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.payment",
            res_id: paymentId,
            view_mode: "form",
            views: [[false, "form"]]
});
    }
}

registry.category("actions").add("payment_approval_dashboard", PaymentApprovalDashboard);

