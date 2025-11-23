# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AssessmentHumanReview(models.Model):
    _name = 'assessment.human.review'
    _description = 'Human Review of Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'review_date desc'
    _rec_name = 'candidate_id'

    candidate_id = fields.Many2one(
        'assessment.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer',
        default=lambda self: self.env.user,
        required=True,
        readonly=True
    )
    
    review_date = fields.Datetime(
        string='Review Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Adjusted Scores (0-100) - Optional, can use question-level scores instead
    technical_score = fields.Float(
        string='Technical Score',
        help='Optional: Score by category or use question-level scores'
    )
    sales_score = fields.Float(
        string='Sales Score',
        help='Optional: Score by category or use question-level scores'
    )
    communication_score = fields.Float(
        string='Communication Score',
        help='Optional: Score by category or use question-level scores'
    )
    learning_score = fields.Float(
        string='Learning Agility Score',
        help='Optional: Score by category or use question-level scores'
    )
    cultural_fit_score = fields.Float(
        string='Cultural Fit Score',
        help='Optional: Score by category or use question-level scores'
    )

    # Per-Question Human Scores (0-100)
    q1_human_score = fields.Float(string='Q1 Human Score', help='Human score for Question 1')
    q2_human_score = fields.Float(string='Q2 Human Score', help='Human score for Question 2')
    q3_human_score = fields.Float(string='Q3 Human Score', help='Human score for Question 3')
    q4_human_score = fields.Float(string='Q4 Human Score', help='Human score for Question 4')
    q5_human_score = fields.Float(string='Q5 Human Score', help='Human score for Question 5')
    q6_human_score = fields.Float(string='Q6 Human Score', help='Human score for Question 6')
    q7_human_score = fields.Float(string='Q7 Human Score', help='Human score for Question 7')
    q8_human_score = fields.Float(string='Q8 Human Score', help='Human score for Question 8')
    q9_human_score = fields.Float(string='Q9 Human Score', help='Human score for Question 9')
    q10_human_score = fields.Float(string='Q10 Human Score', help='Human score for Question 10')

    # Per-Question AI vs Human Average (0-100)
    q1_avg_score = fields.Float(string='Q1 Average', compute='_compute_question_averages', store=True)
    q2_avg_score = fields.Float(string='Q2 Average', compute='_compute_question_averages', store=True)
    q3_avg_score = fields.Float(string='Q3 Average', compute='_compute_question_averages', store=True)
    q4_avg_score = fields.Float(string='Q4 Average', compute='_compute_question_averages', store=True)
    q5_avg_score = fields.Float(string='Q5 Average', compute='_compute_question_averages', store=True)
    q6_avg_score = fields.Float(string='Q6 Average', compute='_compute_question_averages', store=True)
    q7_avg_score = fields.Float(string='Q7 Average', compute='_compute_question_averages', store=True)
    q8_avg_score = fields.Float(string='Q8 Average', compute='_compute_question_averages', store=True)
    q9_avg_score = fields.Float(string='Q9 Average', compute='_compute_question_averages', store=True)
    q10_avg_score = fields.Float(string='Q10 Average', compute='_compute_question_averages', store=True)

    # Overall Score
    overall_score = fields.Float(
        string='Overall Score',
        compute='_compute_overall_score',
        store=True,
        required=False
    )
    
    # Review Details
    reviewer_notes = fields.Text(
        string='Reviewer Notes',
        help='General notes about the candidate'
    )
    strengths = fields.Text(
        string='Identified Strengths',
        help='Key strengths observed'
    )
    concerns = fields.Text(
        string='Concerns',
        help='Areas of concern or red flags'
    )
    
    recommendation = fields.Selection([
        ('reject', 'Reject'),
        ('reconsider', 'Reconsider'),
        ('interview', 'Recommend Interview'),
        ('strong_hire', 'Strong Hire'),
    ], string='Recommendation', tracking=True)
    
    # Related fields for question answers (from response)
    q1_answer = fields.Text(string='Q1 Answer', related='candidate_id.response_id.q1_answer', readonly=True)
    q2_answer = fields.Text(string='Q2 Answer', related='candidate_id.response_id.q2_answer', readonly=True)
    q3_answer = fields.Text(string='Q3 Answer', related='candidate_id.response_id.q3_answer', readonly=True)
    q4_answer = fields.Text(string='Q4 Answer', related='candidate_id.response_id.q4_answer', readonly=True)
    q5_answer = fields.Text(string='Q5 Answer', related='candidate_id.response_id.q5_answer', readonly=True)
    q6_answer = fields.Text(string='Q6 Answer', related='candidate_id.response_id.q6_answer', readonly=True)
    q7_answer = fields.Text(string='Q7 Answer', related='candidate_id.response_id.q7_answer', readonly=True)
    q8_answer = fields.Text(string='Q8 Answer', related='candidate_id.response_id.q8_answer', readonly=True)
    q9_answer = fields.Text(string='Q9 Answer', related='candidate_id.response_id.q9_answer', readonly=True)
    q10_answer = fields.Text(string='Q10 Answer', related='candidate_id.response_id.q10_answer', readonly=True)

    # Related fields for AI scores (from response)
    q1_ai_score = fields.Float(string='Q1 AI Score', related='candidate_id.response_id.q1_score', readonly=True)
    q2_ai_score = fields.Float(string='Q2 AI Score', related='candidate_id.response_id.q2_score', readonly=True)
    q3_ai_score = fields.Float(string='Q3 AI Score', related='candidate_id.response_id.q3_score', readonly=True)
    q4_ai_score = fields.Float(string='Q4 AI Score', related='candidate_id.response_id.q4_score', readonly=True)
    q5_ai_score = fields.Float(string='Q5 AI Score', related='candidate_id.response_id.q5_score', readonly=True)
    q6_ai_score = fields.Float(string='Q6 AI Score', related='candidate_id.response_id.q6_score', readonly=True)
    q7_ai_score = fields.Float(string='Q7 AI Score', related='candidate_id.response_id.q7_score', readonly=True)
    q8_ai_score = fields.Float(string='Q8 AI Score', related='candidate_id.response_id.q8_score', readonly=True)
    q9_ai_score = fields.Float(string='Q9 AI Score', related='candidate_id.response_id.q9_score', readonly=True)
    q10_ai_score = fields.Float(string='Q10 AI Score', related='candidate_id.response_id.q10_score', readonly=True)

    # Score Comparison with AI
    ai_score_before = fields.Float(
        string='AI Score',
        related='candidate_id.ai_score_id.overall_score',
        readonly=True
    )
    score_difference = fields.Float(
        string='Score Adjustment',
        compute='_compute_score_difference',
        store=True,
        help='Difference between human and AI score'
    )
    score_change_reason = fields.Text(
        string='Reason for Score Adjustment',
        help='Explain why you adjusted the AI score'
    )
    
    # Interview Scheduling
    interview_scheduled = fields.Boolean(string='Interview Scheduled')
    interview_date = fields.Datetime(string='Interview Date')
    interview_notes = fields.Text(string='Interview Notes')
    
    @api.depends('q1_human_score', 'q2_human_score', 'q3_human_score', 'q4_human_score',
                 'q5_human_score', 'q6_human_score', 'q7_human_score', 'q8_human_score',
                 'q9_human_score', 'q10_human_score', 'candidate_id.response_id')
    def _compute_question_averages(self):
        """Calculate average of AI and Human scores for each question"""
        for record in self:
            if not record.candidate_id or not record.candidate_id.response_id:
                # Set all averages to 0 if no response
                for i in range(1, 11):
                    setattr(record, f'q{i}_avg_score', 0.0)
                continue

            response = record.candidate_id.response_id

            for i in range(1, 11):
                human_score = getattr(record, f'q{i}_human_score', 0)
                ai_score = getattr(response, f'q{i}_score', 0)

                # Calculate average if both scores exist, otherwise use whichever is available
                if human_score > 0 and ai_score > 0:
                    avg = (human_score + ai_score) / 2
                elif human_score > 0:
                    avg = human_score
                elif ai_score > 0:
                    avg = ai_score
                else:
                    avg = 0.0

                setattr(record, f'q{i}_avg_score', round(avg, 2))

    @api.depends('technical_score', 'sales_score', 'communication_score',
                 'learning_score', 'cultural_fit_score', 'q1_avg_score', 'q2_avg_score',
                 'q3_avg_score', 'q4_avg_score', 'q5_avg_score', 'q6_avg_score',
                 'q7_avg_score', 'q8_avg_score', 'q9_avg_score', 'q10_avg_score')
    def _compute_overall_score(self):
        """Calculate weighted overall score - uses category scores or question averages"""
        WEIGHTS = {
            'technical': 0.25,
            'sales': 0.25,
            'communication': 0.20,
            'learning': 0.15,
            'cultural_fit': 0.15,
        }

        for record in self:
            # Check if we have category scores
            has_category_scores = all([
                record.technical_score, record.sales_score, record.communication_score,
                record.learning_score, record.cultural_fit_score
            ])

            if has_category_scores:
                # Use category-based scoring
                record.overall_score = (
                    record.technical_score * WEIGHTS['technical'] +
                    record.sales_score * WEIGHTS['sales'] +
                    record.communication_score * WEIGHTS['communication'] +
                    record.learning_score * WEIGHTS['learning'] +
                    record.cultural_fit_score * WEIGHTS['cultural_fit']
                )
            else:
                # Fallback to question-level average if available
                question_scores = [
                    getattr(record, f'q{i}_avg_score', 0) for i in range(1, 11)
                ]
                if any(question_scores):
                    valid_scores = [s for s in question_scores if s > 0]
                    record.overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
                else:
                    record.overall_score = 0.0
    
    @api.depends('overall_score', 'ai_score_before')
    def _compute_score_difference(self):
        """Calculate difference between human and AI score"""
        for record in self:
            if record.overall_score and record.ai_score_before:
                record.score_difference = record.overall_score - record.ai_score_before
            else:
                record.score_difference = 0.0
    
    @api.constrains('technical_score', 'sales_score', 'communication_score',
                    'learning_score', 'cultural_fit_score')
    def _check_score_range(self):
        """Validate score ranges"""
        for record in self:
            scores = [
                record.technical_score,
                record.sales_score,
                record.communication_score,
                record.learning_score,
                record.cultural_fit_score,
            ]
            for score in scores:
                if not 0 <= score <= 100:
                    raise ValidationError(_('All scores must be between 0 and 100.'))
    
    @api.model
    def create(self, vals):
        """Create review and update candidate status"""
        review = super(AssessmentHumanReview, self).create(vals)
        
        # Update candidate status
        review.candidate_id.write({'status': 'reviewed'})
        
        # Create ranking if recommendation is positive
        if review.recommendation in ['interview', 'strong_hire']:
            self.env['assessment.ranking'].create_or_update_ranking(review.candidate_id)
        
        # Log the review
        self.env['assessment.audit.log'].sudo().create({
            'candidate_id': review.candidate_id.id,
            'action': 'human_review',
            'description': f'Human review completed by {review.reviewer_id.name}',
            'user_id': self.env.user.id,
        })
        
        # Send notification if significant score change
        if abs(review.score_difference) > 10:
            review._send_score_change_notification()
        
        return review
    
    def write(self, vals):
        """Track review updates"""
        result = super(AssessmentHumanReview, self).write(vals)
        
        # Log significant changes
        if 'overall_score' in vals or 'recommendation' in vals:
            for record in self:
                self.env['assessment.audit.log'].sudo().create({
                    'candidate_id': record.candidate_id.id,
                    'action': 'review_updated',
                    'description': f'Review updated by {self.env.user.name}',
                    'user_id': self.env.user.id,
                })
        
        return result
    
    def _send_score_change_notification(self):
        """Send notification when score significantly differs from AI"""
        self.ensure_one()

        # Get the assessment manager group
        manager_group = self.env.ref('scholarix_assessment.group_assessment_manager', raise_if_not_found=False)

        if not manager_group:
            return

        # Get all users in the manager group
        manager_users = manager_group.users

        if not manager_users:
            return

        # Get the email template
        template = self.env.ref('scholarix_assessment.mail_template_score_change_notification', raise_if_not_found=False)

        if not template:
            return

        # Send email to each manager
        for manager in manager_users:
            if manager.email:
                template.with_context(lang=manager.lang).send_mail(
                    self.id,
                    force_send=True,
                    email_values={'email_to': manager.email}
                )
    
    def action_submit_review(self):
        """Submit the review (placeholder for validation logic)"""
        self.ensure_one()
        # Add any validation or workflow logic here if needed
        return True
    
    def action_view_candidate(self):
        """Open the candidate record"""
        self.ensure_one()
        return {
            'name': _('Candidate'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.candidate',
            'res_id': self.candidate_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_schedule_interview(self):
        """Schedule interview for candidate"""
        self.ensure_one()
        
        return {
            'name': _('Schedule Interview'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.human.review',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit'}
        }
    
    def action_shortlist_candidate(self):
        """Shortlist candidate"""
        self.ensure_one()
        self.candidate_id.write({'status': 'shortlisted'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Candidate shortlisted successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }
