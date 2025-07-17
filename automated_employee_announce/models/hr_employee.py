from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def send_birthday_announcements(self):
        """Send birthday announcements to all employees."""
        today = date.today()
        birthday_employees = self.search([
            ('birthday', '!=', False),
        ])
        
        for employee in birthday_employees:
            if employee.birthday and employee.birthday.month == today.month and employee.birthday.day == today.day:
                # Find the birthday mail template
                template = self.env.ref('automated_employee_announce.mail_template_employee_birthday', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(employee.id, force_send=True)
                        employee.message_post(body="Automated: Birthday announcement email sent.")
                        _logger.info(f"Birthday announcement sent for {employee.name}")
                    except Exception as e:
                        _logger.error(f"Failed to send birthday announcement for {employee.name}: {str(e)}")
    
    def send_anniversary_announcements(self):
        """Send work anniversary announcements to all employees."""
        today = date.today()
        employees_with_hire_date = self.search([
            ('joining_date', '!=', False),
        ])
        
        for employee in employees_with_hire_date:
            if employee.joining_date and employee.joining_date.month == today.month and employee.joining_date.day == today.day:
                # Find the anniversary mail template
                template = self.env.ref('automated_employee_announce.mail_template_employee_anniversary', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(employee.id, force_send=True)
                        employee.message_post(body="Automated: Work anniversary announcement email sent.")
                        _logger.info(f"Anniversary announcement sent for {employee.name}")
                    except Exception as e:
                        _logger.error(f"Failed to send anniversary announcement for {employee.name}: {str(e)}")
    
    @api.model
    def cron_send_birthday_announcements(self):
        """Cron job to send birthday announcements."""
        self.send_birthday_announcements()
        
    @api.model 
    def cron_send_anniversary_announcements(self):
        """Cron job to send anniversary announcements."""
        self.send_anniversary_announcements()
