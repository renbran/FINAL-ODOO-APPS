import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api,_, exceptions
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from urllib.parse import urlparse
from odoo.exceptions import UserError
import requests
import re

class ResPartnerDocument(models.Model):
    _name = 'res.partner.document'
    _description = 'Customer Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Document Name', required=True, help="Enter the name of the document.")
    # attachment = fields.Binary(string='Attachment', help="Upload the document file as an attachment.")
    attachment = fields.Many2many('ir.attachment', string='Attachment',  help="Upload the document file as an attachment.")


    document_url = fields.Char(string="Document URL",  help="Provide a URL link to the document if available.")
    category_id = fields.Many2one('res.partner.document.category', string="Category",required=True,  help="Select the category this document belongs to.")
    expiry_date = fields.Date(string='Expiry Date', required=True,  help="The date when this document expires.")


    email = fields.Char(string='Notification Email', required=True,  help="Enter the email address to receive expiry notifications.")
    signature = fields.Binary(string="E-Signature", help="Upload an electronic signature for this document.")
    tags = fields.Many2many('res.partner.category', string="Tags",required=True, help="Assign tags to categorize this document.")
    
   
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        ondelete='cascade',
        required=True,
        help="Select the customer to whom this document belongs."
    )
    
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
        store=True,
        help="Indicates whether the document has expired."
    )
    
    expiry_status = fields.Selection(
        [
            ('expired', 'Expired'),
            ('expiring_today', 'Expiring Today'),
            ('expiring_soon', 'Expiring Soon'),
            ('valid', 'Valid'),
            ('no_expiry', 'No Expiry Date')
        ],
        string="Status",
        compute="_compute_expiry_status",
        store=False,
        help="Shows the expiry status of the document."
        
        
    )
   
      
    def action_save_document(self):
        self.ensure_one()
        current_user = self.env.user
        document_partner = self.partner_id
      
        if document_partner and document_partner != current_user.partner_id and current_user.has_group('base.group_system'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('You are creating someone else\'s document!'),
                    'type': 'warning',
                    'sticky': False,
                    'timeout': 5000,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'}
                }
            }
        else:
            return {
            
                    
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Your document was saved successfully!'),
                    'type': 'success',
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'}
                }
            }
    show_warning = fields.Boolean(
        string="Show Warning",
        compute='_compute_show_warning',
        help="Technical field to determine if warning should be shown"
    )
    @api.model
    def create(self, vals):
        user = self.env.user
        # If user is not admin and partner_id != user.partner_id -> raise error
        if not user.has_group('base.group_system') and vals.get('partner_id') != user.partner_id.id:
            raise UserError(_("You are not allowed to create a document for another customer."))
        return super().create(vals)

    def write(self, vals):
        for rec in self:
            user = self.env.user
            # If user is not admin and record.partner_id != user.partner_id -> raise error
            if not user.has_group('base.group_system') and rec.partner_id != user.partner_id:
                raise UserError(_("You are not allowed to modify a document that is not yours."))
        return super().write(vals)

    def unlink(self):
        for rec in self:
            user = self.env.user
            if not user.has_group('base.group_system') and rec.partner_id != user.partner_id:
                raise UserError(_("You are not allowed to delete a document that is not yours."))
        return super().unlink()
    

    
    
    
    
    
    
    @api.constrains('document_url')
    def _validate_document_url(self):
        for record in self:
            url = record.document_url.strip() if record.document_url else''
            
            if not url:
                raise ValidationError(_("URL cannot be empty."))

            # Check URL format
            if not url.startswith(('http://', 'https://')):
                raise ValidationError(_("URL must start with http:// or https://"))

            # Check allowed domains
            allowed_domains = [
                'drive.google.com',     
                'docs.google.com',
                'dropbox.com',
                'www.dropbox.com',
                'onedrive.live.com',
                'sharepoint.com',
                '1drv.ms'
            ]
            
            if not any(domain in url.lower() for domain in allowed_domains):
                raise ValidationError(_("Only Google Drive, OneDrive/SharePoint, and Dropbox URLs are allowed."))


            
            # **OneDrive/SharePoint Specific Validation**
            if 'sharepoint.com' in url.lower() or 'onedrive.live.com' in url.lower():
                if not self._validate_onedrive_url(url):
                    raise ValidationError(_("Invalid OneDrive/SharePoint URL format."))
                
                # Additional existence check
                if not self._check_onedrive_exists(url):
                    raise ValidationError(_("This OneDrive/SharePoint link does not exist or is inaccessible."))
                return  # Skip further checks if OneDrive/SharePoint passes
            
            # **Standard existence check for Google Drive & Dropbox**
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                
                if response.status_code == 405:  # HEAD not allowed, try GET
                    response = requests.get(url, headers=headers, timeout=10, stream=True)
                
                if response.status_code >= 400:
                    raise ValidationError(_("URL does not exist (HTTP %s)") % response.status_code)
                    
            except requests.RequestException as e:
                raise ValidationError(_("Could not verify URL: %s") % str(e))
            
            
            
    

    def _validate_onedrive_url(self, url): 
        """Strict validation for OneDrive/SharePoint URLs"""
        url = url.lower().strip()
        
        # Personal OneDrive (onedrive.live.com)
        if 'onedrive.live.com' in url:
            # Validate structure
            if not re.match(
                r'^https://onedrive\.live\.com/(?:edit\.aspx\?resid=|.*\?id=)[A-Za-z0-9!_-]{12,}(?:&cid=[A-Za-z0-9!_-]{12,})?$',
                url
            ):
                return False
            
            # Verify link existence
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.head(
                    url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )
                
                # Accept 200, 302, 401, 403 as valid
                return response.status_code in (200, 302, 401, 403)
                
            except requests.RequestException:
                return False
        
        # Business OneDrive/SharePoint (sharepoint.com)
        elif 'sharepoint.com' in url:
            # Validate structure
            if not re.match(
                r'^https://[a-z0-9-]+-my\.sharepoint\.com/:.:/g/personal/[a-z0-9._-]+_[a-z0-9-]+/[A-Za-z0-9!_-]{12,}(\?e=[A-Za-z0-9]{5,10})?$',
                url
            ):
                return False
                
            # Verify link existence
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                }
                response = requests.head(
                    url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )
                
                # Accept 200, 302, 401, 403 as valid
                return response.status_code in (200, 302, 401, 403)
                
            except requests.RequestException:
                return False
        
        # Personal OneDrive short link (1drv.ms)
        elif '1drv.ms' in url:
            # Validate structure
            if not re.match(
                r'^https://1drv\.ms/[a-z]/s![A-Za-z0-9!_-]{12,}(\?e=[A-Za-z0-9]{5,10})?$',
                url
            ):
                return False
                
            # Verify link existence
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.head(
                    url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )
                
                # Accept 200, 302, 401, 403 as valid
                return response.status_code in (200, 302, 401, 403)
                
            except requests.RequestException:
                return False
        
        return False

    def _check_onedrive_exists(self, url):
        """Check if OneDrive/SharePoint link exists (returns True/False)"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Accept 200 (OK), 302 (Redirect), 401/403 (Private but exists)
            return response.status_code in (200, 302, 401, 403)
        
        except requests.RequestException:
            return False
        
        
   
    
    def _validate_dropbox_url(self, url):
        """Validate Dropbox URL format with more flexible pattern"""
        url = url.lower().strip()
        
        # New Dropbox format with rlkey and st parameters
        if re.match(
            r'^https://(?:www\.)?dropbox\.com/scl/fo/[a-z0-9]{10,}/[^\s?]+\?(rlkey=[a-z0-9]+&st=[a-z0-9]+)(?:&dl=[01])?$',
            url
        ):
            return True
        
        # Older Dropbox format without parameters
        if re.match(
            r'^https://(?:www\.)?dropbox\.com/s/[a-z0-9]{10,}/[^\s?]+(?:\?dl=[01])?$',
            url
        ):
            return True
        
        # Preview links
        if re.match(
            r'^https://(?:www\.)?dropbox\.com/preview/[^\s?]+(?:\?.*)?$',
            url
        ):
            return True
        
        return False

    def _check_dropbox_accessible(self, url):
        """Check if Dropbox link is actually accessible (can be opened)"""
        try:
            # Convert to preview URL if it's a download link
            check_url = url.replace('?dl=1', '?dl=0') if '?dl=1' in url else url
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # First try HEAD request
            try:
                response = requests.head(
                    check_url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )
                if response.status_code == 200:
                    return True
            except:
                pass
            
            # If HEAD fails or returns non-200, do a GET request with stream=True
            response = requests.get(
                check_url,
                headers=headers,
                timeout=15,
                allow_redirects=True,
                stream=True
            )
            
            # Check for error responses
            if response.status_code != 200:
                return False
                
            # Check if we got redirected to an error page
            final_url = response.url.lower()
            if any(x in final_url for x in ['error', 'login', 'home']):
                return False
                
            # Check content type and initial content for error messages
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                try:
                    first_chunk = next(response.iter_content(1024)).decode('utf-8').lower()
                    if any(x in first_chunk for x in ['error', 'not found', 'does not exist', 'dropbox 404']):
                        return False
                    # Additional check for Dropbox-specific error messages
                    if 'this file was deleted' in first_chunk or 'this folder is empty' in first_chunk:
                        return False
                except:
                    pass
                    
            return True
            
        except requests.RequestException:
            return False
        
        
        
        
        
        
        
    
    # def _validate_onedrive_url(self, url):
    #     """Strict validation for OneDrive/SharePoint URLs"""
    #     url = url.lower().strip()
        
    #     # Personal OneDrive (onedrive.live.com)
    #     if 'onedrive.live.com' in url:
    #         # Validate structure
    #         if not re.match(
    #             r'^https://onedrive\.live\.com/(?:edit\.aspx\?resid=|.*\?id=)[A-Za-z0-9!_-]{12,}(?:&cid=[A-Za-z0-9!_-]{12,})?$',
    #             url
    #         ):
    #             return False
            
    #         # Verify link existence
    #         try:
    #             headers = {'User-Agent': 'Mozilla/5.0'}
    #             response = requests.head(
    #                 url,
    #                 headers=headers,
    #                 timeout=10,
    #                 allow_redirects=True
    #             )
                
    #             # Accept 200, 302, 401, 403 as valid
    #             return response.status_code in (200, 302, 401, 403)
                
    #         except requests.RequestException:
    #             return False
        
    #     # Business OneDrive/SharePoint (sharepoint.com)
    #     elif 'sharepoint.com' in url:
    #         # Validate structure
    #         if not re.match(
    #             r'^https://[a-z0-9-]+-my\.sharepoint\.com/:.:/g/personal/[a-z0-9._-]+_[a-z0-9-]+/[A-Za-z0-9!_-]{12,}(\?e=[A-Za-z0-9]{5,10})?$',
    #             url
    #         ):
    #             return False
                
    #         # Verify link existence
    #         try:
    #             headers = {
    #                 'User-Agent': 'Mozilla/5.0',
    #                 'Accept': 'application/json'
    #             }
    #             response = requests.head(
    #                 url,
    #                 headers=headers,
    #                 timeout=10,
    #                 allow_redirects=True
    #             )
                
    #             # Accept 200, 302, 401, 403 as valid
    #             return response.status_code in (200, 302, 401, 403)
                
    #         except requests.RequestException:
    #             return False
        
    #     return False

    # def _check_onedrive_exists(self, url):
    #     """Check if OneDrive/SharePoint link exists (returns True/False)"""
    #     try:
    #         headers = {'User-Agent': 'Mozilla/5.0'}
    #         response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
    #         # Accept 200 (OK), 302 (Redirect), 401/403 (Private but exists)
    #         return response.status_code in (200, 302, 401, 403)
        
    #     except requests.RequestException:
    #         return False
        

    


    # @api.constrains('document_url')
    # def _check_valid_url(self):
    #     trusted_domains = [
    #         'drive.google.com',
    #         'docs.google.com',
    #         'dropbox.com',
    #         'onedrive.live.com'
    #     ]
    #     for record in self:
    #         url = record.document_url
    #         if url:
    #             # Must start with http/https
    #             if not url.startswith('http://') and not url.startswith('https://'):
    #                 raise ValidationError("URL must start with http:// or https://")

    #             # Check if it contains a trusted domain
    #             if not any(domain in url for domain in trusted_domains):
    #                 raise ValidationError("Only Google Drive, Dropbox, or OneDrive URLs are allowed.")
                
            
            
            
            
    # @api.constrains('document_url')
    # def _check_valid_url(self):
    #     url_regex = re.compile(
    #         r'^(https?://)?'  # http:// or https://
    #         r'((drive\.google\.com|dropbox\.com|onedrive\.live\.com|docs\.google\.com)|'  # allowed domains
    #         r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}))'  # any domain (fallback)
    #         r'(/[^\s]*)?$'  # path
    #     )
    #     for record in self:
    #         if record.document_url:
    #             if not url_regex.match(record.document_url):
    #                 raise ValidationError("Please enter a valid URL (e.g., Google Drive, Dropbox, OneDrive, etc).")
    
    
    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        for record in self:
            if record.expiry_date and record.expiry_date < date.today():
                raise ValidationError(_("Expiry date cannot be in the past. Please select a valid date."))
    
    @api.constrains('expiry_date')
    def _validate_expiry_not_today(self):
        today = fields.Date.today()
        for record in self:
            if record.expiry_date == today:
                raise ValidationError(_("You cannot set today's date as the expiry date. Please select a future date."))

    
    def write(self, vals):
        if 'expiry_date' in vals:
            new_date = fields.Date.from_string(vals['expiry_date'])
            today = fields.Date.today()
            if new_date <= today:
                raise ValidationError(_("You cannot set the expiry date to today or a past date. Please select a future date."))

        return super(ResPartnerDocument, self).write(vals)


    def action_delete_document(self):
     for rec in self:
        rec.unlink()
        
        
    @api.constrains('attachment')
    def _check_attachment_required(self):
        for rec in self:
            if not rec.attachment:
                raise ValidationError(_("Please upload at least one attachment."))
        
    # @api.constrains('attachment', 'document_url')
    # def _check_attachment_or_url(self):
    #     for record in self:
    #         if not record.attachment and not record.document_url:
    #             raise ValidationError("You must either upload an attachment or provide a document URL.")

    
    # @api.constrains('attachment')
    # def _check_attachment_required(self):
    #     for record in self:
    #         if not record.attachment:
    #             raise ValidationError("Please upload at least one attachment.")
    
    # @api.constrains('attachment')
    # def _check_attachment_required(self):
    #     for record in self:
    #         if not record.attachment:
    #             raise ValidationError("Please upload at least one attachment before saving.")
            
            
    # @api.model
    # def create(self, vals):
    #     """ Attach documents to the chatter automatically when a document is created """
    #     record = super(ResPartnerDocument, self).create(vals)

       
    #     if 'attachment_ids' in vals:
    #         attachments = self.env['ir.attachment'].browse(vals['attachment_ids'][0][2])
    #         for attachment in attachments:
    #             record.message_post(
    #                 body=f"📎 New document uploaded: <b>{attachment.name}</b>",
    #                 attachment_ids=[(4, attachment.id)]
    #             )

    #     return record
    
   

    # @api.model
    # def create(self, vals):
    #     """ Attach documents to the chatter automatically when a document is created """
    #     record = super(ResPartnerDocument, self).create(vals)

       
    #     if 'attachment_ids' in vals:
    #         attachments = self.env['ir.attachment'].browse(vals['attachment_ids'][0][2])
    #         for attachment in attachments:
    #             record.message_post(
    #                 body=f"📎 New document uploaded: <b>{attachment.name}</b>",
    #                 attachment_ids=[(4, attachment.id)]
    #             )

    #     return record

    @api.depends('expiry_date')
    def _compute_expiry_status(self):
      today = date.today()
      for record in self:
        if record.expiry_date:
            if record.expiry_date < today:
                record.expiry_status = 'expired'
            elif record.expiry_date == today:
                    record.expiry_status = 'expiring_today'
            elif today <= record.expiry_date <= today + timedelta(days=7):
                record.expiry_status = 'expiring_soon'
            else:
                record.expiry_status = 'valid'
        else:
            record.expiry_status = 'no_expiry'


 
    @api.model
    def create(self, vals):
        """Override create method to update the dashboard when a new document is added."""
        record = super(ResPartnerDocument, self).create(vals)
        self.env["customer.document.dashboard"].calculate_expiry_data()
        return record
    
    def write(self, vals):
        result = super(ResPartnerDocument, self).write(vals)
        self.env["customer.document.dashboard"].calculate_expiry_data()  # Update dashboard
        return result


    @api.model
    def send_expiry_notification(self):
        """Send emails before, on, and after the document expiry date."""

        # Fetch configuration for days before and after
        notify_days_before = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'zehntech_customer_document_management.notify_days_before_expiry', default=7
            )
        )
        notify_days_after = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'zehntech_customer_document_management.notify_days_after_expiry', default=1
            )
        )

        today = fields.Date.today()

        # Load email templates
        template_today = self.env.ref('zehntech_customer_document_management.email_template_document_expiry_today', raise_if_not_found=False)
        template_before = self.env.ref('zehntech_customer_document_management.email_template_document_expiry_before', raise_if_not_found=False)
        template_after = self.env.ref('zehntech_customer_document_management.email_template_document_expiry_after', raise_if_not_found=False)

        if not template_today or not template_before or not template_after:
            return  # if any template is missing, exit safely

        for record in self.search([]):
            if not record.email or not record.expiry_date:
                continue  # Skip if email or expiry date is missing

            # Calculate related dates
            before_expiry_date = record.expiry_date - timedelta(days=notify_days_before)
            after_expiry_date = record.expiry_date + timedelta(days=notify_days_after)

            # Decide which template to send
            if today == record.expiry_date:
                # Send TODAY expiry notification
                template_today.send_mail(record.id, force_send=True)
            elif today == before_expiry_date:
                # Send BEFORE expiry notification
                template_before.send_mail(record.id, force_send=True)
            elif today == after_expiry_date:
                # Send AFTER expiry notification
                template_after.send_mail(record.id, force_send=True)

    # def send_expiry_notification(self):
    #     """Send email notification before, on, and after the expiry date.
    #        Also update the cron job’s next execution time based on a global setting.
    #     """
    #     notify_days_before = int(
    #         self.env['ir.config_parameter'].sudo().get_param(
    #             'zehntech_customer_document_management.notify_days_before_expiry', default=7
    #         )
    #     )
    #     notify_days_after = int(
    #         self.env['ir.config_parameter'].sudo().get_param(
    #             'zehntech_customer_document_management.notify_days_after_expiry', default=1
    #         )
    #     )
       
    #     today = fields.Date.today()
    #     template = self.env.ref('zehntech_customer_document_management.email_template_document_expiry')
       
    #     for record in self.search([]):
    #         if not record.email:
    #             continue  # Skip if no email provided
    #         before_expiry_date = record.expiry_date - timedelta(days=notify_days_before)
    #         after_expiry_date = record.expiry_date + timedelta(days=notify_days_after)
 
    #         if record.expiry_date == today or before_expiry_date == today or after_expiry_date == today:
    #             template.send_mail(
    #                 record.id,
    #                 force_send=True,
    #                 email_values={'email_to': record.email}
    #             )
       
    #     cron_time = float(
    #         self.env['ir.config_parameter'].sudo().get_param(
    #             'zehntech_customer_document_management.cron_run_time', default=15.33
    #         )
    #     )
    #     cron_hour = int(cron_time)
    #     cron_minute = int((cron_time - cron_hour) * 60)
        
    #     cron = self.env.ref('zehntech_customer_document_management.cron_check_document_expiry', raise_if_not_found=False)
    #     if cron:
    #         new_nextcall = datetime.now().replace(hour=cron_hour, minute=cron_minute, second=0, microsecond=0)
    #         if new_nextcall < datetime.now():
    #             new_nextcall += timedelta(days=1)
    #         cron.sudo().write({'nextcall': new_nextcall})

    

    @api.model
    def update_cron_time(self):
        """Update the cron job execution time based on user settings"""
        cron_time = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'zehntech_customer_document_management.cron_run_time', default=15.33
            )
        )
        cron_hour = int(cron_time)
        cron_minute = int((cron_time - cron_hour) * 60)

        cron = self.env.ref('zehntech_customer_document_management.cron_check_document_expiry', raise_if_not_found=False)
        if cron:
            new_nextcall = datetime.now().replace(hour=cron_hour, minute=cron_minute, second=0, microsecond=0)

            # Ensure the cron is scheduled for the next valid time
            if new_nextcall < datetime.now():
                new_nextcall += timedelta(days=1)

            cron.sudo().write({'nextcall': new_nextcall})
            
            
    def _validate_email_format(self, email):
        """ Check if email format is valid """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if email and not re.match(email_regex, email):
            raise ValidationError(_("Invalid Email Format! Please enter a valid email."))


    @api.model
    def create(self, vals):
        """ Validate email and attachment before saving """
        if 'email' in vals:
            self._validate_email_format(vals['email'])

        if not vals.get('attachment') and not vals.get('document_url'):
            raise ValidationError(_("Attachment or Document URL is required."))

        return super(ResPartnerDocument, self).create(vals)

    def write(self, vals):
        """ Validate email and attachment on update """
        if 'email' in vals:
            self._validate_email_format(vals['email'])

        if ('attachment' in vals or 'document_url' in vals) and not vals.get('attachment') and not vals.get('document_url'):
            raise ValidationError(_("Attachment or Document URL is required."))

        return super(ResPartnerDocument, self).write(vals)
    
    
    
    
    
    
    
    


#     @api.depends('attachment_ids.mimetype')
#     def _compute_previewable_attachments(self):
#         """Mark only PDF attachments as previewable."""
#         for record in self:
#             record.previewable_attachments = record.attachment_ids.filtered(
#                 lambda att: att.mimetype and att.mimetype.startswith('application/pdf')
#             )

# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'

#     previewable = fields.Boolean(string="Can be Previewed", compute="_compute_previewable", store=True)

#     @api.depends('mimetype')
#     def _compute_previewable(self):
#         """Compute whether an attachment can be previewed (Only PDFs)."""
#         for attachment in self:
#             attachment.previewable = bool(attachment.mimetype and attachment.mimetype.startswith('application/pdf'))




    
    
    
    