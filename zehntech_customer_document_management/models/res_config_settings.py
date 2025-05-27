import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from odoo import _

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
   
    def _update_cron_time(self):
        # Example: Find the cron job and update its execution time
        cron = self.env.ref('zehntech_customer_document_management.ir_cron_document_expiry_notification', raise_if_not_found=False)
        if cron:
            cron.write({'interval_number': 1, 'interval_type': 'days'})

    
    email_notification_time = fields.Datetime(
    string='Expiry Notification Date & Time',
  
    )

    @api.constrains('email_notification_time')
    def _check_email_notification_time_not_in_past(self):
        for record in self:
            if record.email_notification_time:
                now = fields.Datetime.now()
                if record.email_notification_time < now:
                    raise ValidationError(_("You cannot set a past date and time for expiry notifications."))

    
    # Define Unsplash API fields
    unsplash_access_key = fields.Char(
        string="Unsplash Access Key",
        config_parameter='zehntech_customer_document_management.unsplash_access_key',
        help="API access key for integrating Unsplash."
    )

    unsplash_app_id = fields.Char(
        string="Unsplash App ID",
        config_parameter='zehntech_customer_document_management.unsplash_app_id',
        
    )

    # Define notification settings
    notify_days_before_expiry = fields.Integer(
        string="Days Before Expiry Notification",
        config_parameter='zehntech_customer_document_management.notify_days_before_expiry',
        default=7,
       
    )

    notify_days_after_expiry = fields.Integer(
        string="Days After Expiry Notification",
        config_parameter='zehntech_customer_document_management.notify_days_after_expiry',
        default=1,
        
    )

    
    def set_values(self):
        """Save settings values and update cron job execution time dynamically."""
        super(ResConfigSettings, self).set_values()
        
        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('zehntech_customer_document_management.email_notification_time', str(self.email_notification_time or ''))

        # Update cron job timing only if email_notification_time is set
        if self.email_notification_time:
            cron = self.env.ref('zehntech_customer_document_management.cron_document_expiry_notification', raise_if_not_found=False)

            if cron:
                cron_time = fields.Datetime.to_datetime(self.email_notification_time)  # Convert to datetime
                cron.write({
                    'interval_number': 1,
                    'interval_type': 'days',
                    'nextcall': cron_time.strftime('%Y-%m-%d %H:%M:%S'),
                })

    @api.model
    def get_values(self):
        """Retrieve settings values."""
        res = super(ResConfigSettings, self).get_values()
        res.update(
            email_notification_time=self.env['ir.config_parameter'].sudo().get_param('zehntech_customer_document_management.email_notification_time')
        )
        return res


   
    
 

   