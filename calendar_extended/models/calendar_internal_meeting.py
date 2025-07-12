# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarInternalMeeting(models.Model):
    _name = 'calendar.internal.meeting'
    _description = 'Internal Meeting'

    name = fields.Char('Meeting Title', required=True)
    start = fields.Datetime('Start Date', required=True)
    stop = fields.Datetime('End Date', required=True)
    duration = fields.Float('Duration', compute='_compute_duration', store=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)

    @api.depends('start', 'stop')
    def _compute_duration(self):
        for meeting in self:
            if meeting.start and meeting.stop:
                diff = meeting.stop - meeting.start
                meeting.duration = diff.total_seconds() / 3600.0
            else:
                meeting.duration = 0.0
