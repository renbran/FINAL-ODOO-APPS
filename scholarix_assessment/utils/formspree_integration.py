# -*- coding: utf-8 -*-
"""
Formspree Integration for Assessment System
Sends assessment submissions to Formspree for backup and notification
"""
import requests
import logging
from odoo import _

_logger = logging.getLogger(__name__)


class FormspreeIntegration:
    """Handle Formspree API integration for assessment backups"""
    
    def __init__(self, form_id=None):
        """
        Initialize Formspree integration
        
        Args:
            form_id (str): Your Formspree form ID (e.g., 'xyzabc123')
        """
        self.form_id = form_id or self._get_default_form_id()
        self.endpoint = f"https://formspree.io/f/{self.form_id}"
        self.timeout = 10  # seconds
        
    def _get_default_form_id(self):
        """
        Get default form ID from Odoo system parameters
        Override this or pass form_id during initialization
        """
        # Default placeholder - replace with your Formspree form ID
        # You can set this via Settings > Technical > System Parameters
        # Key: scholarix_assessment.formspree_form_id
        return "YOUR_FORMSPREE_FORM_ID"
    
    def send_assessment_backup(self, candidate, response, ai_score=None):
        """
        Send assessment data to Formspree for backup
        
        Args:
            candidate: assessment.candidate record
            response: assessment.response record
            ai_score: assessment.ai.score record (optional)
            
        Returns:
            dict: Response from Formspree API
        """
        try:
            # Prepare data payload
            payload = self._prepare_payload(candidate, response, ai_score)
            
            # Send to Formspree
            response_data = self._send_to_formspree(payload)
            
            _logger.info(
                "Assessment backup sent to Formspree for candidate: %s (%s)",
                candidate.full_name, candidate.email
            )
            
            return {
                'success': True,
                'message': 'Backup sent successfully',
                'response': response_data
            }
            
        except requests.exceptions.Timeout:
            _logger.warning("Formspree request timeout for candidate: %s", candidate.email)
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'Formspree backup timed out but assessment was saved'
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error("Formspree API error: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send backup but assessment was saved'
            }
            
        except Exception as e:
            _logger.exception("Unexpected error in Formspree integration: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Backup failed but assessment was saved'
            }
    
    def _prepare_payload(self, candidate, response, ai_score=None):
        """
        Prepare data payload for Formspree
        
        Returns:
            dict: Formatted data for Formspree
        """
        # Basic candidate info
        payload = {
            # Candidate Information
            '_subject': f'New Assessment Submission: {candidate.full_name}',
            'candidate_name': candidate.full_name,
            'candidate_email': candidate.email,
            'candidate_phone': candidate.phone or 'N/A',
            'candidate_location': candidate.location or 'N/A',
            'odoo_experience': candidate.odoo_experience or 'N/A',
            'sales_experience': candidate.sales_experience or 'N/A',
            'submission_date': str(candidate.submission_date),
            
            # Assessment Responses
            'question_1': self._format_question_answer(1, response.q1_answer),
            'question_2': self._format_question_answer(2, response.q2_answer),
            'question_3': self._format_question_answer(3, response.q3_answer),
            'question_4': self._format_question_answer(4, response.q4_answer),
            'question_5': self._format_question_answer(5, response.q5_answer),
            'question_6': self._format_question_answer(6, response.q6_answer),
            'question_7': self._format_question_answer(7, response.q7_answer),
            'question_8': self._format_question_answer(8, response.q8_answer),
            'question_9': self._format_question_answer(9, response.q9_answer),
            'question_10': self._format_question_answer(10, response.q10_answer),
        }
        
        # Add AI scores if available
        if ai_score:
            payload.update({
                'ai_overall_score': f"{ai_score.overall_score:.1f}%",
                'ai_technical_score': f"{ai_score.technical_score:.1f}%",
                'ai_sales_score': f"{ai_score.sales_score:.1f}%",
                'ai_communication_score': f"{ai_score.communication_score:.1f}%",
                'ai_learning_score': f"{ai_score.learning_score:.1f}%",
                'ai_cultural_fit_score': f"{ai_score.cultural_fit_score:.1f}%",
                'ai_recommendation': ai_score.ai_recommendation or 'N/A',
                'ai_strengths': ai_score.identified_strengths or 'N/A',
                'ai_skill_gaps': ai_score.skill_gaps or 'N/A',
                'ai_confidence': f"{ai_score.ai_confidence_score:.1f}%",
            })
        
        # Add summary
        payload['submission_summary'] = self._generate_summary(candidate, response, ai_score)
        
        return payload
    
    def _format_question_answer(self, question_num, answer):
        """Format question and answer for readability"""
        questions = {
            1: "Describe a time you automated a repetitive process",
            2: "How have you used AI tools in your work?",
            3: "Client asks for a feature but doesn't understand what they need",
            4: "Client asks 'How long will this project take?'",
            5: "Describe how you'd learn a new technology",
            6: "Client says 'Your price is too high'",
            7: "Tell me about a difficult client situation",
            8: "Explain what Odoo does to someone non-technical",
            9: "Client asks for something out of scope - how to say no?",
            10: "Why do you want this role? Any concerns?"
        }
        
        q_text = questions.get(question_num, f"Question {question_num}")
        answer_text = answer[:500] if answer else "No answer provided"
        
        return f"{q_text}\n\nAnswer: {answer_text}"
    
    def _generate_summary(self, candidate, response, ai_score=None):
        """Generate a summary of the assessment"""
        summary_parts = [
            f"=== ASSESSMENT SUMMARY ===",
            f"Candidate: {candidate.full_name}",
            f"Email: {candidate.email}",
            f"Submitted: {candidate.submission_date}",
            f"Status: {candidate.status}",
            ""
        ]
        
        if ai_score:
            summary_parts.extend([
                f"AI ANALYSIS:",
                f"- Overall Score: {ai_score.overall_score:.1f}%",
                f"- Technical: {ai_score.technical_score:.1f}%",
                f"- Sales: {ai_score.sales_score:.1f}%",
                f"- Communication: {ai_score.communication_score:.1f}%",
                f"- Learning: {ai_score.learning_score:.1f}%",
                f"- Cultural Fit: {ai_score.cultural_fit_score:.1f}%",
                f"- Recommendation: {ai_score.ai_recommendation}",
                f"- Confidence: {ai_score.ai_confidence_score:.1f}%",
                ""
            ])
        
        summary_parts.extend([
            f"Odoo Experience: {candidate.odoo_experience or 'N/A'}",
            f"Sales Experience: {candidate.sales_experience or 'N/A'}",
            f"Location: {candidate.location or 'N/A'}",
            f"",
            f"Total Questions Answered: 10",
            f"",
            f"This is an automated backup from SCHOLARIX Assessment System.",
        ])
        
        return "\n".join(summary_parts)
    
    def _send_to_formspree(self, payload):
        """
        Send POST request to Formspree
        
        Args:
            payload (dict): Data to send
            
        Returns:
            dict: Response from Formspree
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        return response.json()
    
    @staticmethod
    def validate_form_id(form_id):
        """
        Validate Formspree form ID format
        
        Args:
            form_id (str): Form ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not form_id or not isinstance(form_id, str):
            return False
        
        # Basic validation - form IDs are typically 8-10 characters
        if len(form_id) < 6 or len(form_id) > 20:
            return False
        
        # Should contain only alphanumeric characters
        return form_id.replace('_', '').replace('-', '').isalnum()


def send_to_formspree(candidate, response, ai_score=None, form_id=None):
    """
    Convenience function to send assessment to Formspree
    
    Args:
        candidate: assessment.candidate record
        response: assessment.response record
        ai_score: assessment.ai.score record (optional)
        form_id: Formspree form ID (optional, uses default if not provided)
        
    Returns:
        dict: Result of the operation
    """
    integration = FormspreeIntegration(form_id=form_id)
    return integration.send_assessment_backup(candidate, response, ai_score)
