from odoo import api, models

class PropertySaleReport(models.AbstractModel):
    _name = 'report.property_sale_management.report_property_sale_ledger'
    _description = 'Property Sale Ledger Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['property.sale'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'property.sale',
            'docs': docs,
            'data': data,
            'get_payment_summary': self._get_payment_summary,
        }
    
    def _get_payment_summary(self, sale):
        """Helper method to calculate payment summary"""
        return {
            'total_paid': sum(line.capital_repayment 
                             for line in sale.property_sale_line_ids 
                             if line.collection_status == 'paid'),
            'total_due': sum(line.capital_repayment 
                            for line in sale.property_sale_line_ids 
                            if line.collection_status != 'paid'),
        }