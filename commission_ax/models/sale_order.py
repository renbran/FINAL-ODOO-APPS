from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CommissionGroup(models.Model):
    _name = 'commission.group'
    _description = 'Commission Group'

    # [Previous field definitions remain the same...]

    @api.constrains(
        'consultant_percentage', 'consultant_fixed_amount',
        'second_agent_percentage', 'second_agent_fixed_amount',
        'manager_percentage', 'manager_fixed_amount',
        'director_percentage', 'director_fixed_amount',
        'sale_value', 'amount_untaxed'
    )
    def _check_commission_allocations(self):
        for record in self:
            if not record.sale_value or not record.amount_untaxed:
                continue
            
            total_allocated = 0.0
            
            # Calculate consultant allocation
            if record.consultant_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.consultant_percentage / 100)
            elif record.consultant_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.consultant_percentage / 100)
            else:
                total_allocated += record.consultant_fixed_amount
            
            # Calculate second agent allocation
            if record.second_agent_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.second_agent_percentage / 100)
            elif record.second_agent_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.second_agent_percentage / 100)
            else:
                total_allocated += record.second_agent_fixed_amount
            
            # Calculate manager allocation
            if record.manager_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.manager_percentage / 100)
            elif record.manager_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.manager_percentage / 100)
            else:
                total_allocated += record.manager_fixed_amount
            
            # Calculate director allocation
            if record.director_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.director_percentage / 100)
            elif record.director_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.director_percentage / 100)
            else:
                total_allocated += record.director_fixed_amount
            
            # Check against untaxed amount
            if total_allocated > record.amount_untaxed:
                raise ValidationError(_(
                    "Total commission allocations (%.2f) cannot exceed the untaxed amount (%.2f)!"
                ) % (total_allocated, record.amount_untaxed))

    @api.onchange(
        'consultant_calculation_type', 'consultant_percentage', 'consultant_fixed_amount',
        'second_agent_calculation_type', 'second_agent_percentage', 'second_agent_fixed_amount',
        'manager_calculation_type', 'manager_percentage', 'manager_fixed_amount',
        'director_calculation_type', 'director_percentage', 'director_fixed_amount'
    )
    def _onchange_commission_values(self):
        """Warn user when allocations approach the limit"""
        for record in self:
            if not record.sale_value or not record.amount_untaxed:
                continue
            
            # Calculate current total allocation
            total_allocated = 0.0
            
            if record.consultant_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.consultant_percentage / 100)
            elif record.consultant_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.consultant_percentage / 100)
            else:
                total_allocated += record.consultant_fixed_amount
            
            if record.second_agent_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.second_agent_percentage / 100)
            elif record.second_agent_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.second_agent_percentage / 100)
            else:
                total_allocated += record.second_agent_fixed_amount
            
            if record.manager_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.manager_percentage / 100)
            elif record.manager_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.manager_percentage / 100)
            else:
                total_allocated += record.manager_fixed_amount
            
            if record.director_calculation_type == 'sales_value':
                total_allocated += record.sale_value * (record.director_percentage / 100)
            elif record.director_calculation_type == 'untaxed':
                total_allocated += record.amount_untaxed * (record.director_percentage / 100)
            else:
                total_allocated += record.director_fixed_amount
            
            # Calculate remaining available amount
            remaining = record.amount_untaxed - total_allocated
            
            # Show warning if allocations exceed 90% of available amount
            if total_allocated > 0 and remaining < (0.1 * record.amount_untaxed):
                return {
                    'warning': {
                        'title': _("Allocation Warning"),
                        'message': _(
                            "You have allocated %.2f of %.2f available (%.2f remaining). "
                            "Total allocations cannot exceed the untaxed amount!"
                        ) % (total_allocated, record.amount_untaxed, remaining)
                    }
                }