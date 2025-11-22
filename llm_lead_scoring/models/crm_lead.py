# -*- coding: utf-8 -*-

import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # AI Scoring Fields
    ai_probability_score = fields.Float(
        string='AI Probability Score',
        readonly=True,
        help='AI-calculated lead probability score (0-100)',
        tracking=True,
    )

    ai_completeness_score = fields.Float(
        string='Completeness Score',
        readonly=True,
        help='Score based on how complete the lead information is',
    )

    ai_clarity_score = fields.Float(
        string='Requirement Clarity Score',
        readonly=True,
        help='Score based on how clear the customer requirements are',
    )

    ai_engagement_score = fields.Float(
        string='Engagement Score',
        readonly=True,
        help='Score based on activity and interaction logs',
    )

    # Enrichment Fields
    ai_enrichment_data = fields.Text(
        string='AI Enrichment Data',
        help='JSON data containing AI research and insights',
    )

    ai_last_enrichment_date = fields.Datetime(
        string='Last AI Enrichment',
        readonly=True,
    )

    ai_enrichment_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Enrichment Status', default='pending', readonly=True)

    ai_analysis_summary = fields.Text(
        string='AI Analysis Summary',
        readonly=True,
        help='Summary of AI analysis and recommendations',
    )

    # Configuration
    auto_enrich = fields.Boolean(
        string='Auto Enrich',
        default=True,
        help='Automatically enrich this lead with AI when key fields change',
    )

    # Computed field for visual indicator
    ai_score_color = fields.Integer(
        string='Score Color',
        compute='_compute_ai_score_color',
        store=False,
    )

    @api.depends('ai_probability_score')
    def _compute_ai_score_color(self):
        """Compute color for kanban view based on score"""
        for lead in self:
            if lead.ai_probability_score >= 70:
                lead.ai_score_color = 10  # Green
            elif lead.ai_probability_score >= 40:
                lead.ai_score_color = 3   # Yellow
            else:
                lead.ai_score_color = 1   # Red

    def action_enrich_with_ai(self):
        """Manual action to enrich lead with AI"""
        self.ensure_one()

        if self.ai_enrichment_status == 'processing':
            raise UserError(_('Lead enrichment is already in progress.'))

        return self._enrich_lead()

    def _enrich_lead(self):
        """Internal method to enrich lead with AI"""
        self.ensure_one()

        try:
            self.write({'ai_enrichment_status': 'processing'})
            self.env.cr.commit()  # Commit status update

            llm_service = self.env['llm.service']

            # 1. Calculate AI Probability Score
            _logger.info(f"Calculating AI score for lead: {self.name}")
            scoring_result = llm_service.calculate_ai_probability_score(self)

            # 2. Research Customer (if enabled in settings)
            research_result = ""
            config = self.env['ir.config_parameter'].sudo()
            enable_research = config.get_param('llm_lead_scoring.enable_customer_research', 'True') == 'True'

            if enable_research:
                _logger.info(f"Researching customer for lead: {self.name}")
                research_result = llm_service.research_customer(self)

            # 3. Prepare enrichment data
            enrichment_data = {
                'timestamp': fields.Datetime.now().isoformat(),
                'scores': {
                    'overall': scoring_result['calculated_score'],
                    'completeness': scoring_result['completeness_score'],
                    'clarity': scoring_result['clarity_score'],
                    'engagement': scoring_result['engagement_score'],
                },
                'analysis': {
                    'completeness': scoring_result['completeness_analysis'],
                    'clarity': scoring_result['clarity_analysis'],
                    'engagement': scoring_result['engagement_analysis'],
                    'llm_final': scoring_result['llm_analysis'],
                },
                'research': research_result,
            }

            # 4. Create internal note with findings
            note_body = self._format_enrichment_note(enrichment_data)
            self.message_post(
                body=note_body,
                subject='AI Lead Enrichment',
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # 5. Update lead fields
            self.write({
                'ai_probability_score': scoring_result['calculated_score'],
                'ai_completeness_score': scoring_result['completeness_score'],
                'ai_clarity_score': scoring_result['clarity_score'],
                'ai_engagement_score': scoring_result['engagement_score'],
                'ai_enrichment_data': json.dumps(enrichment_data, indent=2),
                'ai_last_enrichment_date': fields.Datetime.now(),
                'ai_enrichment_status': 'completed',
                'ai_analysis_summary': scoring_result['llm_analysis'],
            })

            _logger.info(f"Successfully enriched lead {self.name} with AI score: {scoring_result['calculated_score']}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Lead enriched successfully with AI score: %.2f') % scoring_result['calculated_score'],
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Error enriching lead {self.id}: {str(e)}", exc_info=True)
            self.write({
                'ai_enrichment_status': 'failed',
                'ai_analysis_summary': f'Enrichment failed: {str(e)}',
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to enrich lead: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def _format_enrichment_note(self, data):
        """Format enrichment data as HTML note"""
        scores = data.get('scores', {})
        analysis = data.get('analysis', {})
        research = data.get('research', '')

        html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h3 style="color: #875A7B;">🤖 AI Lead Enrichment Report</h3>
            <p><strong>Generated:</strong> {data.get('timestamp', '')}</p>

            <h4 style="color: #875A7B;">📊 AI Probability Scores</h4>
            <ul>
                <li><strong>Overall Probability:</strong> {scores.get('overall', 0):.2f}/100</li>
                <li><strong>Information Completeness:</strong> {scores.get('completeness', 0):.2f}/100</li>
                <li><strong>Requirement Clarity:</strong> {scores.get('clarity', 0):.2f}/100</li>
                <li><strong>Engagement Level:</strong> {scores.get('engagement', 0):.2f}/100</li>
            </ul>

            <h4 style="color: #875A7B;">📝 Analysis</h4>

            <p><strong>Completeness Analysis:</strong><br/>
            {analysis.get('completeness', 'N/A')}</p>

            <p><strong>Clarity Analysis:</strong><br/>
            {analysis.get('clarity', 'N/A')}</p>

            <p><strong>Engagement Analysis:</strong><br/>
            {analysis.get('engagement', 'N/A')}</p>

            <p><strong>AI Recommendation:</strong><br/>
            {analysis.get('llm_final', 'N/A')}</p>
        """

        if research:
            html += f"""
            <h4 style="color: #875A7B;">🔍 Customer Research</h4>
            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                {research.replace(chr(10), '<br/>')}
            </div>
            """

        html += "</div>"
        return html

    @api.model
    def _cron_enrich_leads(self):
        """Scheduled action to enrich leads automatically"""
        config = self.env['ir.config_parameter'].sudo()
        auto_enrich_enabled = config.get_param('llm_lead_scoring.auto_enrich_enabled', 'False') == 'True'

        if not auto_enrich_enabled:
            _logger.info("Auto-enrichment is disabled in settings")
            return

        # Find leads that need enrichment
        leads_to_enrich = self.search([
            ('auto_enrich', '=', True),
            ('ai_enrichment_status', 'in', ['pending', 'failed']),
            ('type', '=', 'opportunity'),  # Only enrich opportunities
            ('active', '=', True),
        ], limit=50)  # Limit to avoid overload

        _logger.info(f"Found {len(leads_to_enrich)} leads to enrich")

        for lead in leads_to_enrich:
            try:
                lead._enrich_lead()
                # Add delay between requests to avoid rate limiting
                self.env.cr.commit()
            except Exception as e:
                _logger.error(f"Failed to enrich lead {lead.id}: {str(e)}")
                continue

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger auto-enrichment"""
        leads = super(CrmLead, self).create(vals_list)

        config = self.env['ir.config_parameter'].sudo()
        auto_enrich_new = config.get_param('llm_lead_scoring.auto_enrich_new_leads', 'False') == 'True'

        if auto_enrich_new:
            for lead in leads:
                if lead.auto_enrich and lead.type == 'opportunity':
                    # Enrich in background
                    lead.with_delay()._enrich_lead()

        return leads

    def write(self, vals):
        """Override write to trigger re-enrichment on key field changes"""
        result = super(CrmLead, self).write(vals)

        # Fields that trigger re-enrichment
        trigger_fields = [
            'partner_name', 'contact_name', 'email_from', 'phone',
            'description', 'expected_revenue', 'probability'
        ]

        if any(field in vals for field in trigger_fields):
            config = self.env['ir.config_parameter'].sudo()
            auto_enrich_update = config.get_param('llm_lead_scoring.auto_enrich_on_update', 'False') == 'True'

            if auto_enrich_update:
                for lead in self:
                    if lead.auto_enrich and lead.type == 'opportunity':
                        # Mark as pending for next cron run
                        lead.write({'ai_enrichment_status': 'pending'})

        return result

    def action_view_enrichment_data(self):
        """Action to view enrichment data in a formatted way"""
        self.ensure_one()

        if not self.ai_enrichment_data:
            raise UserError(_('No enrichment data available for this lead.'))

        try:
            data = json.loads(self.ai_enrichment_data)
            formatted_data = json.dumps(data, indent=2)
        except json.JSONDecodeError:
            formatted_data = self.ai_enrichment_data

        return {
            'name': _('AI Enrichment Data'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'show_enrichment_data': True},
        }
