from odoo import models, api

class PropertyOfferReport(models.AbstractModel):
    _name = 'report.property_sale_management.property_offer_report_template'
    _description = 'Property Offer Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['property.offer'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'property.offer',
            'docs': docs,
            'data': data,
        }