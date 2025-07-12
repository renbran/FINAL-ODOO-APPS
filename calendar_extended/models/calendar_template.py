# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarTemplate(models.Model):
    _name = 'calendar.template'
    _description = 'Calendar Meeting Template'

    name = fields.Char('Template Name', required=True)
    duration = fields.Float('Duration (Hours)', default=1.0)
    description = fields.Text('Description')
    resource_ids = fields.Many2many('calendar.resource', string='Required Resources')
    active = fields.Boolean('Active', default=True)
