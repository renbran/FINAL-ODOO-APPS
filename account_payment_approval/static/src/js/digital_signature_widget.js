/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class DigitalSignatureWidget extends Component {
    static template = "account_payment_approval.DigitalSignatureWidget";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
        signature_type: { type: String, optional: true },
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.canvasRef = useRef("signatureCanvas");
        this.state = useState({
            isDrawing: false,
            hasSignature: false,
            isLoading: false,
            signatureData: null,
        });

        onMounted(this.initializeCanvas);
    }

    initializeCanvas() {
        if (!this.canvasRef.el || this.props.readonly) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = 400;
        canvas.height = 150;
        
        // Set drawing styles
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Add event listeners
        canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        canvas.addEventListener('mousemove', this.draw.bind(this));
        canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        canvas.addEventListener('mouseout', this.stopDrawing.bind(this));
        
        // Touch events for mobile
        canvas.addEventListener('touchstart', this.handleTouch.bind(this));
        canvas.addEventListener('touchmove', this.handleTouch.bind(this));
        canvas.addEventListener('touchend', this.stopDrawing.bind(this));

        // Load existing signature if available
        const signatureData = this.props.record.data[this.props.name];
        if (signatureData) {
            this.loadSignature(signatureData);
        }
    }

    startDrawing(event) {
        if (this.props.readonly) return;
        
        this.state.isDrawing = true;
        const canvas = this.canvasRef.el;
        const rect = canvas.getBoundingClientRect();
        const ctx = canvas.getContext('2d');
        
        ctx.beginPath();
        ctx.moveTo(
            event.clientX - rect.left,
            event.clientY - rect.top
        );
    }

    draw(event) {
        if (!this.state.isDrawing || this.props.readonly) return;
        
        const canvas = this.canvasRef.el;
        const rect = canvas.getBoundingClientRect();
        const ctx = canvas.getContext('2d');
        
        ctx.lineTo(
            event.clientX - rect.left,
            event.clientY - rect.top
        );
        ctx.stroke();
        
        this.state.hasSignature = true;
    }

    stopDrawing() {
        if (!this.state.isDrawing) return;
        
        this.state.isDrawing = false;
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext('2d');
        ctx.closePath();
        
        // Save signature data
        this.saveSignatureData();
    }

    handleTouch(event) {
        event.preventDefault();
        const touch = event.touches[0];
        const mouseEvent = new MouseEvent(event.type === 'touchstart' ? 'mousedown' : 
                                        event.type === 'touchmove' ? 'mousemove' : 'mouseup', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        
        this.canvasRef.el.dispatchEvent(mouseEvent);
    }

    clearSignature() {
        if (this.props.readonly) return;
        
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        this.state.hasSignature = false;
        this.state.signatureData = null;
        
        // Update record
        this.props.record.update({ [this.props.name]: false });
    }

    saveSignatureData() {
        if (!this.state.hasSignature || this.props.readonly) return;
        
        const canvas = this.canvasRef.el;
        const signatureData = canvas.toDataURL('image/png');
        
        this.state.signatureData = signatureData;
        
        // Update record with signature data
        this.props.record.update({ 
            [this.props.name]: signatureData 
        });
    }

    loadSignature(signatureData) {
        if (!signatureData) return;
        
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            this.state.hasSignature = true;
            this.state.signatureData = signatureData;
        };
        
        img.src = signatureData;
    }

    async saveToDatabase() {
        if (!this.state.hasSignature || this.props.readonly) {
            this.notification.add(_t("No signature to save"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        
        try {
            await this.orm.call(
                "account.payment",
                "save_digital_signature",
                [this.props.record.resId, this.state.signatureData, this.props.signature_type]
            );
            
            this.notification.add(_t("Signature saved successfully"), { type: "success" });
            
            // Trigger record update
            await this.props.record.save();
            
        } catch (error) {
            console.error("Error saving signature:", error);
            this.notification.add(
                _t("Failed to save signature: %s", error.message || error),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    get canSave() {
        return this.state.hasSignature && !this.props.readonly && !this.state.isLoading;
    }

    get placeholderText() {
        return this.props.placeholder || _t("Sign here");
    }
}

// Register the widget
registry.category("fields").add("digital_signature", DigitalSignatureWidget);
