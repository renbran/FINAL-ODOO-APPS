# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class RentalConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_days = fields.Integer(string='Days', default=5,
                                   config_parameter='rental_management.reminder_days')
    sale_reminder_days = fields.Integer(string="Days ", default=3,
                                        config_parameter='rental_management.sale_reminder_days')
    invoice_post_type = fields.Selection([('manual', 'Invoice Post Manually'),
                                          ('automatically', 'Invoice Post Automatically')], string="Invoice Post",
                                         default='manual', config_parameter='rental_management.invoice_post_type')

    month_days = fields.Integer(string="Month Days",
                                default=30, config_parameter='rental_management.month_days')
    quarter_days = fields.Integer(string="Quarter Days",
                                  default=90, config_parameter='rental_management.quarter_days')
    year_days = fields.Integer(string="Year Days",
                               default=365, config_parameter='rental_management.year_days')

    # Default Account Product
    installment_item_id = fields.Many2one('product.product', string="Installment Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_1',
                                                                            raise_if_not_found=False),
                                          config_parameter='rental_management.account_installment_item_id')
    deposit_item_id = fields.Many2one('product.product', string="Deposit Item",
                                      default=lambda self: self.env.ref('rental_management.property_product_2',
                                                                        raise_if_not_found=False),
                                      config_parameter='rental_management.account_deposit_item_id')
    broker_item_id = fields.Many2one('product.product', string="Broker Commission Item",
                                     default=lambda self: self.env.ref('rental_management.property_product_3',
                                                                       raise_if_not_found=False),
                                     config_parameter='rental_management.account_broker_item_id')
    maintenance_item_id = fields.Many2one('product.product', string="Maintenance Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_4',
                                                                            raise_if_not_found=False),
                                          config_parameter='rental_management.account_maintenance_item_id')

    # Fee Configuration
    default_dld_fee_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Sale Price')
    ], string='Default DLD Fee Type', default='percentage',
       config_parameter='rental_management.default_dld_fee_type',
       help='Dubai Land Department fee calculation method')

    default_dld_fee_percentage = fields.Float(
        string='Default DLD Fee Percentage',
        default=4.0,
        config_parameter='rental_management.default_dld_fee_percentage',
        help='Default DLD Fee as percentage of sale price (e.g., 4.0 for 4%)')

    default_dld_fee_amount = fields.Monetary(
        string='Default DLD Fee (Fixed)',
        config_parameter='rental_management.default_dld_fee_amount',
        currency_field='currency_id',
        help='Default fixed DLD Fee amount')

    default_admin_fee_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Sale Price')
    ], string='Default Admin Fee Type', default='percentage',
       config_parameter='rental_management.default_admin_fee_type',
       help='Administrative fee calculation method')

    default_admin_fee_percentage = fields.Float(
        string='Default Admin Fee Percentage',
        default=2.0,
        config_parameter='rental_management.default_admin_fee_percentage',
        help='Default Admin Fee as percentage of sale price (e.g., 2.0 for 2%)')

    default_admin_fee_amount = fields.Monetary(
        string='Default Admin Fee (Fixed)',
        config_parameter='rental_management.default_admin_fee_amount',
        currency_field='currency_id',
        help='Default fixed Admin Fee amount')

    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)
