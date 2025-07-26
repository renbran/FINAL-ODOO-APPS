# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DigestDigest(models.Model):
    _inherit = 'digest.digest'
    
    @api.model
    def _get_digest_template(self):
        """Override to use custom template without Odoo branding"""
        template = super()._get_digest_template()
        
        # Replace Odoo references in digest templates
        company = self.env.company
        if company.replace_odoo_branding and company.white_label_name:
            if hasattr(template, 'body_html') and template.body_html:
                template.body_html = template.body_html.replace(
                    'Powered by Odoo', 
                    f'Powered by {company.white_label_name}'
                )
        
        return template
    
    def _get_digest_intro(self):
        """Override digest intro to remove Odoo branding"""
        intro = super()._get_digest_intro()
        company = self.env.company
        
        if company.replace_odoo_branding and company.white_label_name:
            intro = intro.replace('Odoo', company.white_label_name)
            
        return intro
