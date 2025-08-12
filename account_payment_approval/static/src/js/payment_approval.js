/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PaymentApprovalWidget extends Component {
    static template = "account_payment_approval.PaymentApprovalWidget";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            isLoading: false,
            progress: 0,
        });
    }
    
    async onApprove() {
        this.state.isLoading = true;
        try {
            await this.orm.call(
                "account.payment",
                "action_approve",
                [this.props.record.resId]
            );
            this.notification.add("Payment approved successfully", {
                type: "success",
            });
        } catch (error) {
            this.notification.add("Failed to approve payment", {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }
}

registry.category("fields").add("payment_approval", PaymentApprovalWidget);