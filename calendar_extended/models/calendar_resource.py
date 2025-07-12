# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarResource(models.Model):
    _name = 'calendar.resource'
    _description = 'Calendar Resource'

    name = fields.Char('Name', required=True)
    resource_type = fields.Selection([
        ('room', 'Room'),
        ('equipment', 'Equipment'),
        ('other', 'Other')
    ], string='Resource Type', default='room', required=True)
    capacity = fields.Integer('Capacity')
    location = fields.Char('Location')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
