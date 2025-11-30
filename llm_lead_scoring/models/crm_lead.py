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
    
    ai_enrichment_report = fields.Html(
        string='AI Enrichment Report',
        readonly=True,
        sanitize=False,
        help='Complete HTML enrichment report with scores and analysis',
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
        """Format enrichment data as HTML report for Odoo chatter display"""
        scores = data.get('scores', {})
        analysis = data.get('analysis', {})
        research = data.get('research', '')

        def format_text(text):
            """Clean and format text for HTML display"""
            if not text or text == 'N/A':
                return '<em style="color: #888;">No data available</em>'
            # Convert markdown-style formatting to HTML
            text = text.replace('**', '')
            text = text.replace('\n\n', '</p><p>')
            text = text.replace('\n', '<br/>')
            text = text.replace('\t*', '<br/>•')
            text = text.replace('* ', '• ')
            return text.strip()
        
        def get_score_badge(score, label):
            """Generate score badge with color"""
            if score >= 70:
                color = '#28a745'  # Green
                icon = '🟢'
            elif score >= 40:
                color = '#ffc107'  # Yellow  
                icon = '🟡'
            else:
                color = '#dc3545'  # Red
                icon = '🔴'
            return f'''<div style="display: inline-block; margin: 5px 10px 5px 0; padding: 8px 15px; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
                <span style="color: #666; font-size: 11px; display: block;">{label}</span>
                <strong style="color: {color}; font-size: 18px;">{score:.0f}</strong><span style="color: #888; font-size: 12px;">/100</span> {icon}
            </div>'''

        overall = scores.get('overall', 0)
        completeness = scores.get('completeness', 0)
        clarity = scores.get('clarity', 0)
        engagement = scores.get('engagement', 0)

        # Build HTML report
        report = f'''
<div style="font-family: Arial, sans-serif; max-width: 100%; padding: 0;">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="margin: 0 0 5px 0; font-size: 16px;">🤖 AI Lead Enrichment Report</h3>
        <small style="opacity: 0.9;">Generated: {data.get('timestamp', '')[:19].replace('T', ' ')}</small>
    </div>
    
    <!-- Scores Section -->
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #333; font-size: 14px; border-bottom: 1px solid #dee2e6; padding-bottom: 8px;">📊 Probability Scores</h4>
        <div style="display: flex; flex-wrap: wrap;">
            {get_score_badge(overall, 'Overall Score')}
            {get_score_badge(completeness, 'Completeness')}
            {get_score_badge(clarity, 'Clarity')}
            {get_score_badge(engagement, 'Engagement')}
        </div>
    </div>
    
    <!-- Analysis Section -->
    <div style="background: #fff; border: 1px solid #e9ecef; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="margin: 0; padding: 12px 15px; background: #f8f9fa; border-bottom: 1px solid #e9ecef; color: #333; font-size: 14px; border-radius: 8px 8px 0 0;">📝 Detailed Analysis</h4>
        
        <div style="padding: 15px;">
            <!-- Completeness -->
            <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0;">
                <strong style="color: #495057; font-size: 12px;">🔍 Completeness:</strong>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 13px; line-height: 1.5;">{format_text(analysis.get('completeness', 'N/A'))}</p>
            </div>
            
            <!-- Clarity -->
            <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0;">
                <strong style="color: #495057; font-size: 12px;">💡 Clarity:</strong>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 13px; line-height: 1.5;">{format_text(analysis.get('clarity', 'N/A'))}</p>
            </div>
            
            <!-- Engagement -->
            <div style="margin-bottom: 0;">
                <strong style="color: #495057; font-size: 12px;">📈 Engagement:</strong>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 13px; line-height: 1.5;">{format_text(analysis.get('engagement', 'N/A'))}</p>
            </div>
        </div>
    </div>
    
    <!-- AI Recommendation -->
    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%); border: 1px solid #f0ad4e; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #856404; font-size: 14px;">🎯 AI Recommendation</h4>
        <div style="color: #856404; font-size: 13px; line-height: 1.6;">{format_text(analysis.get('llm_final', 'N/A'))}</div>
    </div>'''

        # Add research section if available
        if research and research.strip():
            report += f'''
    <!-- Customer Research -->
    <div style="background: #e7f3ff; border: 1px solid #b8daff; border-radius: 8px; padding: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #004085; font-size: 14px;">🌐 Customer Research</h4>
        <div style="color: #004085; font-size: 12px; line-height: 1.5; max-height: 300px; overflow-y: auto;">{format_text(research)}</div>
    </div>'''

        report += '''
</div>'''

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
