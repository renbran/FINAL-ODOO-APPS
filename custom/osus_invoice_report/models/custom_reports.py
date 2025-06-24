from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        return self.env.ref('custom_reports.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        return self.env.ref('custom_reports.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        return self.env.ref('custom_reports.action_report_custom_receipt').report_action(self)