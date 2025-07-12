# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarReminder(models.Model):
    _name = 'calendar.reminder'
    _description = 'Calendar Meeting Reminder'

    meeting_id = fields.Many2one('calendar.internal.meeting', string='Meeting', required=True)
    reminder_type = fields.Selection([
        ('email', 'Email'),
        ('notification', 'Notification')
    ], string='Reminder Type', required=True)
    minutes = fields.Integer('Minutes Before', default=30)
    sent = fields.Boolean('Sent', default=False)
