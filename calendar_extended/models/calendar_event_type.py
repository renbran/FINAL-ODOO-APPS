# -*- coding: utf-8 -*-
from odoo import models, fields

class CalendarEventType(models.Model):
    _name = 'calendar.event.type'
    _description = 'Calendar Event Type'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
