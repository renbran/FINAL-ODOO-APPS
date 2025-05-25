from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BrokerCommissionInvoice(models.Model):
    _name = 'broker.commission.invoice'
    _description = 'Broker Commission Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', default='New', readonly=True)
    property_sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, tracking=True)
    seller_id = fields.Many2one('res.partner', string='Broker', required=True, 
                            domain=[('is_company','=',True)], tracking=True)
    commission_percentage = fields.Float(string='Commission %', digits=(5,2), tracking=True)
    commission_amount = fields.Monetary(string='Commission Amount', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                related='property_sale_id.currency_id', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Commission Allocation Fields
    internal_commission_ids = fields.One2many('internal.commission', 'broker_commission_id', 
                                            string="Commission Allocations")
    total_allocated = fields.Monetary(string='Total Allocated', compute='_compute_allocation', store=True)
    company_share = fields.Monetary(string='Company Share', compute='_compute_allocation', store=True)
    internal_commission_count = fields.Integer(string="Allocations Count", compute='_compute_internal_commission_count', store=True)
    
    # Status Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Invoice Fields
    invoice_ids = fields.One2many('account.move', 'broker_commission_id', string="Invoices", 
                                readonly=True, domain=[('move_type', '=', 'out_invoice')])
    total_invoiced = fields.Monetary(string='Total Invoiced', compute='_compute_payment_info', store=True)
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_payment_info', store=True)
    payment_progress = fields.Float(string='Payment Progress %', compute='_compute_payment_info', store=True)
    payment_state = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string='Payment Status', compute='_compute_payment_info', store=True)
    
    # Vendor Bill Fields
    vendor_bill_ids = fields.One2many('account.move', 'broker_commission_id', string="Vendor Bills",
                                    readonly=True, domain=[('move_type', '=', 'in_invoice')])
    vendor_bill_count = fields.Integer(string="Bill Count", compute='_compute_vendor_bill_info', store=True)
    total_vendor_billed = fields.Monetary(string='Total Vendor Bills', compute='_compute_vendor_bill_info', store=True)
    total_vendor_paid = fields.Monetary(string='Total Paid to Vendors', compute='_compute_vendor_bill_info', store=True)
    vendor_payment_progress = fields.Float(string='Vendor Payment Progress %', compute='_compute_vendor_bill_info', store=True)
    vendor_bill_state = fields.Selection([
        ('not_billed', 'Not Billed'),
        ('partial', 'Partially Generated'),
        ('complete', 'All Generated')
    ], string='Billing Status', compute='_compute_vendor_bill_info', store=True)

    @api.depends('commission_amount', 'internal_commission_ids.amount')
    def _compute_allocation(self):
        for rec in self:
            allocated = sum(rec.internal_commission_ids.mapped('amount'))
            rec.total_allocated = allocated
            rec.company_share = rec.commission_amount - allocated

    @api.depends('internal_commission_ids')
    def _compute_internal_commission_count(self):
        for rec in self:
            rec.internal_commission_count = len(rec.internal_commission_ids)

    @api.depends('invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_payment_info(self):
        for rec in self:
            valid_invoices = rec.invoice_ids.filtered(lambda i: i.state != 'cancel')
            total = sum(valid_invoices.mapped('amount_total'))
            paid = sum(inv.amount_total - inv.amount_residual for inv in valid_invoices)
            
            rec.total_invoiced = total
            rec.total_paid = paid
            rec.payment_progress = (paid / total) * 100 if total else 0
            
            if not valid_invoices:
                rec.payment_state = 'not_invoiced'
            elif all(inv.payment_state == 'paid' for inv in valid_invoices):
                rec.payment_state = 'paid'
                if rec.state == 'invoiced':  # Only update state if already invoiced
                    rec.state = 'paid'
            else:
                rec.payment_state = 'partial'

    @api.depends('payment_state')
    def _update_state_based_on_payment(self):
            for record in self:
                if record.payment_state == 'paid':
                    record.state = 'paid'
                elif record.payment_state == 'partial':
                    record.state = 'invoiced'   
    
    @api.depends('vendor_bill_ids.amount_total', 'vendor_bill_ids.amount_residual', 
                'internal_commission_ids.is_billed', 'internal_commission_ids')
    def _compute_vendor_bill_info(self):
        for rec in self:
            valid_bills = rec.vendor_bill_ids.filtered(lambda b: b.state != 'cancel')
            total = sum(valid_bills.mapped('amount_total'))
            paid = sum(bill.amount_total - bill.amount_residual for bill in valid_bills)
            
            rec.vendor_bill_count = len(valid_bills)
            rec.total_vendor_billed = total
            rec.total_vendor_paid = paid
            rec.vendor_payment_progress = (paid / total) * 100 if total else 0
            
            # Check if all internal commissions have been billed
            billed_allocations = len(rec.internal_commission_ids.filtered('is_billed'))
            total_allocations = len(rec.internal_commission_ids)
            
            if not total_allocations or not billed_allocations:
                rec.vendor_bill_state = 'not_billed'
            elif billed_allocations < total_allocations:
                rec.vendor_bill_state = 'partial'
            else:
                rec.vendor_bill_state = 'complete'

    def action_confirm(self):
        for record in self:
            if not record.internal_commission_ids:
                raise UserError(_("Please add commission allocations before confirming"))
            
            total_percentage = sum(record.internal_commission_ids.mapped('percentage'))
            if total_percentage > 100:
                raise UserError(_("Total allocated percentage cannot exceed 100%"))
                
            record.state = 'confirmed'
        return True
    
    def action_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.state = 'draft'
        else:
            raise UserError(_("Only cancelled commissions can be reset to draft"))
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state == 'invoiced':
                raise UserError(_("Cannot cancel an invoiced commission. Please create a credit note instead."))
            record.state = 'cancelled'
        return True

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'create': False},
        }
    
    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {'create': False},
        }
    
    def action_view_internal_commissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Allocations',
            'res_model': 'internal.commission',
            'view_mode': 'tree,form',
            'domain': [('broker_commission_id', '=', self.id)],
            'context': {'default_broker_commission_id': self.id},
        }

    def action_generate_broker_invoice(self):
        """Generate the actual customer invoice for broker commission"""
        self.ensure_one()
        if not self.seller_id:
            raise UserError(_("Please specify a broker first"))
        
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.seller_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'name': f"Broker Commission for {self.property_sale_id.name}",
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': self.property_sale_id.property_id.revenue_account_id.id,
            })],
            'broker_commission_id': self.id,
        })
        
        self.write({
            'state': 'invoiced',
            'invoice_ids': [(4, invoice.id)]
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_generate_all_vendor_bills(self):
        """Generate vendor bills for all allocations that don't have one yet"""
        self.ensure_one()
        
        if self.state not in ['confirmed', 'invoiced', 'paid']:
            raise UserError(_("Commission must be confirmed before generating vendor bills"))
        
        if not self.internal_commission_ids:
            raise UserError(_("No commission allocations to generate bills for"))
        
        unbilled_allocations = self.internal_commission_ids.filtered(lambda a: not a.is_billed)
        if not unbilled_allocations:
            raise UserError(_("All commission allocations already have vendor bills"))
        
        for allocation in unbilled_allocations:
            allocation.action_generate_vendor_bill()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {'create': False},
        }
        
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('broker.commission.invoice') or 'New'
        return super().create(vals)