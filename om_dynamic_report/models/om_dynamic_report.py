from odoo import models, fields, api

class OmDynamicReport(models.Model):
    _name = 'om.dynamic.report'
    _description = 'OM Dynamic Report'

    name = fields.Char(string="Report Name", required=True)
    report_type = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV')
    ], string="Report Type", required=True)
    model_id = fields.Many2one('ir.model', string="Model", required=True)
    filter_domain = fields.Char(string="Domain Filter")
    active = fields.Boolean(default=True)

    def generate_report(self):
        # Placeholder for dynamic report generation logic
        return True
