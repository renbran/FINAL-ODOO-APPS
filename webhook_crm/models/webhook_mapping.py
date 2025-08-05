# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)

class WebhookMapping(models.Model):
    _name = 'webhook.mapping'
    _description = 'Webhook Field Mapping Configuration'

    name = fields.Char('Mapping Name', required=True)
    source_name = fields.Char('Source Name', required=True, help="Identifier for the webhook source")
    active = fields.Boolean('Active', default=True)
    field_mapping_ids = fields.One2many('webhook.field.mapping', 'mapping_id', string='Field Mappings')
    default_values = fields.Text('Default Values (JSON)', help="JSON object with default field values")
    transformation_rules = fields.Text('Transformation Rules (Python Code)', 
                                     help="Python code to transform webhook data")
    
    def process_webhook_data(self, webhook_data):
        """Process webhook data and return mapped values for CRM lead"""
        try:
            mapped_data = {}
            
            # Apply field mappings
            for mapping in self.field_mapping_ids:
                value = self._extract_value(webhook_data, mapping.source_field)
                if value is not None:
                    mapped_data[mapping.target_field] = self._transform_value(
                        value, mapping.transformation_type, mapping.transformation_params
                    )
            
            # Apply default values
            if self.default_values:
                try:
                    defaults = json.loads(self.default_values)
                    for key, value in defaults.items():
                        if key not in mapped_data:
                            mapped_data[key] = value
                except json.JSONDecodeError:
                    _logger.warning("Invalid JSON in default_values for mapping %s", self.name)
            
            # Apply transformation rules
            if self.transformation_rules:
                local_vars = {'webhook_data': webhook_data, 'mapped_data': mapped_data}
                try:
                    exec(self.transformation_rules, {}, local_vars)
                    mapped_data = local_vars.get('mapped_data', mapped_data)
                except Exception as e:
                    _logger.error("Error executing transformation rules: %s", str(e))
            
            return mapped_data
            
        except Exception as e:
            _logger.error("Error processing webhook data: %s", str(e))
            return {}
    
    def _extract_value(self, data, path):
        """Extract value from nested dictionary using dot notation"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                elif isinstance(value, list) and key.isdigit():
                    index = int(key)
                    value = value[index] if 0 <= index < len(value) else None
                else:
                    return None
            return value
        except (KeyError, IndexError, TypeError):
            return None
    
    def _transform_value(self, value, transformation_type, params):
        """Transform value based on transformation type"""
        if not transformation_type or transformation_type == 'none':
            return value
            
        try:
            if transformation_type == 'uppercase':
                return str(value).upper()
            elif transformation_type == 'lowercase':
                return str(value).lower()
            elif transformation_type == 'capitalize':
                return str(value).capitalize()
            elif transformation_type == 'strip':
                return str(value).strip()
            elif transformation_type == 'replace' and params:
                old, new = params.split('|', 1) if '|' in params else (params, '')
                return str(value).replace(old, new)
            elif transformation_type == 'mapping' and params:
                mapping_dict = json.loads(params)
                return mapping_dict.get(str(value), value)
            elif transformation_type == 'format' and params:
                return params.format(value=value)
            elif transformation_type == 'boolean':
                return value in ['true', 'True', '1', 1, True, 'yes', 'Yes']
            elif transformation_type == 'float':
                return float(value)
            elif transformation_type == 'int':
                return int(value)
        except Exception as e:
            _logger.warning("Error transforming value %s with type %s: %s", 
                          value, transformation_type, str(e))
        
        return value


class WebhookFieldMapping(models.Model):
    _name = 'webhook.field.mapping'
    _description = 'Webhook Field Mapping'

    mapping_id = fields.Many2one('webhook.mapping', string='Mapping', required=True, ondelete='cascade')
    source_field = fields.Char('Source Field Path', required=True, 
                              help="Path to source field using dot notation (e.g., contact.email)")
    target_field = fields.Selection([
        ('name', 'Lead Name'),
        ('contact_name', 'Contact Name'),
        ('email_from', 'Email'),
        ('phone', 'Phone'),
        ('mobile', 'Mobile'),
        ('website', 'Website'),
        ('function', 'Job Position'),
        ('title', 'Title'),
        ('street', 'Street'),
        ('street2', 'Street 2'),
        ('city', 'City'),
        ('state_id', 'State'),
        ('zip', 'ZIP'),
        ('country_id', 'Country'),
        ('company_name', 'Company Name'),
        ('industry_id', 'Industry'),
        ('description', 'Description'),
        ('tag_ids', 'Tags'),
        ('source_id', 'Source'),
        ('medium_id', 'Medium'),
        ('campaign_id', 'Campaign'),
        ('referred', 'Referred By'),
        ('user_id', 'Salesperson'),
        ('team_id', 'Sales Team'),
        ('priority', 'Priority'),
        ('type', 'Type'),
    ], string='Target Field', required=True)
    transformation_type = fields.Selection([
        ('none', 'None'),
        ('uppercase', 'Uppercase'),
        ('lowercase', 'Lowercase'),
        ('capitalize', 'Capitalize'),
        ('strip', 'Strip Whitespace'),
        ('replace', 'Replace Text'),
        ('mapping', 'Value Mapping'),
        ('format', 'Format String'),
        ('boolean', 'Convert to Boolean'),
        ('float', 'Convert to Float'),
        ('int', 'Convert to Integer'),
    ], string='Transformation', default='none')
    transformation_params = fields.Char('Transformation Parameters',
                                      help="Parameters for transformation (JSON for mapping, old|new for replace, etc.)")
    required = fields.Boolean('Required Field', default=False)
