# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
import logging

_logger = logging.getLogger(__name__)


class AssessmentCandidate(models.Model):
    _name = 'assessment.candidate'
    _description = 'Assessment Candidate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'submission_date desc, overall_score desc'
    _rec_name = 'full_name'

    # Personal Information
    full_name = fields.Char(
        string='Full Name',
        required=True,
        tracking=True,
        index=True
    )
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True,
        index=True
    )
    phone = fields.Char(
        string='Phone',
        tracking=True
    )
    location = fields.Char(
        string='Location',
        tracking=True
    )
    
    # Experience Levels
    odoo_experience = fields.Selection([
        ('none', 'No Experience'),
        ('0-2', '0-2 years'),
        ('2-5', '2-5 years'),
        ('5+', '5+ years'),
    ], string='Odoo Experience', required=True, tracking=True)
    
    sales_experience = fields.Selection([
        ('0-1', '0-1 years'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5+', '5+ years'),
    ], string='Sales Experience', required=True, tracking=True)
    
    # Submission Metadata
    submission_date = fields.Datetime(
        string='Submission Date',
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )
    ip_address = fields.Char(string='IP Address', readonly=True)
    user_agent = fields.Text(string='User Agent', readonly=True)
    
    # Status Management
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('ai_scored', 'AI Scored'),
        ('under_review', 'Under Human Review'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ], string='Status', default='draft', required=True, tracking=True, index=True)
    
    # Access Token for Portal
    access_token = fields.Char(
        string='Security Token',
        copy=False,
        readonly=True,
        index=True
    )
    
    # Relationships
    response_id = fields.Many2one(
        'assessment.response',
        string='Assessment Response',
        ondelete='cascade',
        readonly=True
    )
    ai_score_id = fields.Many2one(
        'assessment.ai.score',
        string='AI Score',
        ondelete='cascade',
        readonly=True
    )
    human_review_id = fields.Many2one(
        'assessment.human.review',
        string='Human Review',
        ondelete='cascade',
        readonly=True
    )
    ranking_id = fields.Many2one(
        'assessment.ranking',
        string='Ranking',
        ondelete='cascade',
        readonly=True
    )
    
    # Computed Scores
    overall_score = fields.Float(
        string='Overall Score',
        compute='_compute_overall_score',
        store=True,
        tracking=True,
        index=True
    )
    technical_score = fields.Float(
        string='Technical Score',
        compute='_compute_category_scores',
        store=True
    )
    sales_score = fields.Float(
        string='Sales Score',
        compute='_compute_category_scores',
        store=True
    )
    communication_score = fields.Float(
        string='Communication Score',
        compute='_compute_category_scores',
        store=True
    )
    learning_score = fields.Float(
        string='Learning Agility Score',
        compute='_compute_category_scores',
        store=True
    )
    cultural_fit_score = fields.Float(
        string='Cultural Fit Score',
        compute='_compute_category_scores',
        store=True
    )
    
    # Ranking
    overall_rank = fields.Integer(
        string='Overall Rank',
        compute='_compute_ranking',
        store=True,
        index=True
    )
    percentile = fields.Float(
        string='Percentile',
        compute='_compute_ranking',
        store=True
    )
    
    # Smart Buttons Count
    audit_log_count = fields.Integer(
        string='Audit Logs',
        compute='_compute_audit_log_count'
    )
    
    # Flags
    is_duplicate = fields.Boolean(
        string='Possible Duplicate',
        compute='_compute_duplicate_check',
        store=True
    )
    has_red_flags = fields.Boolean(
        string='Has Red Flags',
        compute='_compute_red_flags',
        store=True
    )
    
    # Notes
    internal_notes = fields.Text(string='Internal Notes')

    # SQL constraints removed to allow duplicate submissions
    # Users can now submit multiple assessments with the same email
    _sql_constraints = []

    @api.model
    def create(self, vals):
        # Generate access token
        if not vals.get('access_token'):
            vals['access_token'] = self._generate_access_token()
        
        # Log submission
        candidate = super(AssessmentCandidate, self).create(vals)
        self._log_audit(candidate, 'create', 'Candidate submitted assessment')
        
        return candidate

    def write(self, vals):
        # Track status changes
        if 'status' in vals:
            for record in self:
                old_status = record.status
                self._log_audit(record, 'status_change', 
                              f'Status changed from {old_status} to {vals["status"]}')
        
        return super(AssessmentCandidate, self).write(vals)

    @api.depends('human_review_id.overall_score', 'ai_score_id.overall_score')
    def _compute_overall_score(self):
        """Final score prioritizes human review over AI score"""
        for record in self:
            if record.human_review_id and record.human_review_id.overall_score:
                record.overall_score = record.human_review_id.overall_score
            elif record.ai_score_id and record.ai_score_id.overall_score:
                record.overall_score = record.ai_score_id.overall_score
            else:
                record.overall_score = 0.0

    @api.depends('human_review_id', 'ai_score_id')
    def _compute_category_scores(self):
        """Get category scores from human review or AI"""
        for record in self:
            source = record.human_review_id if record.human_review_id else record.ai_score_id
            if source:
                record.technical_score = source.technical_score or 0.0
                record.sales_score = source.sales_score or 0.0
                record.communication_score = source.communication_score or 0.0
                record.learning_score = source.learning_score or 0.0
                record.cultural_fit_score = source.cultural_fit_score or 0.0
            else:
                record.technical_score = 0.0
                record.sales_score = 0.0
                record.communication_score = 0.0
                record.learning_score = 0.0
                record.cultural_fit_score = 0.0

    @api.depends('overall_score')
    def _compute_ranking(self):
        """Calculate rank based on overall score"""
        all_candidates = self.search([('overall_score', '>', 0)], order='overall_score desc')
        total_count = len(all_candidates)
        
        for idx, candidate in enumerate(all_candidates, start=1):
            if candidate.id in self.ids:
                candidate.overall_rank = idx
                candidate.percentile = ((total_count - idx + 1) / total_count * 100) if total_count else 0

    def _compute_audit_log_count(self):
        """Count audit logs for smart button"""
        for record in self:
            record.audit_log_count = self.env['assessment.audit.log'].search_count([
                ('candidate_id', '=', record.id)
            ])

    @api.depends('email')
    def _compute_duplicate_check(self):
        """Check for potential duplicate submissions"""
        for record in self:
            if record.email:
                domain = [('email', '=', record.email)]
                # Only exclude current record if it has a real ID (not NewId for unsaved records)
                if record.id and isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                duplicate_count = self.search_count(domain)
                record.is_duplicate = duplicate_count > 0
            else:
                record.is_duplicate = False

    @api.depends('ai_score_id.has_red_flags')
    def _compute_red_flags(self):
        """Check if AI detected any red flags"""
        for record in self:
            record.has_red_flags = record.ai_score_id.has_red_flags if record.ai_score_id else False

    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(_('Invalid email format: %s') % record.email)
    
    @api.constrains('full_name')
    def _check_full_name(self):
        """Validate full name is not empty"""
        for record in self:
            if record.full_name and len(record.full_name.strip()) < 2:
                raise ValidationError(_('Full name must be at least 2 characters long.'))

    @api.model
    def _generate_access_token(self):
        """Generate unique access token for portal access"""
        import secrets
        return secrets.token_urlsafe(32)

    def _log_audit(self, record, action, description):
        """Create audit log entry"""
        self.env['assessment.audit.log'].sudo().create({
            'candidate_id': record.id,
            'action': action,
            'description': description,
            'user_id': self.env.user.id,
            'ip_address': record.ip_address,
        })

    def action_view_audit_logs(self):
        """Smart button action to view audit logs"""
        return {
            'name': _('Audit Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.audit.log',
            'view_mode': 'tree,form',
            'domain': [('candidate_id', '=', self.id)],
            'context': {'default_candidate_id': self.id}
        }

    def action_start_ai_scoring(self):
        """Trigger AI scoring process"""
        self.ensure_one()
        if not self.response_id:
            raise ValidationError(_('No assessment response found for this candidate.'))
        
        # Call AI scoring engine
        ai_score = self.env['assessment.ai.score'].create_from_response(self.response_id)
        self.write({
            'ai_score_id': ai_score.id,
            'status': 'ai_scored'
        })
        
        # Send notification email
        self.action_send_submission_confirmation()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('AI scoring completed successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_request_human_review(self):
        """Request human review - update status and create activity"""
        self.ensure_one()
        if not self.ai_score_id:
            raise ValidationError(_('Cannot request human review without AI scoring. Please run AI scoring first.'))

        self.status = 'under_review'

        # Log the review request
        self._log_audit(self, 'review_request',
                       f'Human review requested for candidate: {self.full_name}')

        # Create activity for reviewer
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Review Candidate: %s') % self.full_name,
            note=_('Please review and score this candidate.'),
            user_id=self.env.user.id,
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Human review requested. Use "Create Human Review" button to start reviewing.'),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_create_human_review(self):
        """Create and open human review form"""
        self.ensure_one()
        if not self.ai_score_id:
            raise ValidationError(_('Cannot create human review without AI scoring. Please run AI scoring first.'))

        if self.human_review_id:
            # If review already exists, open it
            return {
                'name': _('Human Review'),
                'type': 'ir.actions.act_window',
                'res_model': 'assessment.human.review',
                'res_id': self.human_review_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Create new human review with AI scores as starting point
        human_review = self.env['assessment.human.review'].create({
            'candidate_id': self.id,
            'technical_score': self.ai_score_id.technical_score,
            'sales_score': self.ai_score_id.sales_score,
            'communication_score': self.ai_score_id.communication_score,
            'learning_score': self.ai_score_id.learning_score,
            'cultural_fit_score': self.ai_score_id.cultural_fit_score,
            'recommendation': self.ai_score_id.ai_recommendation or 'interview',
        })

        # Link to candidate
        self.write({
            'human_review_id': human_review.id,
            'status': 'under_review'
        })

        # Open the human review form
        return {
            'name': _('Human Review'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.human.review',
            'res_id': human_review.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_submission_confirmation(self):
        """Send email confirmation to candidate"""
        self.ensure_one()
        template = self.env.ref('scholarix_assessment.mail_template_assessment_confirmation', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_export_to_recruitment(self):
        """Export candidate to HR Recruitment module"""
        self.ensure_one()
        
        # Create applicant
        applicant = self.env['hr.applicant'].create({
            'partner_name': self.full_name,
            'email_from': self.email,
            'partner_phone': self.phone,
            'description': f"""
                Assessment Scores:
                - Overall: {self.overall_score:.1f}/100
                - Technical: {self.technical_score:.1f}/100
                - Sales: {self.sales_score:.1f}/100
                - Communication: {self.communication_score:.1f}/100
                - Learning Agility: {self.learning_score:.1f}/100
                - Cultural Fit: {self.cultural_fit_score:.1f}/100
                
                Rank: #{self.overall_rank} (Top {self.percentile:.1f}%)
            """,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant',
            'res_id': applicant.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_portal_assessment(self):
        """Open portal view of assessment"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f"{base_url}/assessment/view/{self.access_token}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_print_assessment_pdf(self):
        """Print assessment PDF report - safe method without XML ID dependency"""
        self.ensure_one()
        return self.env.ref('scholarix_assessment.action_report_assessment_candidate').report_action(self)

    @api.model
    def get_dashboard_statistics(self):
        """Get statistics for dashboard"""
        total = self.search_count([])
        pending = self.search_count([('status', '=', 'submitted')])
        ai_scored = self.search_count([('status', '=', 'ai_scored')])
        reviewed = self.search_count([('status', 'in', ['reviewed', 'shortlisted'])])
        
        avg_score = self.search([('overall_score', '>', 0)])
        avg = sum(avg_score.mapped('overall_score')) / len(avg_score) if avg_score else 0
        
        return {
            'total_submissions': total,
            'pending_review': pending,
            'ai_scored': ai_scored,
            'reviewed': reviewed,
            'average_score': round(avg, 1),
        }
