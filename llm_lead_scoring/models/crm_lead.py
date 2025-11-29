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

    def _format_enrichment_note(self, data):
        """Format enrichment data as HTML note"""
        scores = data.get('scores', {})
        analysis = data.get('analysis', {})
        research = data.get('research', '')
        
        # Helper function to format text with proper line breaks
        def format_text(text):
            if not text or text == 'N/A':
                return '<em style="color: #999;">No data available</em>'
            return text.replace('\n', '<br/>').replace('**', '<strong>').replace('**', '</strong>')
        
        # Score color coding
        def get_score_color(score):
            if score >= 70:
                return '#28a745'  # Green
            elif score >= 40:
                return '#ffc107'  # Yellow
            else:
                return '#dc3545'  # Red

        overall_score = scores.get('overall', 0)
        score_color = get_score_color(overall_score)

        html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; color: #333;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px 10px 0 0; color: white; text-align: center;">
                <h2 style="margin: 0; font-size: 24px; font-weight: 600;">🤖 AI Lead Enrichment Report</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">Generated: {data.get('timestamp', '')}</p>
            </div>

            <!-- Overall Score Badge -->
            <div style="background: white; padding: 20px; text-align: center; border-left: 4px solid {score_color}; border-right: 4px solid {score_color};">
                <div style="display: inline-block; background: {score_color}; color: white; padding: 15px 30px; border-radius: 50px; font-size: 18px; font-weight: bold;">
                    Overall Probability: {overall_score:.1f}/100
                </div>
            </div>

            <!-- Detailed Scores -->
            <div style="background: #f8f9fa; padding: 25px; border-left: 4px solid #e9ecef; border-right: 4px solid #e9ecef;">
                <h3 style="color: #495057; margin: 0 0 20px 0; font-size: 18px; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">📊</span> Detailed Scores
                </h3>
                <div style="display: grid; gap: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid {get_score_color(scores.get('completeness', 0))};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: #495057;">Information Completeness</span>
                            <span style="font-size: 18px; font-weight: bold; color: {get_score_color(scores.get('completeness', 0))};">{scores.get('completeness', 0):.1f}%</span>
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid {get_score_color(scores.get('clarity', 0))};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: #495057;">Requirement Clarity</span>
                            <span style="font-size: 18px; font-weight: bold; color: {get_score_color(scores.get('clarity', 0))};">{scores.get('clarity', 0):.1f}%</span>
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid {get_score_color(scores.get('engagement', 0))};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: #495057;">Engagement Level</span>
                            <span style="font-size: 18px; font-weight: bold; color: {get_score_color(scores.get('engagement', 0))};">{scores.get('engagement', 0):.1f}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Analysis Section -->
            <div style="background: white; padding: 25px; border-left: 4px solid #e9ecef; border-right: 4px solid #e9ecef;">
                <h3 style="color: #495057; margin: 0 0 20px 0; font-size: 18px; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">📝</span> Detailed Analysis
                </h3>
                
                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <h4 style="color: #667eea; margin: 0 0 10px 0; font-size: 15px; font-weight: 600;">🔍 Completeness Analysis</h4>
                    <p style="margin: 0; line-height: 1.6; color: #495057;">{format_text(analysis.get('completeness', 'N/A'))}</p>
                </div>

                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <h4 style="color: #667eea; margin: 0 0 10px 0; font-size: 15px; font-weight: 600;">💡 Clarity Analysis</h4>
                    <p style="margin: 0; line-height: 1.6; color: #495057;">{format_text(analysis.get('clarity', 'N/A'))}</p>
                </div>

                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <h4 style="color: #667eea; margin: 0 0 10px 0; font-size: 15px; font-weight: 600;">📈 Engagement Analysis</h4>
                    <p style="margin: 0; line-height: 1.6; color: #495057;">{format_text(analysis.get('engagement', 'N/A'))}</p>
                </div>

                <div style="padding: 20px; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border-radius: 8px; border: 2px solid #667eea;">
                    <h4 style="color: #667eea; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🎯 AI Recommendation</h4>
                    <div style="line-height: 1.8; color: #495057;">{format_text(analysis.get('llm_final', 'N/A'))}</div>
                </div>
            </div>
        """

        if research:
            html += f"""
            <!-- Customer Research Section -->
            <div style="background: white; padding: 25px; border-radius: 0 0 10px 10px; border-left: 4px solid #e9ecef; border-right: 4px solid #e9ecef; border-bottom: 4px solid #e9ecef;">
                <h3 style="color: #495057; margin: 0 0 20px 0; font-size: 18px; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">🔍</span> Customer Research
                </h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8; line-height: 1.8; color: #495057;">
                    {format_text(research)}
                </div>
            </div>
            """
        else:
            html += """
            </div>
            """

        return html

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
