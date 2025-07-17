from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import date

_logger = logging.getLogger(__name__)

class AutomatedMailRule(models.Model):
    _name = 'automated.mail.rule'
    _description = 'Automated Mail Rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Rule name must be unique'),
    ]

    name = fields.Char(string='Rule Name', required=True, index=True, help="Name of the automated mail rule.")
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, help="Model to apply the rule on.")
    active = fields.Boolean(default=True, string='Active')
    mail_template_id = fields.Many2one('mail.template', string='Mail Template', required=True, ondelete='set null', help="Mail template to use.")
    rule_type = fields.Selection([
        ('birthday', 'Birthday'),
        ('work_anniversary', 'Work Anniversary'),
    ], string='Rule Type', required=True, help="Type of automated mail.")
    last_run = fields.Date(string='Last Run', readonly=True)

    def run_rule(self):
        """Run the automated mail rule for the selected type."""
        self.ensure_one()
        model = self.env[self.model_id.model]
        today = date.today()
        if self.rule_type == 'birthday':
            employees = model.search([('birthday', '!=', False)])
            for emp in employees:
                if emp.birthday and emp.birthday.month == today.month and emp.birthday.day == today.day:
                    self.mail_template_id.send_mail(emp.id, force_send=True)
                    emp.message_post(body="Automated: Birthday announcement email sent.")
        elif self.rule_type == 'work_anniversary':
            employees = model.search([('work_email', '!=', False), ('hire_date', '!=', False)])
            for emp in employees:
                if emp.hire_date and emp.hire_date.month == today.month and emp.hire_date.day == today.day:
                    self.mail_template_id.send_mail(emp.id, force_send=True)
                    emp.message_post(body="Automated: Work anniversary announcement email sent.")
        self.last_run = today

    @api.model
    def run_all_active_rules(self):
        rules = self.search([('active', '=', True)])
        for rule in rules:
            try:
                rule.run_rule()
            except Exception as e:
                _logger.error(f"AutomatedMailRule failed: {e}")
