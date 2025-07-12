from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CommissionRule(models.Model):
    _name = 'commission.rule'
    _description = 'Commission Rule'
    _order = 'sequence'
    
    name = fields.Char(string="Rule Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    
    # Rule Type
    rule_type = fields.Selection([
        ('broker', 'Broker Commission'),
        ('internal', 'Internal Commission')
    ], string="Rule Type", required=True, default='broker')
    
    # Commission Calculation
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Commission Type", required=True, default='percentage')
    commission_percentage = fields.Float(string="Commission Percentage", digits=(5, 2))
    commission_amount = fields.Monetary(string="Fixed Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency", 
                                default=lambda self: self.env.company.currency_id)
    
    # Application Conditions
    min_property_value = fields.Float(string="Minimum Property Value")
    max_property_value = fields.Float(string="Maximum Property Value")
    property_type_ids = fields.Many2many('property.type', string="Property Types")
    broker_partner_ids = fields.Many2many('res.partner', string="Applicable Brokers",
                                       domain=[('is_company', '=', True)])
    user_ids = fields.Many2many('res.users', string="Applicable Sales Persons")
    
    _sql_constraints = [
        ('check_percentage', 'CHECK(commission_percentage > 0 AND commission_percentage <= 100)',
         'Commission percentage must be between 0 and 100.'),
        ('check_amount', 'CHECK(commission_amount >= 0)',
         'Fixed commission amount must be positive.')
    ]
    
    @api.constrains('min_property_value', 'max_property_value')
    def _check_property_value_range(self):
        """Ensure min value is less than max value"""
        for rule in self:
            if rule.min_property_value and rule.max_property_value:
                if rule.min_property_value >= rule.max_property_value:
                    raise ValidationError(_("Minimum property value must be less than maximum property value."))
    
    def name_get(self):
        """Override name_get to show rule type and percentage/amount"""
        result = []
        for rule in self:
            if rule.commission_type == 'percentage':
                name = f"{rule.name} ({rule.rule_type}: {rule.commission_percentage}%)"
            else:
                name = f"{rule.name} ({rule.rule_type}: {rule.currency_id.symbol}{rule.commission_amount})"
            result.append((rule.id, name))
        return result
    
    @api.model
    def find_applicable_rule(self, property_sale, rule_type):
        """Find applicable commission rule for a property sale"""
        domain = [
            ('active', '=', True),
            ('rule_type', '=', rule_type),
            ('company_id', '=', property_sale.company_id.id)
        ]
        
        # Add property value conditions
        property_value = property_sale.property_value
        domain += [
            '|', ('min_property_value', '=', 0), ('min_property_value', '<=', property_value),
            '|', ('max_property_value', '=', 0), ('max_property_value', '>=', property_value)
        ]
        
        # Add property type condition if applicable
        if property_sale.property_id.property_type_id:
            domain += [
                '|', ('property_type_ids', '=', False), 
                ('property_type_ids', 'in', property_sale.property_id.property_type_id.id)
            ]
        
        # Add broker/user specific conditions
        if rule_type == 'broker' and property_sale.seller_name:
            domain += [
                '|', ('broker_partner_ids', '=', False), 
                ('broker_partner_ids', 'in', property_sale.seller_name.id)
            ]
        
        if rule_type == 'internal' and property_sale.sales_person_id:
            domain += [
                '|', ('user_ids', '=', False), 
                ('user_ids', 'in', property_sale.sales_person_id.id)
            ]
        
        # Find the applicable rule (with lowest sequence number if multiple match)
        applicable_rule = self.search(domain, order='sequence', limit=1)
        return applicable_rule
