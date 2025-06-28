# -*- coding: utf-8 -*-

from odoo import models

class CommissionReport(models.AbstractModel):
    _name = 'report.commission_fields.commission_report'
    _description = 'Commission Report'
    
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }
