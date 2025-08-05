# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def birthday_reminder(self):
        """
        Automated birthday reminder system for OSUS Properties
        Sends birthday wishes to employees and notifications to team
        """
        try:
            today = date.today()
            month = today.month
            day = today.day
            
            # Find employees with birthdays today
            birthday_employees = self.search([
                ('birthday', '!=', False),
                ('active', '=', True)
            ])
            
            for employee in birthday_employees:
                if employee.birthday and employee.birthday.day == day and employee.birthday.month == month:
                    
                    # Send birthday wish to the employee
                    if employee.work_email:
                        try:
                            birthday_template = self.env.ref('osus_birthday_greetings.mail_template_birthday_wish')
                            birthday_template.send_mail(employee.id, force_send=True)
                            _logger.info(f"Birthday wish sent to {employee.name} ({employee.work_email})")
                        except Exception as e:
                            _logger.error(f"Failed to send birthday wish to {employee.name}: {str(e)}")
                    
                    # Send reminder to all other employees
                    other_employees = self.search([
                        ('id', '!=', employee.id),
                        ('work_email', '!=', False),
                        ('active', '=', True)
                    ])
                    
                    if other_employees:
                        all_emails = other_employees.mapped('work_email')
                        if all_emails:
                            try:
                                reminder_template = self.env.ref('osus_birthday_greetings.mail_template_birthday_reminder')
                                email_values = {
                                    'email_to': ','.join(all_emails),
                                    'email_cc': False,
                                    'email_bcc': False,
                                }
                                reminder_template.send_mail(
                                    employee.id, 
                                    email_values=email_values, 
                                    force_send=True
                                )
                                _logger.info(f"Birthday reminder sent to {len(all_emails)} employees for {employee.name}")
                            except Exception as e:
                                _logger.error(f"Failed to send birthday reminder for {employee.name}: {str(e)}")
                                
        except Exception as e:
            _logger.error(f"Error in birthday_reminder function: {str(e)}")

    @api.model
    def _cron_birthday_reminder(self):
        """
        Cron job method for automated birthday reminders
        """
        _logger.info("Starting OSUS Properties birthday reminder cron job")
        self.birthday_reminder()
        _logger.info("Completed OSUS Properties birthday reminder cron job")