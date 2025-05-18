from odoo import api, fields, models

class DocLayout(models.Model):
    _inherit = 'doc.layout'
    
    invoice_layout = fields.Boolean(string="Use for Invoice Layout")
    layout_config_id = fields.Many2one('invoice.layout.config', string="Invoice Layout Configuration")
    
class InvoiceLayoutConfig(models.Model):
    _name = 'invoice.layout.config'
    _description = 'Invoice Layout Configuration'
    
    name = fields.Char(string="Name", required=True)
    header_color = fields.Char(string="Header Color", default="#8b0000")
    text_color = fields.Char(string="Text Color", default="#000000")
    show_qr_code = fields.Boolean(string="Show QR Code", default=True)
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    source = fields.Char(string="Source")
    invoice_layout_id = fields.Many2one('doc.layout', string="Invoice Layout", 
                                        domain=[('invoice_layout', '=', True)])
    
    @api.model
    def _prepare_invoice(self):
        """
        Override to transfer the additional fields to the invoice
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        invoice_vals.update({
            'source': self.source,
            'buyer_id': self.buyer_id.id if self.buyer_id else False,
            'project_id': self.project_id.id if self.project_id else False,
            'unit_id': self.unit_id if self.unit_id else False,
            'invoice_layout_id': self.invoice_layout_id.id if self.invoice_layout_id else False,
        })
        
        return invoice_vals
    
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    source = fields.Char(string="Source")
    buyer_id = fields.Many2one('res.partner', string="Buyer")
    project_id = fields.Many2one('project.project', string="Project")
    unit_id = fields.Char(string="Unit")
    invoice_layout_id = fields.Many2one('doc.layout', string="Invoice Layout", 
                                        domain=[('invoice_layout', '=', True)])
    
    @api.model
    def get_invoice_layout_template(self):
        """
        Return the template to be used based on the invoice layout
        """
        self.ensure_one()
        if self.invoice_layout_id:
            return 'custom_invoice_reports.custom_invoice_layout'
        return 'account.report_invoice_document'
    
    @api.model
    def _get_invoice_report_template(self):
        """
        Override to use custom template if specified
        """
        if self.invoice_layout_id:
            return self.env.ref('custom_invoice_reports.custom_invoice_layout')
        return super(AccountMove, self)._get_invoice_report_template()