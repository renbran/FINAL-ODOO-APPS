# -*- coding: utf-8 -*-

from odoo import models, api, _
import re


class MailTemplate(models.Model):
    _inherit = 'mail.template'
    
    @api.model
    def _render_template(self, template_txt, model, res_ids, post_process=False):
        """Override to replace Odoo branding in email templates"""
        result = super()._render_template(template_txt, model, res_ids, post_process)
        
        company = self.env.company
        if company.replace_odoo_branding and company.white_label_name:
            result = self._replace_branding_in_content(result, company.white_label_name)
        
        return result
    
    def _replace_branding_in_content(self, content, white_label_name):
        """Helper method to replace branding in various content types"""
        if isinstance(content, dict):
            for res_id, text in content.items():
                if isinstance(text, str):
                    content[res_id] = self._replace_text_branding(text, white_label_name)
        elif isinstance(content, str):
            content = self._replace_text_branding(content, white_label_name)
        
        return content
    
    def _replace_text_branding(self, text, white_label_name):
        """Replace Odoo branding in text content"""
        if not text or not white_label_name:
            return text
        
        # Replace specific phrases first
        text = text.replace('Powered by Odoo', f'Powered by {white_label_name}')
        text = text.replace('Built with Odoo', f'Built with {white_label_name}')
        
        # Replace standalone "Odoo" words (but not in URLs or technical contexts)
        text = re.sub(r'\bOdoo\b(?![.])', white_label_name, text)
        
        return text