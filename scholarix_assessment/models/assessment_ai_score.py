# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class AssessmentAIScore(models.Model):
    _name = 'assessment.ai.score'
    _description = 'AI Assessment Score'
    _order = 'scoring_date desc'
    _rec_name = 'candidate_id'

    candidate_id = fields.Many2one(
        'assessment.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    response_id = fields.Many2one(
        'assessment.response',
        string='Response',
        required=True,
        ondelete='cascade'
    )
    
    scoring_date = fields.Datetime(
        string='Scoring Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Category Scores (0-100)
    technical_score = fields.Float(
        string='Technical Score',
        help='Odoo/ERP knowledge and technical understanding'
    )
    sales_score = fields.Float(
        string='Sales Score',
        help='Sales skills and client management'
    )
    communication_score = fields.Float(
        string='Communication Score',
        help='Clarity, articulation, and client communication'
    )
    learning_score = fields.Float(
        string='Learning Agility Score',
        help='Ability to learn and adapt'
    )
    cultural_fit_score = fields.Float(
        string='Cultural Fit Score',
        help='Alignment with company values and culture'
    )
    
    # Overall Score
    overall_score = fields.Float(
        string='Overall Score',
        compute='_compute_overall_score',
        store=True,
        help='Weighted average of all category scores'
    )
    
    # Detailed Analysis
    identified_strengths = fields.Text(
        string='Identified Strengths',
        help='AI-identified candidate strengths'
    )
    skill_gaps = fields.Text(
        string='Skill Gaps',
        help='Areas needing improvement'
    )
    
    # Per-Question Analysis (JSON)
    question_analysis = fields.Text(
        string='Question-by-Question Analysis',
        help='Detailed JSON analysis of each question'
    )
    
    # AI Metadata
    ai_model_version = fields.Char(
        string='AI Model Version',
        default='GPT-4-Turbo',
        readonly=True
    )
    ai_confidence_score = fields.Float(
        string='AI Confidence',
        help='How confident the AI is about this scoring (0-100)'
    )
    processing_time_ms = fields.Integer(
        string='Processing Time (ms)',
        readonly=True
    )
    
    # Red Flags
    has_red_flags = fields.Boolean(
        string='Has Red Flags',
        compute='_compute_red_flags',
        store=True
    )
    red_flags_detail = fields.Text(
        string='Red Flags Detail',
        help='Specific red flags detected by AI'
    )
    
    # Recommendation
    ai_recommendation = fields.Selection([
        ('reject', 'Reject'),
        ('reconsider', 'Reconsider'),
        ('interview', 'Recommend Interview'),
        ('strong_hire', 'Strong Hire'),
    ], string='AI Recommendation')
    
    # Token Usage (for cost tracking)
    tokens_used = fields.Integer(string='Tokens Used', readonly=True)
    estimated_cost = fields.Float(string='Estimated Cost (USD)', readonly=True)

    @api.depends('technical_score', 'sales_score', 'communication_score', 
                 'learning_score', 'cultural_fit_score')
    def _compute_overall_score(self):
        """Calculate weighted overall score"""
        WEIGHTS = {
            'technical': 0.25,
            'sales': 0.25,
            'communication': 0.20,
            'learning': 0.15,
            'cultural_fit': 0.15,
        }
        
        for record in self:
            if all([record.technical_score, record.sales_score, record.communication_score,
                   record.learning_score, record.cultural_fit_score]):
                record.overall_score = (
                    record.technical_score * WEIGHTS['technical'] +
                    record.sales_score * WEIGHTS['sales'] +
                    record.communication_score * WEIGHTS['communication'] +
                    record.learning_score * WEIGHTS['learning'] +
                    record.cultural_fit_score * WEIGHTS['cultural_fit']
                )
            else:
                record.overall_score = 0.0

    @api.depends('red_flags_detail', 'overall_score')
    def _compute_red_flags(self):
        """Determine if candidate has significant red flags"""
        for record in self:
            record.has_red_flags = bool(record.red_flags_detail) or record.overall_score < 50

    @api.model
    def create_from_response(self, response):
        """Create AI score from assessment response"""
        if not response:
            raise UserError(_('No response provided for AI scoring.'))
        
        # Get candidate
        candidate = response.candidate_id
        
        # Call AI scoring engine
        try:
            scoring_result = self._run_ai_scoring(response)
        except Exception as e:
            _logger.error(f"AI scoring failed for candidate {candidate.full_name}: {str(e)}")
            raise UserError(_('AI scoring failed. Please try again or contact support.'))
        
        # Create AI score record
        ai_score = self.create({
            'candidate_id': candidate.id,
            'response_id': response.id,
            'technical_score': scoring_result['scores']['technical'],
            'sales_score': scoring_result['scores']['sales'],
            'communication_score': scoring_result['scores']['communication'],
            'learning_score': scoring_result['scores']['learning'],
            'cultural_fit_score': scoring_result['scores']['cultural_fit'],
            'identified_strengths': scoring_result['strengths'],
            'skill_gaps': scoring_result['gaps'],
            'question_analysis': json.dumps(scoring_result['question_analysis']),
            'ai_confidence_score': scoring_result['confidence'],
            'ai_recommendation': scoring_result['recommendation'],
            'red_flags_detail': scoring_result.get('red_flags', ''),
            'processing_time_ms': scoring_result['processing_time'],
            'tokens_used': scoring_result.get('tokens_used', 0),
            'estimated_cost': scoring_result.get('cost', 0.0),
        })
        
        # Update response with per-question scores
        if 'question_scores' in scoring_result:
            response.write({
                'q1_score': scoring_result['question_scores'].get('q1', 0),
                'q2_score': scoring_result['question_scores'].get('q2', 0),
                'q3_score': scoring_result['question_scores'].get('q3', 0),
                'q4_score': scoring_result['question_scores'].get('q4', 0),
                'q5_score': scoring_result['question_scores'].get('q5', 0),
                'q6_score': scoring_result['question_scores'].get('q6', 0),
                'q7_score': scoring_result['question_scores'].get('q7', 0),
                'q8_score': scoring_result['question_scores'].get('q8', 0),
                'q9_score': scoring_result['question_scores'].get('q9', 0),
                'q10_score': scoring_result['question_scores'].get('q10', 0),
            })
        
        return ai_score

    def _run_ai_scoring(self, response):
        """
        Run AI scoring engine on assessment response
        Supports OpenAI GPT-4 and Anthropic Claude APIs
        """
        import time
        start_time = time.time()
        
        # Get configuration
        ai_provider = self.env['ir.config_parameter'].sudo().get_param('scholarix_assessment.ai_provider', 'anthropic')
        openai_key = self.env['ir.config_parameter'].sudo().get_param('scholarix_assessment.openai_api_key')
        anthropic_key = self.env['ir.config_parameter'].sudo().get_param('scholarix_assessment.anthropic_api_key')
        use_mock = self.env['ir.config_parameter'].sudo().get_param('scholarix_assessment.use_mock_ai', 'False') == 'True'
        
        # Determine which provider to use
        if use_mock:
            _logger.warning("Using mock AI scoring (mock mode enabled)")
            return self._mock_ai_scoring(response)
        
        if ai_provider == 'anthropic' and anthropic_key:
            return self._run_anthropic_scoring(response, anthropic_key, start_time)
        elif ai_provider == 'openai' and openai_key:
            return self._run_openai_scoring(response, openai_key, start_time)
        elif anthropic_key:  # Fallback to Anthropic if available
            _logger.info("No provider specified, using Anthropic API")
            return self._run_anthropic_scoring(response, anthropic_key, start_time)
        elif openai_key:  # Fallback to OpenAI if available
            _logger.info("No provider specified, using OpenAI API")
            return self._run_openai_scoring(response, openai_key, start_time)
        else:
            _logger.warning("No AI API key configured, using mock scoring")
            return self._mock_ai_scoring(response)

    def _run_anthropic_scoring(self, response, api_key, start_time):
        """Run AI scoring using Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Prepare prompt for AI
            system_prompt = self._get_system_prompt()
            user_prompt = self._build_ai_prompt(response)
            
            # Call Anthropic API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse response
            ai_response = message.content[0].text
            result = json.loads(ai_response)
            
            # Add metadata
            processing_time = int((time.time() - start_time) * 1000)
            result['processing_time'] = processing_time
            result['tokens_used'] = message.usage.input_tokens + message.usage.output_tokens
            result['cost'] = (message.usage.input_tokens / 1000000 * 3) + (message.usage.output_tokens / 1000000 * 15)  # Claude pricing
            result['ai_model_used'] = 'claude-3-5-sonnet-20241022'
            
            _logger.info("AI scoring completed using Anthropic Claude (tokens: %d, time: %dms)", 
                        result['tokens_used'], processing_time)
            
            return result
            
        except Exception as e:
            _logger.error("Anthropic API error: %s", str(e))
            # Fallback to mock scoring
            return self._mock_ai_scoring(response)

    def _run_openai_scoring(self, response, api_key, start_time):
        """Run AI scoring using OpenAI GPT-4 API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Prepare prompt for AI
            prompt = self._build_ai_prompt(response)
            
            # Call OpenAI API (modern syntax for openai>=1.0.0)
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            # Parse response
            ai_response = completion.choices[0].message.content
            result = json.loads(ai_response)
            
            # Add metadata
            processing_time = int((time.time() - start_time) * 1000)
            result['processing_time'] = processing_time
            result['tokens_used'] = completion.usage.total_tokens
            result['cost'] = (completion.usage.total_tokens / 1000) * 0.01  # Rough estimate
            result['ai_model_used'] = 'gpt-4-turbo-preview'
            
            _logger.info("AI scoring completed using OpenAI GPT-4 (tokens: %d, time: %dms)", 
                        result['tokens_used'], processing_time)
            
            return result
            
        except Exception as e:
            _logger.error("OpenAI API error: %s", str(e))
            # Fallback to mock scoring
            return self._mock_ai_scoring(response)

    def _mock_ai_scoring(self, response):
        """Mock AI scoring for testing/demo purposes"""
        import random
        import time
        
        # Simulate processing time
        time.sleep(1)
        
        answers = response.get_all_answers()
        metadata = response.get_answer_metadata()
        
        # Simple heuristic scoring based on answer length and quality
        def score_answer(answer, char_count):
            base_score = min(char_count / 2, 80)  # Max 80 for length
            
            # Add points for specifics
            if any(word in answer.lower() for word in ['automated', 'implemented', 'reduced', 'increased']):
                base_score += 10
            if any(char.isdigit() for char in answer):  # Has numbers
                base_score += 5
            
            return min(base_score + random.uniform(-5, 5), 100)
        
        # Score each category
        technical = (score_answer(answers['q1'], metadata['char_counts']['q1']) + 
                    score_answer(answers['q2'], metadata['char_counts']['q2']) +
                    score_answer(answers['q4'], metadata['char_counts']['q4'])) / 3
        
        sales = (score_answer(answers['q6'], metadata['char_counts']['q6']) + 
                score_answer(answers['q7'], metadata['char_counts']['q7'])) / 2
        
        communication = (score_answer(answers['q3'], metadata['char_counts']['q3']) + 
                        score_answer(answers['q8'], metadata['char_counts']['q8'])) / 2
        
        learning = score_answer(answers['q5'], metadata['char_counts']['q5'])
        
        cultural_fit = (score_answer(answers['q9'], metadata['char_counts']['q9']) + 
                       score_answer(answers['q10'], metadata['char_counts']['q10'])) / 2
        
        overall = (technical * 0.25 + sales * 0.25 + communication * 0.20 + 
                  learning * 0.15 + cultural_fit * 0.15)
        
        # Generate recommendation
        if overall >= 85:
            recommendation = 'strong_hire'
        elif overall >= 70:
            recommendation = 'interview'
        elif overall >= 50:
            recommendation = 'reconsider'
        else:
            recommendation = 'reject'
        
        # Identify strengths and gaps
        strengths = []
        gaps = []
        
        if technical >= 75:
            strengths.append("Strong technical understanding")
        else:
            gaps.append("Technical skills need development")
        
        if sales >= 75:
            strengths.append("Excellent sales and client management skills")
        else:
            gaps.append("Sales experience could be stronger")
        
        if communication >= 75:
            strengths.append("Clear and effective communicator")
        else:
            gaps.append("Communication skills need improvement")
        
        return {
            'scores': {
                'technical': round(technical, 1),
                'sales': round(sales, 1),
                'communication': round(communication, 1),
                'learning': round(learning, 1),
                'cultural_fit': round(cultural_fit, 1),
            },
            'overall': round(overall, 1),
            'confidence': random.uniform(75, 95),
            'strengths': '\n'.join(f"• {s}" for s in strengths),
            'gaps': '\n'.join(f"• {g}" for g in gaps),
            'recommendation': recommendation,
            'red_flags': '\n'.join([
                "• Short answer length" if metadata['flags']['has_short_answers'] else "",
                "• Possible copy-paste detected" if metadata['flags']['has_copy_paste_patterns'] else "",
            ]).strip(),
            'question_analysis': {f'q{i}': {'score': random.uniform(60, 90)} for i in range(1, 11)},
            'question_scores': {f'q{i}': random.uniform(60, 90) for i in range(1, 11)},
            'processing_time': random.randint(500, 2000),
            'tokens_used': random.randint(1000, 3000),
            'cost': random.uniform(0.02, 0.06),
        }

    def _get_system_prompt(self):
        """System prompt for AI scoring"""
        return """You are an expert HR assessment evaluator for SCHOLARIX, specializing in evaluating 
candidates for Odoo ERP Sales Consultant roles. Your task is to analyze candidate responses and provide 
detailed scoring across 5 categories:

1. Technical Score (0-100): Odoo/ERP knowledge, automation skills, technical understanding
2. Sales Score (0-100): Client management, objection handling, relationship building
3. Communication Score (0-100): Clarity, articulation, simplification ability
4. Learning Agility (0-100): Adaptability, growth mindset, self-awareness
5. Cultural Fit (0-100): Values alignment, professionalism, honesty

For each assessment, provide:
- Category scores with justification
- Overall recommendation (reject/reconsider/interview/strong_hire)
- Identified strengths (3-5 bullet points)
- Skill gaps (3-5 bullet points)
- Red flags (if any)
- Per-question analysis

Be fair, thorough, and focus on concrete evidence from answers. Look for specifics, examples, 
quantifiable results, and authentic responses. Flag generic, evasive, or inconsistent answers.

Return response as valid JSON."""

    def _build_ai_prompt(self, response):
        """Build prompt for AI from response"""
        candidate = response.candidate_id
        answers = response.get_all_answers()
        
        questions = {
            'q1': 'Describe a time you automated a repetitive process. What tools did you use, and what was the result?',
            'q2': 'How have you used AI tools (like ChatGPT, Copilot, etc.) in your work? Give a specific example.',
            'q3': 'A client asks for a feature but doesn\'t fully understand what they need. How do you handle this conversation?',
            'q4': 'A client asks, "How long will this project take?" How do you respond?',
            'q5': 'Describe how you\'d learn a new technology you\'ve never used before. What\'s your process?',
            'q6': 'A potential client says, "Your price is too high." How do you respond?',
            'q7': 'Tell me about a time you worked with a difficult client. What was the situation and how did you handle it?',
            'q8': 'Explain what Odoo does to someone who has never heard of ERP systems.',
            'q9': 'A client asks for something that\'s clearly out of scope. How do you say no professionally?',
            'q10': 'Why do you want this role? What concerns do you have about this position?'
        }
        
        prompt = f"""
CANDIDATE PROFILE:
- Name: {candidate.full_name}
- Odoo Experience: {candidate.odoo_experience}
- Sales Experience: {candidate.sales_experience}
- Location: {candidate.location}

ASSESSMENT RESPONSES:
"""
        for q_num, question in questions.items():
            prompt += f"\nQ{q_num[-1]}: {question}\n"
            prompt += f"Answer: {answers[q_num]}\n"
            prompt += "-" * 80 + "\n"
        
        prompt += """
Please analyze these responses and provide a JSON response with the following structure:
{
    "scores": {
        "technical": <0-100>,
        "sales": <0-100>,
        "communication": <0-100>,
        "learning": <0-100>,
        "cultural_fit": <0-100>
    },
    "confidence": <0-100>,
    "recommendation": "<reject|reconsider|interview|strong_hire>",
    "strengths": "<bullet point list>",
    "gaps": "<bullet point list>",
    "red_flags": "<any concerns or empty>",
    "question_analysis": {
        "q1": {"score": <0-100>, "notes": "<brief analysis>"},
        ...
    }
}
"""
        return prompt

    def action_regenerate_score(self):
        """Regenerate AI score - keeps historical record"""
        self.ensure_one()

        # Create new score
        new_score = self.create_from_response(self.response_id)

        # Update candidate to point to new score
        # Keep old score for historical purposes
        if self.candidate_id:
            self.candidate_id.write({
                'ai_score_id': new_score.id,
            })

        # Open the new score
        return {
            'name': _('AI Score'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.ai.score',
            'res_id': new_score.id,
            'view_mode': 'form',
            'target': 'current',
        }
