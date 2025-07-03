from odoo import api, fields, models
from .deal_fields_mixin import DealFieldsMixin

class AccountMove(models.Model):
    _inherit = ['account.move', 'deal.fields.mixin']

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    def _transfer_sale_order_fields(self, sale_order, vals):
        """Transfer custom fields from sale order to invoice"""
        if not sale_order:
            return vals
        
        # Defensive validation for Many2one fields
        deal_fields = {
            'booking_date': sale_order.booking_date,
            'developer_commission': sale_order.developer_commission,
            'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id and sale_order.buyer_id.exists() else False,
            'deal_id': sale_order.deal_id,
            'project_id': sale_order.project_id.id if sale_order.project_id and sale_order.project_id.exists() else False,
            'sale_value': sale_order.sale_value,
            'unit_id': sale_order.unit_id.id if sale_order.unit_id and sale_order.unit_id.exists() else False,
        }
        
        # Only include sale_order_type_id if the field exists on the sale order
        if hasattr(sale_order, 'sale_order_type_id') and sale_order.sale_order_type_id:
            try:
                if sale_order.sale_order_type_id.exists():
                    deal_fields['sale_order_type_id'] = sale_order.sale_order_type_id.id
            except Exception:
                # If any error occurs, skip this field
                pass
        
        # Only update vals if the field is not already set
        for field_name, field_value in deal_fields.items():
            if field_name not in vals:
                vals[field_name] = field_value
        
        return vals

    def _validate_many2one_fields(self, vals):
        """Validate and clean Many2one fields in vals"""
        cleaned_vals = vals.copy()
        
        for field_name, field in self._fields.items():
            if isinstance(field, fields.Many2one) and field_name in cleaned_vals:
                val = cleaned_vals[field_name]
                
                # Skip if value is falsy (False, None, 0, etc.)
                if not val:
                    continue
                
                try:
                    # Handle different value types
                    if isinstance(val, int):
                        # Integer ID - check if record exists
                        if val > 0 and self.env[field.comodel_name].browse(val).exists():
                            continue  # Valid ID
                        else:
                            cleaned_vals[field_name] = False
                    elif isinstance(val, models.BaseModel):
                        # Recordset or record object
                        if hasattr(val, 'exists') and val.exists():
                            # Valid recordset with existing records
                            if hasattr(val, 'id'):
                                cleaned_vals[field_name] = val.id
                            else:
                                # Multiple records, take the first one
                                cleaned_vals[field_name] = val.ids[0] if val.ids else False
                        else:
                            cleaned_vals[field_name] = False
                    else:
                        # Unknown object type or invalid format
                        cleaned_vals[field_name] = False
                        
                except Exception as e:
                    # If any error occurs during validation, set to False for safety
                    cleaned_vals[field_name] = False
        
        return cleaned_vals

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        cleaned_vals_list = []
        for vals in vals_list:
            # Clean and validate Many2one fields
            cleaned_vals = self._validate_many2one_fields(vals)
            
            # Transfer sale order custom fields if this is an invoice from a sale order
            if cleaned_vals.get('move_type') in ['out_invoice', 'out_refund'] and cleaned_vals.get('invoice_origin'):
                sale_order = self.env['sale.order'].search([
                    ('name', '=', cleaned_vals.get('invoice_origin'))
                ], limit=1)
                if sale_order:
                    cleaned_vals = self._transfer_sale_order_fields(sale_order, cleaned_vals)
            
            cleaned_vals_list.append(cleaned_vals)
        
        # Call super with cleaned values
        if len(cleaned_vals_list) == 1:
            return super(AccountMove, self).create(cleaned_vals_list[0])
        else:
            return super(AccountMove, self).create(cleaned_vals_list)

    def write(self, vals):
        """Override write to handle changes to invoice_origin"""
        # Clean Many2one fields in vals
        cleaned_vals = self._validate_many2one_fields(vals)
        
        result = super(AccountMove, self).write(cleaned_vals)
        
        # If invoice_origin is being set or changed, transfer sale order fields
        if 'invoice_origin' in cleaned_vals:
            for move in self:
                if move.move_type in ['out_invoice', 'out_refund'] and move.invoice_origin:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', move.invoice_origin)
                    ], limit=1)
                    if sale_order:
                        update_vals = {}
                        self._transfer_sale_order_fields(sale_order, update_vals)
                        if update_vals:
                            # Clean the update values as well
                            update_vals = self._validate_many2one_fields(update_vals)
                            super(AccountMove, move).write(update_vals)
        
        return result

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        """Hook into standard Odoo invoice creation from sale orders"""
        new_vals_list = []
        for vals in vals_list:
            if vals.get('invoice_origin'):
                sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
                if sale_order:
                    vals = self._transfer_sale_order_fields(sale_order, vals)
            new_vals_list.append(vals)
        return super(AccountMove, self)._move_autocomplete_invoice_lines_create(new_vals_list)

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        """Convert amount total to words"""
        for record in self:
            if record.amount_total:
                try:
                    # Try to use Odoo's built-in number to words conversion if available
                    from odoo.tools.misc import formatLang
                    from num2words import num2words
                    amount = record.amount_total
                    currency = record.currency_id.name or 'USD'
                    record.amount_total_words = num2words(amount, lang='en').title() + ' ' + currency
                except ImportError:
                    # Fallback if num2words is not available
                    record.amount_total_words = str(record.amount_total) + ' ' + (record.currency_id.name or 'USD')
            else:
                record.amount_total_words = ''