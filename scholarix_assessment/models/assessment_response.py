# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AssessmentResponse(models.Model):
    _name = 'assessment.response'
    _description = 'Assessment Response'
    _order = 'submission_date desc'
    _rec_name = 'candidate_id'

    candidate_id = fields.Many2one(
        'assessment.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    submission_date = fields.Datetime(
        string='Submission Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Question 1: Automation Experience
    q1_answer = fields.Text(
        string='Q1: Automation Experience',
        help='Describe a time you automated a process'
    )
    q1_char_count = fields.Integer(
        string='Q1 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q1_time_spent = fields.Integer(string='Q1 Time Spent (seconds)')
    q1_score = fields.Float(string='Q1 Score', readonly=True)
    
    # Question 2: AI Tools Experience
    q2_answer = fields.Text(
        string='Q2: AI Tools Experience',
        help='How have you used AI tools in your work?'
    )
    q2_char_count = fields.Integer(
        string='Q2 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q2_time_spent = fields.Integer(string='Q2 Time Spent (seconds)')
    q2_score = fields.Float(string='Q2 Score', readonly=True)
    
    # Question 3: Client Communication
    q3_answer = fields.Text(
        string='Q3: Client Communication',
        help='How do you handle client communication about requirements?'
    )
    q3_char_count = fields.Integer(
        string='Q3 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q3_time_spent = fields.Integer(string='Q3 Time Spent (seconds)')
    q3_score = fields.Float(string='Q3 Score', readonly=True)
    
    # Question 4: Project Estimation
    q4_answer = fields.Text(
        string='Q4: Project Estimation',
        help='How do you estimate project timelines?'
    )
    q4_char_count = fields.Integer(
        string='Q4 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q4_time_spent = fields.Integer(string='Q4 Time Spent (seconds)')
    q4_score = fields.Float(string='Q4 Score', readonly=True)
    
    # Question 5: Learning New Technologies
    q5_answer = fields.Text(
        string='Q5: Learning New Technologies',
        help='Describe your approach to learning new technologies'
    )
    q5_char_count = fields.Integer(
        string='Q5 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q5_time_spent = fields.Integer(string='Q5 Time Spent (seconds)')
    q5_score = fields.Float(string='Q5 Score', readonly=True)
    
    # Question 6: Objection Handling
    q6_answer = fields.Text(
        string='Q6: Objection Handling',
        help='How do you handle client objections?'
    )
    q6_char_count = fields.Integer(
        string='Q6 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q6_time_spent = fields.Integer(string='Q6 Time Spent (seconds)')
    q6_score = fields.Float(string='Q6 Score', readonly=True)
    
    # Question 7: Difficult Client
    q7_answer = fields.Text(
        string='Q7: Difficult Client Management',
        help='Describe a challenging client situation'
    )
    q7_char_count = fields.Integer(
        string='Q7 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q7_time_spent = fields.Integer(string='Q7 Time Spent (seconds)')
    q7_score = fields.Float(string='Q7 Score', readonly=True)
    
    # Question 8: Simplification
    q8_answer = fields.Text(
        string='Q8: Technical Simplification',
        help='Explain Odoo to a non-technical person'
    )
    q8_char_count = fields.Integer(
        string='Q8 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q8_time_spent = fields.Integer(string='Q8 Time Spent (seconds)')
    q8_score = fields.Float(string='Q8 Score', readonly=True)
    
    # Question 9: Setting Boundaries
    q9_answer = fields.Text(
        string='Q9: Setting Client Boundaries',
        help='How do you say no professionally?'
    )
    q9_char_count = fields.Integer(
        string='Q9 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q9_time_spent = fields.Integer(string='Q9 Time Spent (seconds)')
    q9_score = fields.Float(string='Q9 Score', readonly=True)
    
    # Question 10: Motivation and Concerns
    q10_answer = fields.Text(
        string='Q10: Motivation and Concerns',
        help='Why do you want this role? Any concerns?'
    )
    q10_char_count = fields.Integer(
        string='Q10 Character Count',
        compute='_compute_char_counts',
        store=True
    )
    q10_time_spent = fields.Integer(string='Q10 Time Spent (seconds)')
    q10_score = fields.Float(string='Q10 Score', readonly=True)
    
    # Overall Metadata
    total_time_spent = fields.Integer(
        string='Total Time Spent (seconds)',
        compute='_compute_total_time',
        store=True
    )
    total_characters = fields.Integer(
        string='Total Characters',
        compute='_compute_total_characters',
        store=True
    )
    average_answer_length = fields.Integer(
        string='Average Answer Length',
        compute='_compute_average_length',
        store=True
    )
    
    # Analysis Flags
    has_short_answers = fields.Boolean(
        string='Has Short Answers',
        compute='_compute_quality_flags',
        store=True,
        help='One or more answers are suspiciously short'
    )
    has_copy_paste_patterns = fields.Boolean(
        string='Possible Copy-Paste',
        compute='_compute_quality_flags',
        store=True,
        help='Detected patterns suggesting copy-paste'
    )
    
    @api.depends('q1_answer', 'q2_answer', 'q3_answer', 'q4_answer', 'q5_answer',
                 'q6_answer', 'q7_answer', 'q8_answer', 'q9_answer', 'q10_answer')
    def _compute_char_counts(self):
        """Calculate character count for each answer"""
        for record in self:
            record.q1_char_count = len(record.q1_answer or '')
            record.q2_char_count = len(record.q2_answer or '')
            record.q3_char_count = len(record.q3_answer or '')
            record.q4_char_count = len(record.q4_answer or '')
            record.q5_char_count = len(record.q5_answer or '')
            record.q6_char_count = len(record.q6_answer or '')
            record.q7_char_count = len(record.q7_answer or '')
            record.q8_char_count = len(record.q8_answer or '')
            record.q9_char_count = len(record.q9_answer or '')
            record.q10_char_count = len(record.q10_answer or '')
    
    @api.depends('q1_time_spent', 'q2_time_spent', 'q3_time_spent', 'q4_time_spent',
                 'q5_time_spent', 'q6_time_spent', 'q7_time_spent', 'q8_time_spent',
                 'q9_time_spent', 'q10_time_spent')
    def _compute_total_time(self):
        """Calculate total time spent"""
        for record in self:
            record.total_time_spent = sum([
                record.q1_time_spent or 0,
                record.q2_time_spent or 0,
                record.q3_time_spent or 0,
                record.q4_time_spent or 0,
                record.q5_time_spent or 0,
                record.q6_time_spent or 0,
                record.q7_time_spent or 0,
                record.q8_time_spent or 0,
                record.q9_time_spent or 0,
                record.q10_time_spent or 0,
            ])
    
    @api.depends('q1_char_count', 'q2_char_count', 'q3_char_count', 'q4_char_count',
                 'q5_char_count', 'q6_char_count', 'q7_char_count', 'q8_char_count',
                 'q9_char_count', 'q10_char_count')
    def _compute_total_characters(self):
        """Calculate total characters"""
        for record in self:
            record.total_characters = sum([
                record.q1_char_count,
                record.q2_char_count,
                record.q3_char_count,
                record.q4_char_count,
                record.q5_char_count,
                record.q6_char_count,
                record.q7_char_count,
                record.q8_char_count,
                record.q9_char_count,
                record.q10_char_count,
            ])
    
    @api.depends('total_characters')
    def _compute_average_length(self):
        """Calculate average answer length"""
        for record in self:
            record.average_answer_length = record.total_characters // 10 if record.total_characters else 0
    
    @api.depends('q1_char_count', 'q2_char_count', 'q3_char_count', 'q4_char_count',
                 'q5_char_count', 'q6_char_count', 'q7_char_count', 'q8_char_count',
                 'q9_char_count', 'q10_char_count', 'q1_time_spent', 'q2_time_spent')
    def _compute_quality_flags(self):
        """Detect quality issues in responses"""
        MIN_CHARS = 50  # Minimum expected length
        MAX_SPEED = 10  # Max characters per second (copy-paste indicator)
        
        for record in self:
            # Check for short answers
            char_counts = [
                record.q1_char_count, record.q2_char_count, record.q3_char_count,
                record.q4_char_count, record.q5_char_count, record.q6_char_count,
                record.q7_char_count, record.q8_char_count, record.q9_char_count,
                record.q10_char_count
            ]
            record.has_short_answers = any(count < MIN_CHARS for count in char_counts)
            
            # Check for copy-paste patterns (very fast typing)
            if record.q1_time_spent and record.q1_char_count:
                speed = record.q1_char_count / max(record.q1_time_spent, 1)
                record.has_copy_paste_patterns = speed > MAX_SPEED
            else:
                record.has_copy_paste_patterns = False
    
    def get_all_answers(self):
        """Return dictionary of all answers for AI processing"""
        self.ensure_one()
        return {
            'q1': self.q1_answer,
            'q2': self.q2_answer,
            'q3': self.q3_answer,
            'q4': self.q4_answer,
            'q5': self.q5_answer,
            'q6': self.q6_answer,
            'q7': self.q7_answer,
            'q8': self.q8_answer,
            'q9': self.q9_answer,
            'q10': self.q10_answer,
        }
    
    def get_answer_metadata(self):
        """Return metadata about answers"""
        self.ensure_one()
        return {
            'char_counts': {
                'q1': self.q1_char_count,
                'q2': self.q2_char_count,
                'q3': self.q3_char_count,
                'q4': self.q4_char_count,
                'q5': self.q5_char_count,
                'q6': self.q6_char_count,
                'q7': self.q7_char_count,
                'q8': self.q8_char_count,
                'q9': self.q9_char_count,
                'q10': self.q10_char_count,
            },
            'time_spent': {
                'q1': self.q1_time_spent,
                'q2': self.q2_time_spent,
                'q3': self.q3_time_spent,
                'q4': self.q4_time_spent,
                'q5': self.q5_time_spent,
                'q6': self.q6_time_spent,
                'q7': self.q7_time_spent,
                'q8': self.q8_time_spent,
                'q9': self.q9_time_spent,
                'q10': self.q10_time_spent,
            },
            'flags': {
                'has_short_answers': self.has_short_answers,
                'has_copy_paste_patterns': self.has_copy_paste_patterns,
            }
        }
