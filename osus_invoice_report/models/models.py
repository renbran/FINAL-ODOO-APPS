# -*- coding: utf-8 -*-
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_osus_invoice(self):
        return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)

    def action_print_osus_bill(self):
        return self.env.ref('osus_invoice_report.action_report_osus_bill').report_action(self)
