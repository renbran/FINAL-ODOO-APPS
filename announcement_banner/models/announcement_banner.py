# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
import re


class AnnouncementBanner(models.Model):
    _name = 'announcement.banner'
    _description = 'Announcement Banner'
    _order = 'priority desc, id desc'

    name = fields.Char('Title', required=True, help='Title of the announcement')
    message = fields.Html(
        'Message', 
        required=True, 
        sanitize=True,
        sanitize_style=True,
        sanitize_tags=False,
        help='HTML content of the announcement. Use the editor toolbar to format your message.'
    )
    active = fields.Boolean('Active', default=True, help='Only active announcements will be displayed')
    priority = fields.Integer('Priority', default=10, help='Higher priority announcements show first')
    start_date = fields.Datetime('Start Date', help='Announcement will only show after this date')
    end_date = fields.Datetime('End Date', help='Announcement will only show before this date')
    show_once = fields.Boolean('Show Once Per User', default=False, 
                                help='If checked, each user will see this announcement only once')
    user_ids = fields.Many2many('res.users', string='Target Users',
                                 help='Leave empty to show to all users. Select specific users to target them only.')
    shown_count = fields.Integer('Times Shown', compute='_compute_shown_count', store=False)
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate that end date is after start date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError('End date must be after start date.')
    
    @api.constrains('message')
    def _validate_message(self):
        """Validate message content for HTML integrity"""
        for record in self:
            if record.message:
                message_str = str(record.message)
                
                # Check for common HTML tag mismatches
                open_divs = message_str.count('<div')
                close_divs = message_str.count('</div>')
                open_spans = message_str.count('<span')
                close_spans = message_str.count('</span>')
                
                if open_divs != close_divs:
                    raise ValidationError(
                        f'Message contains mismatched div tags ({open_divs} opening, {close_divs} closing). '
                        'Please check your HTML formatting.'
                    )
                
                if open_spans != close_spans:
                    raise ValidationError(
                        f'Message contains mismatched span tags ({open_spans} opening, {close_spans} closing). '
                        'Please check your HTML formatting.'
                    )
    
    def process_message_content(self, message):
        """Process and clean HTML message content for proper display"""
        if not message:
            return ''
        
        # Convert Markup to string if needed
        if hasattr(message, '__html__'):
            message = str(message)
        
        # Strip leading/trailing whitespace
        message = message.strip()
        
        # If message is empty after stripping, return empty string
        if not message:
            return ''
        
        # Check if content is predominantly plain text (minimal HTML tags)
        has_block_tags = bool(re.search(r'<(p|div|h[1-6]|ul|ol|table|pre)[^>]*>', message))
        
        if not has_block_tags:
            # Content is plain text or inline HTML only
            # Split by double line breaks for paragraphs
            paragraphs = re.split(r'\n\s*\n+', message)
            processed_paragraphs = []
            
            for para in paragraphs:
                para = para.strip()
                if para:
                    # Replace single line breaks with <br> within paragraph
                    para = para.replace('\n', '<br>')
                    # Wrap in paragraph tag if not already wrapped
                    if not para.startswith('<'):
                        para = f'<p>{para}</p>'
                    processed_paragraphs.append(para)
            
            message = '\n'.join(processed_paragraphs)
        else:
            # Content has HTML structure, just clean it up
            # Convert orphan line breaks to <br> tags
            message = re.sub(r'(?<!>)\n(?!<)', '<br>', message)
            
            # Clean up multiple consecutive <br> tags
            message = re.sub(r'(<br\s*/?>){3,}', '<br><br>', message)
        
        # Ensure images have proper responsive attributes
        # Add img-fluid class to images without any class
        message = re.sub(
            r'<img(?!\s[^>]*class=)',
            '<img class="img-fluid"',
            message
        )
        
        # Add img-fluid class to images that have other classes
        message = re.sub(
            r'<img\s+([^>]*class=["\'])(?![^"\']*img-fluid)([^"\']*["\'])',
            r'<img \1img-fluid \2',
            message
        )
        
        # Ensure images have alt attribute for accessibility
        message = re.sub(
            r'<img(?!\s[^>]*alt=)',
            '<img alt="Announcement image"',
            message
        )
        
        # Process tables for responsive display
        if '<table' in message:
            # Track if we're already inside a table-responsive div
            parts = []
            in_table = False
            in_responsive_div = False
            
            lines = message.split('\n')
            for line in lines:
                # Check for existing table-responsive wrapper
                if 'table-responsive' in line and '<div' in line:
                    in_responsive_div = True
                    parts.append(line)
                    continue
                
                # Opening table tag
                if '<table' in line and not in_table:
                    in_table = True
                    # Only wrap if not already in responsive div
                    if not in_responsive_div:
                        parts.append('<div class="table-responsive">')
                    
                    # Add table classes if not present
                    if 'class=' not in line:
                        line = line.replace('<table', '<table class="table table-bordered"')
                    elif 'table' not in line:
                        line = re.sub(r'class="([^"]*)"', r'class="\1 table table-bordered"', line)
                    parts.append(line)
                
                # Closing table tag
                elif '</table>' in line and in_table:
                    parts.append(line)
                    # Close responsive div if we opened it
                    if not in_responsive_div:
                        parts.append('</div>')
                    in_table = False
                    in_responsive_div = False
                else:
                    parts.append(line)
            
            message = '\n'.join(parts)
        
        # Clean up excessive whitespace while preserving intentional structure
        # Remove multiple blank lines but keep paragraph spacing
        message = re.sub(r'\n\s*\n\s*\n+', '\n\n', message)
        
        # Remove whitespace before closing tags
        message = re.sub(r'\s+</', '</', message)
        
        # Remove whitespace after opening tags
        message = re.sub(r'>\s+', '>', message)
        
        return message.strip()
    
    def _compute_shown_count(self):
        """Compute how many times the announcement has been shown"""
        for record in self:
            record.shown_count = self.env['announcement.banner.log'].search_count([
                ('announcement_id', '=', record.id)
            ])
    
    @api.model
    def get_active_announcements(self):
        """Return active announcements for current user"""
        domain = [('active', '=', True)]
        now = fields.Datetime.now()
        
        announcements = self.search(domain)
        result = []
        
        for announcement in announcements:
            # Check date range
            if announcement.start_date and announcement.start_date > now:
                continue
            if announcement.end_date and announcement.end_date < now:
                continue
            
            # Check target users
            if announcement.user_ids and self.env.user not in announcement.user_ids:
                continue
            
            # Check if already shown
            if announcement.show_once:
                shown = self.env['announcement.banner.log'].search([
                    ('announcement_id', '=', announcement.id),
                    ('user_id', '=', self.env.user.id)
                ], limit=1)
                if shown:
                    continue
            
            # Process message content for proper display
            message_content = announcement.process_message_content(announcement.message)
            
            result.append({
                'id': announcement.id,
                'name': announcement.name,
                'message': message_content,
                'priority': announcement.priority,
            })
        
        return result
    
    @api.model
    def mark_as_shown(self, announcement_id):
        """Mark announcement as shown for current user"""
        announcement = self.browse(announcement_id)
        if announcement.exists():
            # Check if already logged to avoid duplicates
            existing_log = self.env['announcement.banner.log'].search([
                ('announcement_id', '=', announcement_id),
                ('user_id', '=', self.env.user.id)
            ], limit=1)
            
            if not existing_log:
                self.env['announcement.banner.log'].create({
                    'announcement_id': announcement_id,
                    'user_id': self.env.user.id,
                })
        return True
    
    def action_preview(self):
        """Preview the processed announcement message"""
        self.ensure_one()
        processed_message = self.process_message_content(self.message)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Preview: ' + self.name,
                'message': Markup(processed_message),
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_test_announcement(self):
        """Test the announcement display for current user"""
        self.ensure_one()
        
        # Temporarily enable the announcement
        original_active = self.active
        self.active = True
        
        try:
            announcements = self.get_active_announcements()
            matching = [a for a in announcements if a['id'] == self.id]
            
            if matching:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Test Successful',
                        'message': 'Announcement would be displayed to you. Check browser console for details.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Test Failed',
                        'message': 'Announcement would NOT be displayed (check dates, user targeting, or show_once setting).',
                        'type': 'warning',
                        'sticky': True,
                    }
                }
        finally:
            self.active = original_active


class AnnouncementBannerLog(models.Model):
    _name = 'announcement.banner.log'
    _description = 'Announcement Banner Log'
    _order = 'shown_date desc'
    _rec_name = 'announcement_id'

    announcement_id = fields.Many2one(
        'announcement.banner', 
        'Announcement', 
        required=True, 
        ondelete='cascade', 
        index=True
    )
    user_id = fields.Many2one(
        'res.users', 
        'User', 
        required=True, 
        ondelete='cascade', 
        index=True
    )
    shown_date = fields.Datetime(
        'Shown Date', 
        default=fields.Datetime.now, 
        required=True, 
        index=True
    )
    
    _sql_constraints = [
        ('unique_announcement_user', 
         'unique(announcement_id, user_id)', 
         'This announcement has already been shown to this user!')
    ]
    
    @api.model
    def cleanup_old_logs(self, days=90):
        """Clean up old announcement logs (optional maintenance method)
        
        Args:
            days (int): Remove logs older than this many days
            
        Returns:
            int: Number of logs deleted
        """
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        old_logs = self.search([('shown_date', '<', cutoff_date)])
        count = len(old_logs)
        old_logs.unlink()
        return count
    
    def name_get(self):
        """Custom name display for logs"""
        result = []
        for record in self:
            name = f"{record.announcement_id.name} - {record.user_id.name} ({record.shown_date})"
            result.append((record.id, name))
        return result