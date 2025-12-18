# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
import json
import logging
from ..utils.formspree_integration import send_to_formspree

_logger = logging.getLogger(__name__)


class AssessmentController(http.Controller):

    @http.route('/assessment/submit', type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def submit_assessment_form(self, **kw):
        """Handle form submission from portal"""
        try:
            # Ensure clean transaction
            request.env.cr.commit()
            
            # Validate required fields
            if not kw.get('candidateName') or not kw.get('candidateEmail'):
                return request.render('scholarix_assessment.portal_assessment_error', {
                    'error_message': _('Please provide your name and email.')
                })

            # Duplicate email check removed - users can now submit multiple assessments
            email = kw.get('candidateEmail', '').strip().lower()

            # Create candidate
            candidate = request.env['assessment.candidate'].sudo().create({
                'full_name': kw.get('candidateName'),
                'email': email,
                'phone': kw.get('candidatePhone'),
                'location': kw.get('candidateLocation'),
                'odoo_experience': kw.get('odooExperience'),
                'sales_experience': kw.get('salesExperience'),
                'status': 'submitted',
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT'),
            })

            # Create response with all answers
            response = request.env['assessment.response'].sudo().create({
                'candidate_id': candidate.id,
                'q1_answer': kw.get('q10_answer', ''),
                'q2_answer': kw.get('q20_answer', ''),
                'q3_answer': kw.get('q30_answer', ''),
                'q4_answer': kw.get('q40_answer', ''),
                'q5_answer': kw.get('q50_answer', ''),
                'q6_answer': kw.get('q60_answer', ''),
                'q7_answer': kw.get('q70_answer', ''),
                'q8_answer': kw.get('q80_answer', ''),
                'q9_answer': kw.get('q90_answer', ''),
                'q10_answer': kw.get('q100_answer', ''),
            })

            # Link response to candidate
            candidate.write({'response_id': response.id})

            # Trigger AI scoring
            ai_score = None
            try:
                ai_score = request.env['assessment.ai.score'].sudo().create_from_response(response)
                candidate.write({'ai_score_id': ai_score.id, 'status': 'ai_scored'})
            except (ValueError, KeyError, AttributeError) as e:
                _logger.warning("AI scoring failed: %s", str(e))
                # Continue even if AI scoring fails

            # Commit the transaction before sending email
            request.env.cr.commit()
            
            # Send to Formspree for backup (non-blocking)
            try:
                # Check if Formspree is enabled
                formspree_enabled = request.env['ir.config_parameter'].sudo().get_param(
                    'scholarix_assessment.formspree_enabled', 'False'
                )
                if formspree_enabled.lower() == 'true':
                    form_id = request.env['ir.config_parameter'].sudo().get_param(
                        'scholarix_assessment.formspree_form_id'
                    )
                    if form_id and form_id != 'YOUR_FORMSPREE_FORM_ID':
                        formspree_result = send_to_formspree(candidate, response, ai_score, form_id)
                        if formspree_result.get('success'):
                            _logger.info("Assessment backed up to Formspree for %s", candidate.email)
                        else:
                            _logger.warning("Formspree backup failed: %s", formspree_result.get('message'))
                    else:
                        _logger.debug("Formspree form ID not configured, skipping backup")
                else:
                    _logger.debug("Formspree integration disabled")
            except Exception as e:  # pylint: disable=broad-except
                _logger.warning("Formspree integration error: %s", str(e))
                # Don't fail the submission if Formspree fails
            
            # Send confirmation email
            try:
                candidate.action_send_submission_confirmation()
                _logger.info("Confirmation email sent to %s", candidate.email)
            except (ValueError, KeyError, AttributeError) as e:
                _logger.warning("Email sending failed: %s", str(e))
                # Don't fail the submission if email fails

            # Log successful submission
            _logger.info("Assessment submitted successfully for %s (%s)", candidate.full_name, candidate.email)
            
            # Redirect to thank you page
            return request.redirect('/assessment/thank-you')

        except ValidationError as e:
            _logger.error("Validation error in assessment submission: %s", str(e))
            request.env.cr.rollback()
            return request.render('scholarix_assessment.portal_assessment_error', {
                'error_message': str(e)
            })
        except IntegrityError as e:
            _logger.error("Database integrity error in assessment submission: %s", str(e))
            request.env.cr.rollback()
            # Duplicate email check removed - generic error message
            return request.render('scholarix_assessment.portal_assessment_error', {
                'error_message': _('A database error occurred. Please try again or contact support.')
            })
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            _logger.exception("Error in assessment submission: %s", str(e))
            request.env.cr.rollback()
            return request.render('scholarix_assessment.portal_assessment_error', {
                'error_message': _('An error occurred. Please try again or contact support.')
            })

    @http.route('/assessment/submit/api', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def submit_assessment_api(self):  # pylint: disable=unused-argument
        """
        API endpoint to submit candidate assessment
        Expected JSON payload:
        {
            "candidate": {...},
            "responses": {...},
            "metadata": {...}
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            
            # Validate required fields
            if not all(key in data for key in ['candidate', 'responses']):
                return {'success': False, 'error': 'Missing required fields'}
            
            candidate_data = data['candidate']
            responses_data = data['responses']
            metadata = data.get('metadata', {})
            
            # Create candidate
            candidate = request.env['assessment.candidate'].sudo().create({
                'full_name': candidate_data.get('candidateName'),
                'email': candidate_data.get('candidateEmail'),
                'phone': candidate_data.get('candidatePhone'),
                'location': candidate_data.get('candidateLocation'),
                'odoo_experience': candidate_data.get('odooExperience'),
                'sales_experience': candidate_data.get('salesExperience'),
                'status': 'submitted',
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT'),
            })
            
            # Create response
            response = request.env['assessment.response'].sudo().create({
                'candidate_id': candidate.id,
                'q1_answer': responses_data.get('q1_answer', ''),
                'q2_answer': responses_data.get('q2_answer', ''),
                'q3_answer': responses_data.get('q3_answer', ''),
                'q4_answer': responses_data.get('q4_answer', ''),
                'q5_answer': responses_data.get('q5_answer', ''),
                'q6_answer': responses_data.get('q6_answer', ''),
                'q7_answer': responses_data.get('q7_answer', ''),
                'q8_answer': responses_data.get('q8_answer', ''),
                'q9_answer': responses_data.get('q9_answer', ''),
                'q10_answer': responses_data.get('q10_answer', ''),
                'q1_time_spent': metadata.get('timeSpent', {}).get('q1', 0),
                'q2_time_spent': metadata.get('timeSpent', {}).get('q2', 0),
                'q3_time_spent': metadata.get('timeSpent', {}).get('q3', 0),
                'q4_time_spent': metadata.get('timeSpent', {}).get('q4', 0),
                'q5_time_spent': metadata.get('timeSpent', {}).get('q5', 0),
                'q6_time_spent': metadata.get('timeSpent', {}).get('q6', 0),
                'q7_time_spent': metadata.get('timeSpent', {}).get('q7', 0),
                'q8_time_spent': metadata.get('timeSpent', {}).get('q8', 0),
                'q9_time_spent': metadata.get('timeSpent', {}).get('q9', 0),
                'q10_time_spent': metadata.get('timeSpent', {}).get('q10', 0),
            })
            
            # Link response to candidate
            candidate.write({'response_id': response.id})
            
            # Trigger AI scoring
            ai_score = request.env['assessment.ai.score'].sudo().create_from_response(response)
            candidate.write({'ai_score_id': ai_score.id, 'status': 'ai_scored'})
            
            # Send to Formspree for backup (non-blocking)
            try:
                formspree_enabled = request.env['ir.config_parameter'].sudo().get_param(
                    'scholarix_assessment.formspree_enabled', 'False'
                )
                if formspree_enabled.lower() == 'true':
                    form_id = request.env['ir.config_parameter'].sudo().get_param(
                        'scholarix_assessment.formspree_form_id'
                    )
                    if form_id and form_id != 'YOUR_FORMSPREE_FORM_ID':
                        formspree_result = send_to_formspree(candidate, response, ai_score, form_id)
                        if formspree_result.get('success'):
                            _logger.info("Assessment backed up to Formspree for %s", candidate.email)
            except Exception as formspree_error:  # pylint: disable=broad-except
                _logger.warning("Formspree integration error: %s", str(formspree_error))
            
            # Send confirmation email
            candidate.action_send_submission_confirmation()
            
            # Prepare response
            return {
                'success': True,
                'candidateId': candidate.id,
                'accessToken': candidate.access_token,
                'aiAnalysis': {
                    'overallScore': ai_score.overall_score,
                    'scores': {
                        'technical': ai_score.technical_score,
                        'sales': ai_score.sales_score,
                        'communication': ai_score.communication_score,
                        'learning': ai_score.learning_score,
                        'fit': ai_score.cultural_fit_score,
                    },
                    'strengths': ai_score.identified_strengths,
                    'skillGaps': ai_score.skill_gaps,
                    'recommendation': ai_score.ai_recommendation,
                    'confidence': ai_score.ai_confidence_score,
                },
                'message': 'Assessment submitted successfully. Check your email for confirmation.'
            }
            
        except ValidationError as e:
            _logger.error("Validation error in assessment submission: %s", str(e))
            return {'success': False, 'error': str(e)}
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            _logger.exception(f"Error in assessment submission: {str(e)}")
            return {'success': False, 'error': 'An error occurred. Please try again.'}
    
    @http.route('/assessment/questions', type='json', auth='public', methods=['GET'])
    def get_questions(self):
        """Get all active assessment questions"""
        try:
            questions = request.env['assessment.question'].sudo().get_active_questions()
            
            return {
                'success': True,
                'questions': [{
                    'id': q.id,
                    'sequence': q.sequence,
                    'name': q.name,
                    'question_text': q.question_text,
                    'help_text': q.help_text,
                    'question_type': q.question_type,
                    'category': q.category,
                    'min_char_count': q.min_char_count,
                    'max_char_count': q.max_char_count,
                    'is_required': q.is_required,
                } for q in questions]
            }
        except (ValueError, KeyError, AttributeError) as e:
            _logger.exception("Error fetching questions: %s", str(e))
            return {'success': False, 'error': 'Failed to fetch questions'}
    
    @http.route('/assessment/check-email', type='json', auth='public', methods=['POST'])
    def check_email(self, email):
        """Check if email already has a submission"""
        try:
            existing = request.env['assessment.candidate'].sudo().search_count([
                ('email', '=', email)
            ])
            
            return {
                'success': True,
                'exists': existing > 0,
                'count': existing
            }
        except (ValueError, TypeError) as e:
            _logger.exception("Error checking email: %s", str(e))
            return {'success': False, 'error': 'Failed to check email'}
    
    @http.route('/api/v1/dashboard/candidates', type='json', auth='user', methods=['GET'])
    def get_candidates(self, page=1, limit=20, status=None, sortBy='submission_date', 
                      sortOrder='desc', search=None, **filters):
        """Get candidates list for dashboard"""
        try:
            # Build domain
            domain = []
            if status:
                domain.append(('status', '=', status))
            if search:
                domain.append('|', '|', 
                            ('full_name', 'ilike', search),
                            ('email', 'ilike', search),
                            ('phone', 'ilike', search))
            
            if filters.get('minScore'):
                domain.append(('overall_score', '>=', float(filters['minScore'])))
            if filters.get('maxScore'):
                domain.append(('overall_score', '<=', float(filters['maxScore'])))
            
            # Get total count
            total = request.env['assessment.candidate'].search_count(domain)
            
            # Get paginated results
            offset = (int(page) - 1) * int(limit)
            order = f"{sortBy} {sortOrder}"
            
            candidates = request.env['assessment.candidate'].search(
                domain, limit=int(limit), offset=offset, order=order
            )
            
            # Prepare response
            return {
                'success': True,
                'data': {
                    'candidates': [{
                        'id': c.id,
                        'full_name': c.full_name,
                        'email': c.email,
                        'phone': c.phone,
                        'location': c.location,
                        'odoo_experience': c.odoo_experience,
                        'sales_experience': c.sales_experience,
                        'submission_date': c.submission_date.isoformat() if c.submission_date else None,
                        'status': c.status,
                        'overall_score': c.overall_score,
                        'overall_rank': c.overall_rank,
                        'percentile': c.percentile,
                        'has_red_flags': c.has_red_flags,
                        'is_duplicate': c.is_duplicate,
                    } for c in candidates],
                    'pagination': {
                        'currentPage': int(page),
                        'totalPages': (total + int(limit) - 1) // int(limit),
                        'totalResults': total,
                        'pageSize': int(limit),
                        'hasNext': offset + int(limit) < total,
                        'hasPrev': int(page) > 1,
                    },
                    'statistics': request.env['assessment.candidate'].get_dashboard_statistics(),
                }
            }
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            _logger.exception("Error fetching candidates: %s", str(e))
            return {'success': False, 'error': str(e)}
    
    @http.route('/api/v1/dashboard/candidate/<int:candidate_id>', type='json', auth='user')
    def get_candidate_detail(self, candidate_id):
        """Get detailed candidate information"""
        try:
            candidate = request.env['assessment.candidate'].browse(candidate_id)
            if not candidate.exists():
                return {'success': False, 'error': 'Candidate not found'}
            
            return {
                'success': True,
                'data': {
                    'candidate': {
                        'id': candidate.id,
                        'full_name': candidate.full_name,
                        'email': candidate.email,
                        'phone': candidate.phone,
                        'location': candidate.location,
                        'odoo_experience': candidate.odoo_experience,
                        'sales_experience': candidate.sales_experience,
                        'submission_date': candidate.submission_date.isoformat() if candidate.submission_date else None,
                        'status': candidate.status,
                        'overall_score': candidate.overall_score,
                        'technical_score': candidate.technical_score,
                        'sales_score': candidate.sales_score,
                        'communication_score': candidate.communication_score,
                        'learning_score': candidate.learning_score,
                        'cultural_fit_score': candidate.cultural_fit_score,
                        'overall_rank': candidate.overall_rank,
                        'percentile': candidate.percentile,
                    },
                    'responses': candidate.response_id.get_all_answers() if candidate.response_id else {},
                    'aiAnalysis': {
                        'overallScore': candidate.ai_score_id.overall_score,
                        'scores': {
                            'technical': candidate.ai_score_id.technical_score,
                            'sales': candidate.ai_score_id.sales_score,
                            'communication': candidate.ai_score_id.communication_score,
                            'learning': candidate.ai_score_id.learning_score,
                            'culturalFit': candidate.ai_score_id.cultural_fit_score,
                        },
                        'strengths': candidate.ai_score_id.identified_strengths,
                        'skillGaps': candidate.ai_score_id.skill_gaps,
                        'recommendation': candidate.ai_score_id.ai_recommendation,
                        'redFlags': candidate.ai_score_id.red_flags_detail,
                        'confidence': candidate.ai_score_id.ai_confidence_score,
                    } if candidate.ai_score_id else None,
                    'humanReview': {
                        'overallScore': candidate.human_review_id.overall_score,
                        'scores': {
                            'technical': candidate.human_review_id.technical_score,
                            'sales': candidate.human_review_id.sales_score,
                            'communication': candidate.human_review_id.communication_score,
                            'learning': candidate.human_review_id.learning_score,
                            'culturalFit': candidate.human_review_id.cultural_fit_score,
                        },
                        'reviewerNotes': candidate.human_review_id.reviewer_notes,
                        'strengths': candidate.human_review_id.strengths,
                        'concerns': candidate.human_review_id.concerns,
                        'recommendation': candidate.human_review_id.recommendation,
                        'reviewDate': candidate.human_review_id.review_date.isoformat() if candidate.human_review_id.review_date else None,
                        'reviewer': candidate.human_review_id.reviewer_id.name,
                    } if candidate.human_review_id else None,
                    'auditLog': request.env['assessment.audit.log'].sudo().get_candidate_timeline(candidate.id),
                }
            }
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            _logger.exception("Error fetching candidate detail: %s", str(e))
            return {'success': False, 'error': str(e)}
    
    @http.route('/api/v1/dashboard/rankings', type='json', auth='user')
    def get_rankings(self, category='overall', limit=50):
        """Get candidate rankings/leaderboard"""
        try:
            rankings = request.env['assessment.ranking'].sudo().get_leaderboard(
                category=category, limit=int(limit)
            )
            
            return {
                'success': True,
                'data': {
                    'rankings': rankings,
                    'category': category,
                    'totalCandidates': len(rankings),
                }
            }
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            _logger.exception("Error fetching rankings: %s", str(e))
            return {'success': False, 'error': str(e)}
