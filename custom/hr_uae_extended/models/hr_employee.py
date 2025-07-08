# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # UAE Specific Fields
    visa_expiry_date = fields.Date(string='Visa Expiry Date')
    passport_expiry_date = fields.Date(string='Passport Expiry Date')
    emirates_id = fields.Char(string='Emirates ID')
    emirates_id_expiry_date = fields.Date(string='Emirates ID Expiry Date')

    # Annual Benefits
    annual_air_ticket = fields.Boolean(string='Eligible for Annual Air Ticket')
    air_ticket_amount = fields.Float(string='Air Ticket Amount')
    air_ticket_frequency = fields.Selection([
        ('yearly', 'Yearly'),
        ('two_yearly', 'Every Two Years')
    ], string='Air Ticket Frequency', default='yearly')
    last_ticket_date = fields.Date(string='Last Air Ticket Date')
    next_ticket_date = fields.Date(string='Next Air Ticket Date', compute='_compute_next_ticket_date', store=True)

    # Leave Benefits
    annual_leave_days = fields.Float(string='Annual Leave Days', default=30)
    annual_leave_salary_type = fields.Selection([
        ('basic', 'Basic Salary'),
        ('gross', 'Gross Salary')
    ], string='Annual Leave Salary Calculation', default='basic')
    
    # Agent Commission
    is_agent = fields.Boolean(string='Is Agent')
    agent_type = fields.Selection([
        ('business_lead', 'Business Lead'),
        ('personal_lead', 'Personal Lead')
    ], string='Agent Type')
    business_lead_commission = fields.Float(string='Business Lead Commission %', digits=(5, 2), default=55.0)
    personal_lead_commission = fields.Float(string='Personal Lead Commission %', digits=(5, 2), default=45.0)
    is_sales_manager = fields.Boolean(string='Is Sales Manager')
    is_relationship_manager = fields.Boolean(string='Is Relationship Manager')
    sales_manager_commission = fields.Float(string='Sales Manager Commission %', digits=(5, 2), default=2.0)
    relationship_manager_commission = fields.Float(string='Relationship Manager Commission %', digits=(5, 2), default=5.0)

    @api.depends('last_ticket_date', 'air_ticket_frequency')
    def _compute_next_ticket_date(self):
        for employee in self:
            if employee.last_ticket_date:
                if employee.air_ticket_frequency == 'yearly':
                    employee.next_ticket_date = employee.last_ticket_date + relativedelta(years=1)
                else:
                    employee.next_ticket_date = employee.last_ticket_date + relativedelta(years=2)
            else:
                employee.next_ticket_date = False

    def calculate_leave_salary(self, days):
        """Calculate leave salary based on UAE labor law"""
        self.ensure_one()
        if self.annual_leave_salary_type == 'basic':
            daily_rate = self.contract_id.wage / 30
        else:
            # Include allowances for gross calculation
            daily_rate = (self.contract_id.wage + self.contract_id.allowances) / 30
        return daily_rate * days
