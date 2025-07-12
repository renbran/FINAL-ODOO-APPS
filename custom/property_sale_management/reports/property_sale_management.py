from odoo import api, models

class PropertySaleReport(models.AbstractModel):
    _name = 'report.property_sale_management.property_sale_report_template'
    _description = 'Property Sale Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['property.sale'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'property.sale',
            'docs': docs,
            'data': data,
        }
