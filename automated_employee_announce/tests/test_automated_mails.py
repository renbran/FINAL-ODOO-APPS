from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TestAutomatedEmployeeAnnounce(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, mail_notify_force_send=True))
        self.hr_employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'work_email': 'test.employee@example.com',
            'birthday': date.today(),
            'hire_date': date.today() - timedelta(days=365),
        })
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.buyer = self.env['res.partner'].create({'name': 'Test Buyer'})
        self.project = self.env['project.project'].create({'name': 'Test Project'})
        self.unit = self.env['product.product'].create({'name': 'Test Unit'})
        self.agent = self.env['res.partner'].create({'name': 'Agent 1', 'email': 'agent1@example.com'})
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'buyer_id': self.buyer.id if hasattr(self.env['sale.order'], 'buyer_id') else False,
            'project_id': self.project.id if hasattr(self.env['sale.order'], 'project_id') else False,
            'unit_id': self.unit.id if hasattr(self.env['sale.order'], 'unit_id') else False,
            'price_unit': 100000,
            'agent1_partner_id': self.agent.id,
            'booking_date': date.today() - timedelta(days=31),
        })

    def test_birthday_announcement_mail(self):
        rule = self.env['automated.mail.rule'].create({
            'name': 'Birthday Rule',
            'model_id': self.env['ir.model']._get_id('hr.employee'),
            'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_birthday').id,
            'rule_type': 'birthday',
        })
        rule.run_rule()
        # Check mail sent in mail.message
        messages = self.hr_employee.message_ids.filtered(lambda m: 'birthday' in (m.subject or '').lower())
        self.assertTrue(messages, 'Birthday announcement mail not sent!')

    def test_saleorder_invoiced_mail(self):
        # Simulate invoice creation
        self.sale_order.state = 'sale'
        self.sale_order._create_invoices()
        messages = self.sale_order.message_ids.filtered(lambda m: 'invoiced' in (m.body or '').lower())
        self.assertTrue(messages, 'Sale order invoiced mail not sent!')

    def test_payment_initiated_mail(self):
        # Simulate payment on invoice
        self.sale_order.state = 'sale'
        invoice = self.sale_order._create_invoices()
        move = invoice and invoice[0] or False
        if move:
            move._message_post_after_payment(None, move)
            messages = self.sale_order.message_ids.filtered(lambda m: 'payment receipt' in (m.body or '').lower())
            self.assertTrue(messages, 'Payment initiated mail not sent!')

    def test_deal_status_reminder_mail(self):
        # Simulate cron job
        self.sale_order.state = 'draft'
        self.env['sale.order'].send_deal_status_reminders()
        messages = self.sale_order.message_ids.filtered(lambda m: 'deal status reminder' in (m.body or '').lower())
        self.assertTrue(messages, 'Deal status reminder mail not sent!')
