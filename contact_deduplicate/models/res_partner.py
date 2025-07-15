# -*- coding: utf-8 -*-

from odoo import models, fields, api
from difflib import SequenceMatcher
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    duplicate_contact_ids = fields.One2many(
        'contact.duplicate', 'partner_id',
        string='Potential Duplicates'
    )
    duplicate_count = fields.Integer(
        string='Duplicate Count',
        compute='_compute_duplicate_count'
    )
    is_duplicate_checked = fields.Boolean(
        string='Duplicate Checked',
        default=False,
        help="Whether this contact has been checked for duplicates"
    )
    merge_history_ids = fields.One2many(
        'contact.merge.history', 'master_partner_id',
        string='Merge History'
    )

    @api.depends('duplicate_contact_ids')
    def _compute_duplicate_count(self):
        for record in self:
            record.duplicate_count = len(record.duplicate_contact_ids)

    def action_find_duplicates(self):
        """Find potential duplicates for this contact"""
        self.ensure_one()
        
        # Clear existing duplicates for this partner
        self.duplicate_contact_ids.unlink()
        
        # Search for potential duplicates
        duplicates = self._find_potential_duplicates()
        
        # Create duplicate records
        for duplicate in duplicates:
            self.env['contact.duplicate'].create({
                'partner_id': self.id,
                'duplicate_partner_id': duplicate['partner_id'],
                'similarity_score': duplicate['score'],
                'matching_fields': duplicate['matching_fields'],
            })
        
        self.is_duplicate_checked = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Potential Duplicates',
            'res_model': 'contact.duplicate',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def _find_potential_duplicates(self):
        """Find potential duplicates based on various criteria"""
        duplicates = []
        
        # Skip if no name
        if not self.name:
            return duplicates
        
        # Search domain excluding self
        domain = [
            ('id', '!=', self.id),
            ('is_company', '=', self.is_company),
            ('active', '=', True)
        ]
        
        potential_partners = self.env['res.partner'].search(domain)
        
        for partner in potential_partners:
            score, matching_fields = self._calculate_similarity(partner)
            
            # Only consider as duplicate if similarity is above threshold
            if score >= 0.7:  # 70% similarity threshold
                duplicates.append({
                    'partner_id': partner.id,
                    'score': score,
                    'matching_fields': matching_fields
                })
        
        # Sort by similarity score (highest first)
        duplicates.sort(key=lambda x: x['score'], reverse=True)
        
        return duplicates

    def _calculate_similarity(self, other_partner):
        """Calculate similarity score between two partners"""
        scores = []
        matching_fields = []
        
        # Name similarity (weighted heavily)
        if self.name and other_partner.name:
            name_score = self._string_similarity(self.name, other_partner.name)
            scores.append(name_score * 3)  # Weight name heavily
            if name_score > 0.8:
                matching_fields.append('name')
        
        # Email similarity
        if self.email and other_partner.email:
            if self.email.lower() == other_partner.email.lower():
                scores.append(1.0)
                matching_fields.append('email')
            else:
                email_score = self._string_similarity(self.email, other_partner.email)
                if email_score > 0.8:
                    scores.append(email_score)
                    matching_fields.append('email')
        
        # Phone similarity
        if self.phone and other_partner.phone:
            phone1 = re.sub(r'[^\d]', '', self.phone)
            phone2 = re.sub(r'[^\d]', '', other_partner.phone)
            if phone1 and phone2:
                if phone1 == phone2:
                    scores.append(1.0)
                    matching_fields.append('phone')
                elif len(phone1) >= 7 and len(phone2) >= 7:
                    # Compare last 7 digits
                    if phone1[-7:] == phone2[-7:]:
                        scores.append(0.9)
                        matching_fields.append('phone')
        
        # VAT similarity
        if self.vat and other_partner.vat:
            if self.vat == other_partner.vat:
                scores.append(1.0)
                matching_fields.append('vat')
        
        # Street similarity
        if self.street and other_partner.street:
            street_score = self._string_similarity(self.street, other_partner.street)
            if street_score > 0.8:
                scores.append(street_score)
                matching_fields.append('street')
        
        # City similarity
        if self.city and other_partner.city:
            city_score = self._string_similarity(self.city, other_partner.city)
            if city_score > 0.8:
                scores.append(city_score)
                matching_fields.append('city')
        
        # Calculate final score
        if scores:
            final_score = sum(scores) / len(scores)
            return min(final_score, 1.0), ', '.join(matching_fields)
        
        return 0.0, ''

    def _string_similarity(self, str1, str2):
        """Calculate similarity between two strings using SequenceMatcher"""
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        return SequenceMatcher(None, str1, str2).ratio()

    @api.model
    def find_all_duplicates(self):
        """Find duplicates for all contacts (batch operation)"""
        partners = self.search([('active', '=', True)])
        
        for partner in partners:
            if not partner.is_duplicate_checked:
                partner.action_find_duplicates()
        
        return True

    def action_merge_with_contact(self):
        """Open merge wizard for this contact"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Merge Contacts',
            'res_model': 'contact.merge.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, [self.id])],
                'default_master_partner_id': self.id,
            }
        }
