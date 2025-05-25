from odoo import api, fields, models, _

class PropertyReportWizard(models.TransientModel):
    _name = 'property.report.wizard'
    _description = 'Property Report Wizard'
    
    property_id = fields.Many2one('property.property', string='Property', required=True)
    include_offers = fields.Boolean(string='Include Offers', default=True)
    include_sales = fields.Boolean(string='Include Sales', default=True)
    include_payment_details = fields.Boolean(string='Include Payment Details', default=True)
    
    def action_print_report(self):
        """Print the property report."""
        self.ensure_one()
        
        # Set context for report
        context = {
            'include_offers': self.include_offers,
            'include_sales': self.include_sales,
            'include_payment_details': self.include_payment_details,
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'real_estate_management_v2.report_property',
            'report_type': 'qweb-pdf',
            'res_id': self.property_id.id,
            'context': context,
        }