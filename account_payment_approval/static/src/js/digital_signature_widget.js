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
            showModal: false,
        });

        onMounted(this.initializeCanvas);
    }

    initializeCanvas() {
        if (!this.canvasRef.el || this.props.readonly) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext('2d');
        
        // Set canvas size for high DPI displays
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        
        ctx.scale(dpr, dpr);
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        
        // Set drawing styles
        ctx.strokeStyle = '#2c3e50';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add event listeners
        this.addEventListeners(canvas);
    }

    addEventListeners(canvas) {
        // Mouse events
        canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        canvas.addEventListener('mousemove', this.draw.bind(this));
        canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        canvas.addEventListener('mouseout', this.stopDrawing.bind(this));

        // Touch events for mobile
        canvas.addEventListener('touchstart', this.handleTouch.bind(this));
        canvas.addEventListener('touchmove', this.handleTouch.bind(this));
        canvas.addEventListener('touchend', this.stopDrawing.bind(this));
    }

    startDrawing(event) {
        if (this.props.readonly) return;
        
        this.state.isDrawing = true;
        const rect = this.canvasRef.el.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const ctx = this.canvasRef.el.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    draw(event) {
        if (!this.state.isDrawing || this.props.readonly) return;
        
        const rect = this.canvasRef.el.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const ctx = this.canvasRef.el.getContext('2d');
        ctx.lineTo(x, y);
        ctx.stroke();
        
        this.state.hasSignature = true;
    }

    stopDrawing() {
        this.state.isDrawing = false;
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
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        this.state.hasSignature = false;
        this.state.signatureData = null;
    }

    async saveSignature() {
        if (!this.state.hasSignature || this.props.readonly) {
            this.notification.add(_t("Please draw your signature first"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        
        try {
            // Convert canvas to base64 data URL
            const canvas = this.canvasRef.el;
            const signatureData = canvas.toDataURL('image/png');
            
            // Get current user info for signature
            const userInfo = {
                user_name: this.env.services.user.name,
                user_id: this.env.services.user.userId,
                signature_date: new Date().toISOString(),
                signature_type: this.props.signature_type || 'generic',
            };

            // Save signature to record
            const signatureField = this._getSignatureField();
            const dateField = this._getSignatureDateField();
            
            if (signatureField && dateField) {
                await this.orm.write(
                    this.props.record.resModel,
                    [this.props.record.resId],
                    {
                        [signatureField]: signatureData.split(',')[1], // Remove data:image/png;base64, prefix
                        [dateField]: userInfo.signature_date,
                    }
                );

                this.notification.add(_t("Signature saved successfully"), { type: "success" });
                this.state.showModal = false;
                
                // Trigger record reload if needed
                if (this.props.record.model && this.props.record.model.load) {
                    await this.props.record.model.load();
                }
            }

        } catch (error) {
            console.error("Error saving signature:", error);
            this.notification.add(
                _t("Failed to save signature: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    openSignatureModal() {
        if (this.props.readonly) return;
        this.state.showModal = true;
        
        // Initialize canvas after modal is shown
        setTimeout(() => {
            this.initializeCanvas();
        }, 100);
    }

    closeSignatureModal() {
        this.state.showModal = false;
        this.clearSignature();
    }

    _getSignatureField() {
        const typeMapping = {
            'creator': 'creator_signature',
            'reviewer': 'reviewer_signature',
            'approver': 'approver_signature',
            'authorizer': 'authorizer_signature',
        };
        return typeMapping[this.props.signature_type] || this.props.name;
    }

    _getSignatureDateField() {
        const typeMapping = {
            'creator': 'creator_signature_date',
            'reviewer': 'reviewer_signature_date',
            'approver': 'approver_signature_date',
            'authorizer': 'authorizer_signature_date',
        };
        return typeMapping[this.props.signature_type] || `${this.props.name}_date`;
    }

    _hasExistingSignature() {
        const dateField = this._getSignatureDateField();
        return !!(this.props.record.data[dateField]);
    }

    _getSignatureDisplayText() {
        if (this._hasExistingSignature()) {
            const dateField = this._getSignatureDateField();
            const signatureDate = this.props.record.data[dateField];
            if (signatureDate) {
                const date = new Date(signatureDate);
                return _t("Signed on %s", date.toLocaleString());
            }
            return _t("Signature captured");
        }
        return this.props.placeholder || _t("Click to sign");
    }

    _getButtonClass() {
        if (this._hasExistingSignature()) {
            return "btn btn-success btn-sm";
        }
        return this.props.readonly ? "btn btn-secondary btn-sm" : "btn btn-primary btn-sm";
    }

    _getButtonIcon() {
        if (this._hasExistingSignature()) {
            return "fa fa-check-circle";
        }
        return "fa fa-pencil";
    }
}

registry.category("fields").add("digital_signature", DigitalSignatureWidget);
