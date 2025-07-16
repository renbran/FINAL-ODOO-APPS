/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useRef } from "@odoo/owl";

class GeneralLedgerController extends Component {
    setup() {
        this.actionService = useService("action");
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.formRef = useRef("form");
    }

    async onClickGenerateReport(ev) {
        const formData = new FormData(this.formRef.el);
        const data = Object.fromEntries(formData.entries());
        
        try {
            const options = {
                date_from: data.date_from,
                date_to: data.date_to,
                journal_ids: data.journal_ids ? data.journal_ids.split(",").map(Number) : [],
                target_move: data.target_move || "posted",
                company_id: parseInt(data.company_id) || this.env.session.user_context.allowed_company_ids[0],
                account_ids: data.account_ids ? data.account_ids.split(",").map(Number) : [],
                sortby: data.sortby || "sort_date",
                initial_balance: data.initial_balance === "on",
                display_account: data.display_account || "all",
            };

            await download({
                url: "/dynamic_reports/dynamic_reports_report",
                data: {
                    report_id: "general_ledger",
                    options: JSON.stringify(options),
                },
            });
        } catch (error) {
            this.notification.add(error.message, { type: "danger" });
        }
    }
}

GeneralLedgerController.template = "om_dynamic_reports.GeneralLedgerView";
GeneralLedgerController.props = {};

registry.category("actions").add("om_dynamic_reports.general_ledger_action", GeneralLedgerController);
