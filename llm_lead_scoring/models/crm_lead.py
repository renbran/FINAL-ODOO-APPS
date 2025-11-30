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
        """Format enrichment data as professional HTML report for Odoo display.
        
        Uses table-based layouts for maximum email/widget compatibility.
        Avoids flexbox and gradients which don't render properly in Odoo mail.
        """
        scores = data.get('scores', {})
        analysis = data.get('analysis', {})
        research = data.get('research', '')

        def format_text(text):
            """Clean and format text for HTML display"""
            if not text or text == 'N/A':
                return '<em style="color: #888888;">No data available</em>'
            # Convert markdown-style formatting to HTML
            text = str(text)
            text = text.replace('**', '')
            text = text.replace('\n\n', '</p><p style="margin: 8px 0;">')
            text = text.replace('\n', '<br/>')
            text = text.replace('\t*', '<br/>• ')
            text = text.replace('* ', '• ')
            return text.strip()
        
        def get_score_color(score):
            """Get color based on score value"""
            if score >= 70:
                return '#28a745', '#d4edda', '🟢'  # Green
            elif score >= 40:
                return '#ffc107', '#fff3cd', '🟡'  # Yellow  
            else:
                return '#dc3545', '#f8d7da', '🔴'  # Red
        
        def format_score_cell(score, label):
            """Generate a single score cell for table layout"""
            color, bg_color, icon = get_score_color(score)
            return f'''
                <td style="padding: 10px; text-align: center; background-color: {bg_color}; border-left: 4px solid {color}; vertical-align: top;">
                    <div style="color: #666666; font-size: 11px; margin-bottom: 4px;">{label}</div>
                    <div style="color: {color}; font-size: 22px; font-weight: bold;">{score:.0f}</div>
                    <div style="color: #888888; font-size: 11px;">/100 {icon}</div>
                </td>'''

        overall = scores.get('overall', 0)
        completeness = scores.get('completeness', 0)
        clarity = scores.get('clarity', 0)
        engagement = scores.get('engagement', 0)

        # Determine overall score status
        overall_color, overall_bg, overall_icon = get_score_color(overall)
        
        timestamp = data.get('timestamp', '')
        if timestamp:
            timestamp = timestamp[:19].replace('T', ' ')

        # Build HTML report using table-based layout for compatibility
        report = f'''
<div style="font-family: Arial, Helvetica, sans-serif; max-width: 100%; margin: 0; padding: 0;">
    
    <!-- Header -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px;">
        <tr>
            <td style="background-color: #6366f1; padding: 16px 20px; border-radius: 8px;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="color: #ffffff; font-size: 18px; font-weight: bold;">
                            🤖 AI Lead Enrichment Report
                        </td>
                    </tr>
                    <tr>
                        <td style="color: #e0e0ff; font-size: 12px; padding-top: 4px;">
                            Generated: {timestamp}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    
    <!-- Overall Score Highlight -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px;">
        <tr>
            <td style="background-color: {overall_bg}; border: 2px solid {overall_color}; border-radius: 8px; padding: 16px; text-align: center;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center;">
                            <div style="color: #333333; font-size: 14px; font-weight: bold; margin-bottom: 8px;">OVERALL PROBABILITY SCORE</div>
                            <div style="color: {overall_color}; font-size: 42px; font-weight: bold; line-height: 1;">{overall:.0f}%</div>
                            <div style="color: #666666; font-size: 12px; margin-top: 4px;">{overall_icon} {'High' if overall >= 70 else 'Medium' if overall >= 40 else 'Low'} Priority Lead</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    
    <!-- Score Breakdown -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px; background-color: #f8f9fa; border-radius: 8px;">
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #dee2e6;">
                <strong style="color: #333333; font-size: 14px;">📊 Score Breakdown</strong>
            </td>
        </tr>
        <tr>
            <td style="padding: 12px;">
                <table width="100%" cellpadding="0" cellspacing="8">
                    <tr>
                        {format_score_cell(completeness, 'Completeness')}
                        {format_score_cell(clarity, 'Clarity')}
                        {format_score_cell(engagement, 'Engagement')}
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    
    <!-- Detailed Analysis -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px; border: 1px solid #e9ecef; border-radius: 8px;">
        <tr>
            <td style="background-color: #f8f9fa; padding: 12px 16px; border-bottom: 1px solid #e9ecef; border-radius: 8px 8px 0 0;">
                <strong style="color: #333333; font-size: 14px;">📝 Detailed Analysis</strong>
            </td>
        </tr>
        <tr>
            <td style="padding: 16px;">
                <!-- Completeness Analysis -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px;">
                    <tr>
                        <td style="padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;">
                            <div style="color: #495057; font-size: 13px; font-weight: bold; margin-bottom: 6px;">🔍 Completeness Analysis</div>
                            <div style="color: #666666; font-size: 13px; line-height: 1.6;">{format_text(analysis.get('completeness', 'N/A'))}</div>
                        </td>
                    </tr>
                </table>
                
                <!-- Clarity Analysis -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px;">
                    <tr>
                        <td style="padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;">
                            <div style="color: #495057; font-size: 13px; font-weight: bold; margin-bottom: 6px;">💡 Clarity Analysis</div>
                            <div style="color: #666666; font-size: 13px; line-height: 1.6;">{format_text(analysis.get('clarity', 'N/A'))}</div>
                        </td>
                    </tr>
                </table>
                
                <!-- Engagement Analysis -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <div style="color: #495057; font-size: 13px; font-weight: bold; margin-bottom: 6px;">📈 Engagement Analysis</div>
                            <div style="color: #666666; font-size: 13px; line-height: 1.6;">{format_text(analysis.get('engagement', 'N/A'))}</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    
    <!-- AI Recommendation -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 16px; background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;">
        <tr>
            <td style="padding: 16px;">
                <div style="color: #856404; font-size: 14px; font-weight: bold; margin-bottom: 10px;">🎯 AI Recommendation</div>
                <div style="color: #856404; font-size: 13px; line-height: 1.6;">{format_text(analysis.get('llm_final', 'N/A'))}</div>
            </td>
        </tr>
    </table>'''

        # Add research section if available
        if research and research.strip():
            report += f'''
    
    <!-- Customer Research -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 8px;">
        <tr>
            <td style="padding: 16px;">
                <div style="color: #004085; font-size: 14px; font-weight: bold; margin-bottom: 10px;">🌐 Customer Research</div>
                <div style="color: #004085; font-size: 12px; line-height: 1.5;">{format_text(research)}</div>
            </td>
        </tr>
    </table>'''

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
