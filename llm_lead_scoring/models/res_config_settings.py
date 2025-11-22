# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # LLM Provider Settings
    llm_provider_id = fields.Many2one(
        'llm.provider',
        string='Default LLM Provider',
        config_parameter='llm_lead_scoring.default_provider_id',
    )

    # Auto-enrichment Settings
    auto_enrich_enabled = fields.Boolean(
        string='Enable Auto-Enrichment',
        config_parameter='llm_lead_scoring.auto_enrich_enabled',
        help='Automatically enrich leads using scheduled action',
    )

    auto_enrich_new_leads = fields.Boolean(
        string='Auto-Enrich New Leads',
        config_parameter='llm_lead_scoring.auto_enrich_new_leads',
        help='Automatically enrich leads when they are created',
    )

    auto_enrich_on_update = fields.Boolean(
        string='Auto-Enrich on Update',
        config_parameter='llm_lead_scoring.auto_enrich_on_update',
        help='Re-enrich leads when key fields are updated',
    )

    # Research Settings
    enable_customer_research = fields.Boolean(
        string='Enable Customer Research',
        config_parameter='llm_lead_scoring.enable_customer_research',
        default=True,
        help='Use LLM to research customers from public sources',
    )

    # Scoring Weights
    weight_completeness = fields.Float(
        string='Completeness Weight (%)',
        config_parameter='llm_lead_scoring.weight_completeness',
        default=30.0,
        help='Weight of information completeness in final score',
    )

    weight_clarity = fields.Float(
        string='Clarity Weight (%)',
        config_parameter='llm_lead_scoring.weight_clarity',
        default=40.0,
        help='Weight of requirement clarity in final score',
    )

    weight_engagement = fields.Float(
        string='Engagement Weight (%)',
        config_parameter='llm_lead_scoring.weight_engagement',
        default=30.0,
        help='Weight of engagement level in final score',
    )

    @api.onchange('weight_completeness', 'weight_clarity', 'weight_engagement')
    def _onchange_weights(self):
        """Ensure weights sum to 100%"""
        total = self.weight_completeness + self.weight_clarity + self.weight_engagement
        if abs(total - 100.0) > 0.01 and total > 0:
            # Auto-adjust to ensure 100%
            ratio = 100.0 / total
            self.weight_completeness = round(self.weight_completeness * ratio, 2)
            self.weight_clarity = round(self.weight_clarity * ratio, 2)
            self.weight_engagement = round(self.weight_engagement * ratio, 2)
