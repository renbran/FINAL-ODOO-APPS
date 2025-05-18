from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Commission Allocation'
    _order = 'position, id'

    broker_commission_id = fields.Many2one(
        'broker.commission.invoice',
        required=True,
        ondelete='cascade',
        string="Commission Reference"
    )
    position = fields.Selection([
        ('primary_agent', 'Primary Agent'),
        ('secondary_agent', 'Secondary Agent'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('other', 'Other')
    ], required=True, string="Role Position")
    
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string="Recipient",
        domain=[('is_company', '=', False)]
    )
    percentage = fields.Float(string="Percentage (%)", digits=(5, 2))

    amount = fields.Monetary(
        string="Calculated Amount",
        currency_field='currency_id',
        compute='_compute_amount',
        store=True,
        help="Automatically calculated based on commission percentage and total amount"
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='broker_commission_id.currency_id',
        readonly=True,
        string="Currency"
    )
    
    notes = fields.Text(string="Additional Notes")

    state = fields.Selection(
        related='broker_commission_id.state',
        string="Status",
        store=True
    )

    display_name = fields.Char(
        string="Reference",
        compute='_compute_display_name',
        store=True
    )

    # Vendor bill tracking
    bill_ids = fields.One2many('account.move', 'internal_commission_id', string="Vendor Bills", readonly=True)
    bill_count = fields.Integer(string="Bill Count", compute='_compute_bill_info', store=True)
    total_billed = fields.Monetary(string='Total Billed', compute='_compute_bill_info', store=True)
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_bill_info', store=True)
    bill_payment_progress = fields.Float(string='Payment Progress %', compute='_compute_bill_info', store=True)
    bill_payment_state = fields.Selection([
        ('not_billed', 'Not Billed'),
        ('to_pay', 'To Pay'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string='Bill Status', compute='_compute_bill_info', store=True)
    is_billed = fields.Boolean(string="Is Billed", compute='_compute_bill_info', store=True)

    @api.depends('percentage', 'broker_commission_id.commission_amount')
    def _compute_amount(self):
        for record in self:
            if record.percentage and record.broker_commission_id.commission_amount:
                record.amount = (record.broker_commission_id.commission_amount *
                                 (record.percentage / 100))
            else:
                record.amount = 0.0

    @api.depends('partner_id', 'position', 'broker_commission_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.partner_id and record.broker_commission_id:
                record.display_name = (
                    f"{record.broker_commission_id.name or 'New'} - "
                    f"{record.position or ''} - "
                    f"{record.partner_id.name or ''}"
                )
            else:
                record.display_name = "New Allocation"

    @api.depends('bill_ids.amount_total', 'bill_ids.amount_residual', 'bill_ids.state')
    def _compute_bill_info(self):
        for rec in self:
            rec.bill_count = len(rec.bill_ids)
            valid_bills = rec.bill_ids.filtered(lambda b: b.state != 'cancel')
            rec.is_billed = bool(valid_bills)

            total = sum(valid_bills.mapped('amount_total'))
            paid = sum(b.amount_total - b.amount_residual for b in valid_bills)

            rec.total_billed = total
            rec.total_paid = paid
            rec.bill_payment_progress = (paid / total) * 100 if total else 0.0

            if not valid_bills:
                rec.bill_payment_state = 'not_billed'
            elif all(b.payment_state == 'paid' for b in valid_bills):
                rec.bill_payment_state = 'paid'
            elif any(b.payment_state == 'partial' for b in valid_bills):
                rec.bill_payment_state = 'partial'
            else:
                rec.bill_payment_state = 'to_pay'

    def action_view_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bills'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.bill_ids.ids)],
            'context': {'create': False},
        }

    def action_view_broker_commission(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Broker Commission'),
            'res_model': 'broker.commission.invoice',
            'view_mode': 'form',
            'res_id': self.broker_commission_id.id,
            'target': 'current',
        }

    def action_generate_vendor_bill(self):
        self.ensure_one()

        if self.is_billed:
            raise UserError(_("A vendor bill has already been created for this commission allocation."))

        if not self.partner_id:
            raise UserError(_("Please specify a recipient first."))

        if self.broker_commission_id.state not in ['confirmed', 'invoiced', 'paid']:
            raise UserError(_("Commission must be confirmed before generating vendor bills."))

        property_id = self.broker_commission_id.property_sale_id.property_id
        expense_account = property_id.expense_account_id or self.env['account.account'].search(
            [('user_type_id.type', '=', 'expense')], limit=1)

        if not expense_account:
            raise UserError(_("Please configure an expense account for commissions."))

        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'name': f"Commission for {self.position} - {self.broker_commission_id.property_sale_id.name}",
                'quantity': 1,
                'price_unit': self.amount,
                'account_id': expense_account.id,
            })],
            'internal_commission_id': self.id,
            'broker_commission_id': self.broker_commission_id.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'target': 'current',
        }
