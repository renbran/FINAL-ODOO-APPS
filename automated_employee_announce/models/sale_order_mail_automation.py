from odoo import models, api
from datetime import date, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super().create(vals)
        return order

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Override to send agent notification after invoice creation.
        """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for order in self:
            if order.agent1_partner_id and order.state in ('sale', 'done'):
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_invoiced_agent1', raise_if_not_found=False)
                if template:
                    template.send_mail(order.id, force_send=True)
                    order.message_post(body="Automated: Invoiced notification email sent to agent1_partner_id.")
        return invoices

    @api.model
    def send_deal_status_reminders(self):
        """
        Send reminder to agent1_partner_id for deals not invoiced after 30 days from booking_date.
        """
        today = date.today()
        domain = [
            ('booking_date', '!=', False),
            ('state', 'not in', ['sale', 'done', 'cancel']),
            ('agent1_partner_id', '!=', False),
        ]
        orders = self.search(domain)
        for order in orders:
            if order.booking_date and (today - order.booking_date).days >= 30:
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_deal_status_reminder_agent1', raise_if_not_found=False)
                if template:
                    template.send_mail(order.id, force_send=True)
                    order.message_post(body="Automated: Deal status reminder email sent to agent1_partner_id.")


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _message_post_after_payment(self, payment, move):
        # Call super if it exists (Odoo 17+)
        res = super()._message_post_after_payment(payment, move) if hasattr(super(), '_message_post_after_payment') else None
        # Automated notification to agent1_partner_id on payment receipt
        if move and move.move_type == 'out_invoice' and move.invoice_origin:
            sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
            if sale_order and sale_order.agent1_partner_id:
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_payment_initiated_agent1', raise_if_not_found=False)
                if template:
                    template.send_mail(sale_order.id, force_send=True)
                    sale_order.message_post(body="Automated: Payment receipt notification email sent to agent1_partner_id.")
        return res
