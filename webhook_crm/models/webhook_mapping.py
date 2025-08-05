# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import json
import requests

_logger = logging.getLogger(__name__)


class WebhookMapping(models.Model):
    _name = 'webhook.mapping'
    _description = 'Webhook Field Mapping Configuration'
    _order = 'name, sequence'

    name = fields.Char(
        string='Mapping Name',
        required=True,
        help="Name for this webhook mapping configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering mappings"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this mapping is active"
    )
    
    source_name = fields.Char(
        string='Source Name',
        required=True,
        help="Source identifier for the webhook (e.g., 'facebook', 'google')"
    )
    
    target_model = fields.Char(
        string='Target Model',
        default='crm.lead',
        required=True,
        help="Odoo model to create records in"
    )
    
    description = fields.Text(
        string='Description',
        help="Description of this webhook mapping"
    )
    
    field_mapping_ids = fields.One2many(
        'webhook.field.mapping',
        'webhook_mapping_id',
        string='Field Mappings',
        help="Field mapping configurations"
    )
    
    default_values = fields.Text(
        string='Default Values (JSON)',
        help="Default values to set on created records (JSON format)"
    )
    
    transformation_rules = fields.Text(
        string='Transformation Rules (JSON)',
        help="Data transformation rules (JSON format)"
    )
    
    @api.constrains('default_values')
    def _check_default_values_json(self):
        """Validate that default_values is valid JSON"""
        for record in self:
            if record.default_values:
                try:
                    json.loads(record.default_values)
                except json.JSONDecodeError:
                    raise ValidationError(_("Default Values must be valid JSON format"))
    
    @api.constrains('transformation_rules')
    def _check_transformation_rules_json(self):
        """Validate that transformation_rules is valid JSON"""
        for record in self:
            if record.transformation_rules:
                try:
                    json.loads(record.transformation_rules)
                except json.JSONDecodeError:
                    raise ValidationError(_("Transformation Rules must be valid JSON format"))
    
    def get_default_values_dict(self):
        """Parse default values JSON to dictionary"""
        self.ensure_one()
        if self.default_values:
            try:
                return json.loads(self.default_values)
            except json.JSONDecodeError:
                _logger.warning("Invalid JSON in default_values for mapping %s", self.name)
        return {}
    
    def get_transformation_rules_dict(self):
        """Parse transformation rules JSON to dictionary"""
        self.ensure_one()
        if self.transformation_rules:
            try:
                return json.loads(self.transformation_rules)
            except json.JSONDecodeError:
                _logger.warning("Invalid JSON in transformation_rules for mapping %s", self.name)
        return {}
    
    def transform_webhook_data(self, webhook_data):
        """Transform webhook data according to mapping configuration"""
        self.ensure_one()
        
        if not webhook_data:
            return {}
        
        transformed_data = {}
        
        # Apply field mappings
        for field_mapping in self.field_mapping_ids:
            if field_mapping.source_field in webhook_data:
                source_value = webhook_data[field_mapping.source_field]
                transformed_value = field_mapping.transform_value(source_value)
                if transformed_value is not None:
                    transformed_data[field_mapping.target_field] = transformed_value
        
        # Apply default values
        default_values = self.get_default_values_dict()
        for field_name, default_value in default_values.items():
            if field_name not in transformed_data:
                transformed_data[field_name] = default_value
        
        # Apply transformation rules
        transformation_rules = self.get_transformation_rules_dict()
        if transformation_rules:
            # Apply custom transformation logic here
            # This could be extended based on specific needs
            pass
        
        return transformed_data


class WebhookFieldMapping(models.Model):
    _name = 'webhook.field.mapping'
    _description = 'Webhook Field Mapping'
    _order = 'webhook_mapping_id, sequence, source_field'

    webhook_mapping_id = fields.Many2one(
        'webhook.mapping',
        string='Webhook Mapping',
        required=True,
        ondelete='cascade',
        help="Parent webhook mapping configuration"
    )
    
    mapping_id = fields.Many2one(
        'webhook.mapping',
        string='Mapping ID',
        required=True,
        ondelete='cascade',
        help="Parent webhook mapping configuration (alias for compatibility)"
    )
    
    @api.model
    def create(self, vals):
        # Ensure mapping_id and webhook_mapping_id are synchronized
        if 'mapping_id' in vals and 'webhook_mapping_id' not in vals:
            vals['webhook_mapping_id'] = vals['mapping_id']
        elif 'webhook_mapping_id' in vals and 'mapping_id' not in vals:
            vals['mapping_id'] = vals['webhook_mapping_id']
        return super().create(vals)
    
    def write(self, vals):
        # Ensure mapping_id and webhook_mapping_id stay synchronized
        if 'mapping_id' in vals:
            vals['webhook_mapping_id'] = vals['mapping_id']
        elif 'webhook_mapping_id' in vals:
            vals['mapping_id'] = vals['webhook_mapping_id']
        return super().write(vals)
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering field mappings"
    )
    
    source_field = fields.Char(
        string='Source Field',
        required=True,
        help="Field name in the incoming webhook data"
    )
    
    target_field = fields.Char(
        string='Target Field',
        required=True,
        help="Target field name in the Odoo model"
    )
    
    field_type = fields.Selection([
        ('char', 'Text'),
        ('text', 'Long Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('selection', 'Selection'),
        ('many2one', 'Many2one'),
        ('many2many', 'Many2many'),
        ('one2many', 'One2many'),
    ], string='Field Type', default='char', help="Type of the target Odoo field")
    
    required = fields.Boolean(
        string='Required',
        default=False,
        help="Whether this field mapping is required"
    )
    
    default_value = fields.Char(
        string='Default Value',
        help="Default value if webhook field is missing or empty"
    )
    
    transformation_type = fields.Selection([
        ('none', 'None'),
        ('upper', 'Uppercase'),
        ('lower', 'Lowercase'),
        ('lowercase', 'Lowercase'),
        ('title', 'Title Case'),
        ('strip', 'Strip Whitespace'),
        ('email_normalize', 'Normalize Email'),
        ('phone_normalize', 'Normalize Phone'),
        ('custom', 'Custom Function'),
    ], string='Transformation Type', default='none', help="Data transformation to apply")
    
    custom_function = fields.Char(
        string='Custom Function',
        help="Name of custom transformation function (if transformation is 'custom')"
    )
    
    validation_regex = fields.Char(
        string='Validation Regex',
        help="Regular expression for validating the field value"
    )
    
    description = fields.Text(
        string='Description',
        help="Description of this field mapping"
    )
    
    def transform_value(self, value):
        """Transform a value according to the mapping configuration"""
        self.ensure_one()
        
        if value is None or value == '':
            if self.default_value:
                value = self.default_value
            elif self.required:
                raise ValidationError(_("Required field %s is missing") % self.source_field)
            else:
                return None
        
        # Apply transformations
        if self.transformation_type == 'upper':
            value = str(value).upper()
        elif self.transformation_type in ('lower', 'lowercase'):
            value = str(value).lower()
        elif self.transformation_type == 'title':
            value = str(value).title()
        elif self.transformation_type == 'strip':
            value = str(value).strip()
        elif self.transformation_type == 'email_normalize':
            value = str(value).lower().strip()
        elif self.transformation_type == 'phone_normalize':
            # Basic phone normalization - remove common separators
            value = str(value).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        elif self.transformation_type == 'custom' and self.custom_function:
            # This could be extended to call custom transformation functions
            _logger.info("Custom transformation function %s not implemented", self.custom_function)
        
        # Validate with regex if provided
        if self.validation_regex:
            import re
            if not re.match(self.validation_regex, str(value)):
                raise ValidationError(_("Value %s does not match validation pattern for field %s") % (value, self.source_field))
        
        # Type conversion
        if self.field_type == 'integer':
            try:
                value = int(float(value))  # Convert via float to handle "123.0" strings
            except (ValueError, TypeError):
                if self.required:
                    raise ValidationError(_("Cannot convert %s to integer for field %s") % (value, self.source_field))
                return None
        elif self.field_type == 'float':
            try:
                value = float(value)
            except (ValueError, TypeError):
                if self.required:
                    raise ValidationError(_("Cannot convert %s to float for field %s") % (value, self.source_field))
                return None
        elif self.field_type == 'boolean':
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')
            else:
                value = bool(value)
        
        return value