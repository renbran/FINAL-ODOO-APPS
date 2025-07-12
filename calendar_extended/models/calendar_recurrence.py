# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarRecurrence(models.Model):
    _name = 'calendar.recurrence'
    _description = 'Calendar Meeting Recurrence'

    meeting_id = fields.Many2one('calendar.internal.meeting', string='Meeting', required=True)
    recurrence_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Recurrence Type', required=True)
    interval = fields.Integer('Repeat Every', default=1)
    end_type = fields.Selection([
        ('count', 'Number of repetitions'),
        ('end_date', 'End date'),
        ('forever', 'Forever')
    ], string='Ends', default='count')
    count = fields.Integer('Count', default=1)
    end_date = fields.Date('End Date')
