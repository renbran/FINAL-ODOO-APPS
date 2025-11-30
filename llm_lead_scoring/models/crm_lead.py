# -*- coding: utf-8 -*-

import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Check if module is properly installed before adding fields
    _auto = True  # Ensure automatic table creation
    
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
        index=True,
    )

    ai_enrichment_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Enrichment Status', default='pending', readonly=True, index=True)

    ai_analysis_summary = fields.Text(
        string='AI Analysis Summary',
        readonly=True,
        help='Summary of AI analysis and recommendations',
    )
    
    ai_enrichment_report = fields.Text(
        string='AI Enrichment Report',
        readonly=True,
        help='Complete plain text enrichment report with scores and analysis',
    )

    # Configuration
    auto_enrich = fields.Boolean(
        string='Auto Enrich',
        default=True,
        help='Automatically enrich this lead with AI when key fields change',
        index=True,
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
            # Let Odoo handle transaction management

            llm_service = self.env['llm.service']

            # 1. Calculate AI Probability Score
            _logger.info("Calculating AI score for lead: %s", self.name)
            scoring_result = llm_service.calculate_ai_probability_score(self)

            # 2. Research Customer (if enabled in settings)
            research_result = ""
            enable_research = llm_service._get_config_bool('llm_lead_scoring.enable_customer_research', 'True')

            if enable_research:
                _logger.info("Researching customer for lead: %s", self.name)
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

            # 4. Format plain text enrichment report
            plain_text_report = self._format_plain_text_report(enrichment_data)

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
                'ai_enrichment_report': plain_text_report,
            })

            _logger.info("Successfully enriched lead %s with AI score: %.2f",
                        self.name, scoring_result['calculated_score'])

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
            _logger.error("Error enriching lead %s: %s", self.id, str(e), exc_info=True)
            self.write({
                'ai_enrichment_status': 'failed',
                'ai_analysis_summary': 'Enrichment failed: %s' % str(e),
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

    def _format_plain_text_report(self, data):
        """Format enrichment data as pure plain text report"""
        scores = data.get('scores', {})
        analysis = data.get('analysis', {})
        research = data.get('research', '')

        # Helper function to format text
        def format_text(text):
            """Clean text for plain display"""
            if not text or text == 'N/A':
                return 'No data available'
            # Remove markdown formatting
            text = text.replace('**', '')
            text = text.replace('*', '')
            return text.strip()
        
        # Get score indicator
        def get_score_indicator(score):
            if score >= 70:
                return '🟢 HIGH'
            elif score >= 40:
                return '🟡 MEDIUM'
            else:
                return '🔴 LOW'

        overall_score = scores.get('overall', 0)
        completeness_score = scores.get('completeness', 0)
        clarity_score = scores.get('clarity', 0)
        engagement_score = scores.get('engagement', 0)

        # Pure plain text format - no HTML
        report = f"""================================================================================
🤖 AI LEAD ENRICHMENT REPORT
================================================================================
Generated: {data.get('timestamp', '')}

================================================================================
📊 PROBABILITY SCORES
================================================================================

Overall Probability:      {overall_score:.1f}/100  {get_score_indicator(overall_score)}
Information Completeness: {completeness_score:.1f}/100  {get_score_indicator(completeness_score)}
Requirement Clarity:      {clarity_score:.1f}/100  {get_score_indicator(clarity_score)}
Engagement Level:         {engagement_score:.1f}/100  {get_score_indicator(engagement_score)}

================================================================================
📝 DETAILED ANALYSIS
================================================================================

🔍 COMPLETENESS ANALYSIS:
{format_text(analysis.get('completeness', 'N/A'))}

💡 CLARITY ANALYSIS:
{format_text(analysis.get('clarity', 'N/A'))}

📈 ENGAGEMENT ANALYSIS:
{format_text(analysis.get('engagement', 'N/A'))}

================================================================================
🎯 AI RECOMMENDATION
================================================================================
{format_text(analysis.get('llm_final', 'N/A'))}
"""

        if research:
            report += f"""
================================================================================
🔍 CUSTOMER RESEARCH
================================================================================
{format_text(research)}
"""

        report += """
================================================================================
"""

        return report

    @api.model
    def _cron_enrich_leads(self):
        """Scheduled action to enrich leads automatically"""
        llm_service = self.env['llm.service']
        auto_enrich_enabled = llm_service._get_config_bool('llm_lead_scoring.auto_enrich_enabled', 'False')

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

        _logger.info("Found %d leads to enrich", len(leads_to_enrich))

        for lead in leads_to_enrich:
            try:
                lead._enrich_lead()
                # Let Odoo handle transaction management
            except Exception as e:
                _logger.error("Failed to enrich lead %s: %s", lead.id, str(e))
                continue

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger auto-enrichment"""
        leads = super(CrmLead, self).create(vals_list)

        llm_service = self.env['llm.service']
        auto_enrich_new = llm_service._get_config_bool('llm_lead_scoring.auto_enrich_new_leads', 'False')

        if auto_enrich_new:
            for lead in leads:
                if lead.auto_enrich and lead.type == 'opportunity':
                    # Mark as pending for cron to process
                    # This avoids blocking lead creation and doesn't require queue_job
                    lead.write({'ai_enrichment_status': 'pending'})

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
            llm_service = self.env['llm.service']
            auto_enrich_update = llm_service._get_config_bool('llm_lead_scoring.auto_enrich_on_update', 'False')

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
