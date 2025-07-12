# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarMeetingAttendee(models.Model):
    _name = 'calendar.meeting.attendee'
    _description = 'Meeting Attendee'

    meeting_id = fields.Many2one('calendar.internal.meeting', string='Meeting', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    email = fields.Char('Email', related='partner_id.email', readonly=True)
    state = fields.Selection([
        ('needsAction', 'Needs Action'),
        ('tentative', 'Tentative'),
        ('declined', 'Declined'),
        ('accepted', 'Accepted')], 
        string='Status', default='needsAction')
