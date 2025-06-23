# -*- coding: utf-8 -*-
from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_osus_invoice(self):
        """Print OSUS custom invoice report"""
        return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)

    def action_print_osus_bill(self):
        """Print OSUS custom bill report"""
        return self.env.ref('osus_invoice_report.action_report_osus_bill').report_action(self)
    
    @api.model
    def _get_tax_amount_by_group(self):
        """Helper method to get tax amounts grouped by tax"""
        tax_lines = {}
        for line in self.line_ids.filtered(lambda l: l.tax_line_id):
            tax = line.tax_line_id
            if tax.id not in tax_lines:
                tax_lines[tax.id] = {
                    'tax': tax,
                    'amount': 0.0,
                    'base': 0.0
                }
            tax_lines[tax.id]['amount'] += line.balance
        return list(tax_lines.values())
    
    def _get_company_address(self):
        """Get formatted company address"""
        company = self.company_id
        address_parts = []
        if company.street:
            address_parts.append(company.street)
        if company.street2:
            address_parts.append(company.street2)
        if company.city:
            address_parts.append(company.city)
        if company.state_id:
            address_parts.append(company.state_id.name)
        if company.zip:
            address_parts.append(company.zip)
        if company.country_id:
            address_parts.append(company.country_id.name)
        return ', '.join(address_parts)