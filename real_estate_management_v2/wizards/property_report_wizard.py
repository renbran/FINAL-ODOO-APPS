from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PropertyReportWizard(models.TransientModel):
    _name = 'property.report.wizard'
    _description = 'Property Report Wizard'

    property_id = fields.Many2one(
        'property.property',
        string='Property',
        required=True
    )
    
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report')
    ], string='Report Type', default='summary', required=True)
    
    include_financial = fields.Boolean(
        string='Include Financial Details',
        default=True
    )
    
    include_commission = fields.Boolean(
        string='Include Commission Details',
        default=True
    )
    
    date_from = fields.Date(
        string='From Date'
    )
    
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today
    )

    def action_generate_report(self):
        self.ensure_one()
        
        # Validate date range
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("End date cannot be before start date."))
        
        # Prepare report data
        report_data = {
            'property_id': self.property_id.id,
            'report_type': self.report_type,
            'include_financial': self.include_financial,
            'include_commission': self.include_commission,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        
        # Return report action
        return {
            'type': 'ir.actions.report',
            'report_name': 'real_estate_management_v2.report_property',
            'report_type': 'qweb-pdf',
            'data': report_data,
            'context': self.env.context,
        }