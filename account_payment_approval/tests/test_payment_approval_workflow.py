# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, timedelta
import base64


@tagged('post_install', '-at_install', 'payment_approval')
class TestPaymentApprovalWorkflow(TransactionCase):
    """Test payment approval workflow functionality"""

    def setUp(self):
        super().setUp()
        
        # Create test users with different roles
        self.user_creator = self.env['res.users'].create({
            'name': 'Payment Creator',
            'login': 'creator@test.com',
            'email': 'creator@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('account_payment_approval.group_payment_voucher_user').id,
                self.env.ref('base.group_user').id
            ])]
        })
        
        self.user_reviewer = self.env['res.users'].create({
            'name': 'Payment Reviewer',
            'login': 'reviewer@test.com',
            'email': 'reviewer@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('account_payment_approval.group_payment_voucher_reviewer').id,
                self.env.ref('base.group_user').id
            ])]
        })
        
        self.user_approver = self.env['res.users'].create({
            'name': 'Payment Approver',
            'login': 'approver@test.com',
            'email': 'approver@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('account_payment_approval.group_payment_voucher_approver').id,
                self.env.ref('base.group_user').id
            ])]
        })
        
        self.user_authorizer = self.env['res.users'].create({
            'name': 'Payment Authorizer',
            'login': 'authorizer@test.com',
            'email': 'authorizer@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('account_payment_approval.group_payment_voucher_authorizer').id,
                self.env.ref('base.group_user').id
            ])]
        })
        
        self.user_poster = self.env['res.users'].create({
            'name': 'Payment Poster',
            'login': 'poster@test.com',
            'email': 'poster@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('account_payment_approval.group_payment_voucher_poster').id,
                self.env.ref('base.group_user').id
            ])]
        })
        
        # Create test partner
        self.test_partner = self.env['res.partner'].create({
            'name': 'Test Vendor',
            'supplier_rank': 1,
            'email': 'vendor@test.com'
        })
        
        # Create test journal
        self.test_journal = self.env['account.journal'].create({
            'name': 'Test Bank Journal',
            'type': 'bank',
            'code': 'TBANK',
        })

    def _create_test_payment(self, payment_type='outbound', amount=1000.0, user=None):
        """Helper method to create test payment"""
        if user:
            payment = self.env['account.payment'].with_user(user).create({
                'partner_id': self.test_partner.id,
                'payment_type': payment_type,
                'amount': amount,
                'ref': f'Test {payment_type} payment',
                'journal_id': self.test_journal.id,
            })
        else:
            payment = self.env['account.payment'].create({
                'partner_id': self.test_partner.id,
                'payment_type': payment_type,
                'amount': amount,
                'ref': f'Test {payment_type} payment',
                'journal_id': self.test_journal.id,
            })
        return payment

    def test_payment_creation_and_initial_state(self):
        """Test payment creation and initial state"""
        payment = self._create_test_payment()
        
        # Test initial state
        self.assertEqual(payment.voucher_state, 'draft')
        self.assertFalse(payment.voucher_number)
        self.assertTrue(payment.amount_in_words)
        self.assertTrue(payment.verification_token)

    def test_payment_voucher_workflow(self):
        """Test complete payment voucher workflow (4 stages)"""
        payment = self._create_test_payment(payment_type='outbound')
        
        # Stage 1: Submit for approval
        self.assertTrue(payment.can_submit_for_approval())
        payment.action_submit_for_approval()
        self.assertEqual(payment.voucher_state, 'submitted')
        self.assertTrue(payment.voucher_number)
        
        # Stage 2: Review
        self.assertTrue(payment.can_review())
        payment.with_user(self.user_reviewer).action_review()
        self.assertEqual(payment.voucher_state, 'reviewed')
        
        # Stage 3: Approve
        self.assertTrue(payment.can_approve())
        payment.with_user(self.user_approver).action_approve()
        self.assertEqual(payment.voucher_state, 'approved')
        
        # Stage 4: Authorize
        self.assertTrue(payment.can_authorize())
        payment.with_user(self.user_authorizer).action_authorize()
        self.assertEqual(payment.voucher_state, 'authorized')
        
        # Final: Post
        self.assertTrue(payment.can_post())
        payment.with_user(self.user_poster).action_post()
        self.assertEqual(payment.voucher_state, 'posted')

    def test_receipt_voucher_workflow(self):
        """Test receipt voucher workflow (3 stages)"""
        payment = self._create_test_payment(payment_type='inbound')
        
        # Stage 1: Submit for approval
        payment.action_submit_for_approval()
        self.assertEqual(payment.voucher_state, 'submitted')
        
        # Stage 2: Review (skips approval for receipts)
        payment.with_user(self.user_reviewer).action_review()
        self.assertEqual(payment.voucher_state, 'reviewed')
        
        # Stage 3: Authorize (directly from reviewed)
        self.assertTrue(payment.can_authorize())
        payment.with_user(self.user_authorizer).action_authorize()
        self.assertEqual(payment.voucher_state, 'authorized')
        
        # Final: Post
        payment.with_user(self.user_poster).action_post()
        self.assertEqual(payment.voucher_state, 'posted')

    def test_payment_rejection(self):
        """Test payment rejection at different stages"""
        # Test rejection during review
        payment = self._create_test_payment()
        payment.action_submit_for_approval()
        
        self.assertTrue(payment.can_reject())
        payment.with_user(self.user_reviewer).action_reject()
        self.assertEqual(payment.voucher_state, 'rejected')
        
        # Test rejection during approval
        payment2 = self._create_test_payment()
        payment2.action_submit_for_approval()
        payment2.with_user(self.user_reviewer).action_review()
        
        self.assertTrue(payment2.can_reject())
        payment2.with_user(self.user_approver).action_reject()
        self.assertEqual(payment2.voucher_state, 'rejected')

    def test_voucher_number_generation(self):
        """Test voucher number generation"""
        # Test payment voucher numbering
        payment1 = self._create_test_payment(payment_type='outbound')
        payment1.action_submit_for_approval()
        self.assertTrue(payment1.voucher_number.startswith('PV-'))
        
        # Test receipt voucher numbering
        payment2 = self._create_test_payment(payment_type='inbound')
        payment2.action_submit_for_approval()
        self.assertTrue(payment2.voucher_number.startswith('RV-'))
        
        # Test sequential numbering
        payment3 = self._create_test_payment(payment_type='outbound')
        payment3.action_submit_for_approval()
        self.assertNotEqual(payment1.voucher_number, payment3.voucher_number)

    def test_amount_in_words_conversion(self):
        """Test amount to words conversion"""
        payment = self._create_test_payment(amount=1234.56)
        self.assertIn('one thousand', payment.amount_in_words.lower())
        self.assertIn('two hundred', payment.amount_in_words.lower())
        
        # Test zero amount
        payment_zero = self._create_test_payment(amount=0.0)
        self.assertIn('zero', payment_zero.amount_in_words.lower())

    def test_workflow_constraints(self):
        """Test workflow state constraints"""
        payment = self._create_test_payment()
        
        # Cannot review before submission
        with self.assertRaises(UserError):
            payment.action_review()
        
        # Cannot approve before review
        payment.action_submit_for_approval()
        with self.assertRaises(UserError):
            payment.action_approve()
        
        # Cannot authorize before approval (for payment vouchers)
        payment.with_user(self.user_reviewer).action_review()
        with self.assertRaises(UserError):
            payment.action_authorize()

    def test_security_permissions(self):
        """Test security permissions for different user roles"""
        payment = self._create_test_payment()
        payment.action_submit_for_approval()
        
        # Test reviewer cannot approve
        with self.assertRaises(AccessError):
            payment.with_user(self.user_reviewer).action_approve()
        
        # Test approver cannot authorize
        payment.with_user(self.user_reviewer).action_review()
        with self.assertRaises(AccessError):
            payment.with_user(self.user_approver).action_authorize()
        
        # Test creator cannot review their own payment
        payment_self = self._create_test_payment(user=self.user_creator)
        payment_self.action_submit_for_approval()
        with self.assertRaises(AccessError):
            payment_self.with_user(self.user_creator).action_review()

    def test_payment_modification_restrictions(self):
        """Test payment modification restrictions after submission"""
        payment = self._create_test_payment()
        payment.action_submit_for_approval()
        
        # Should not be able to modify amount after submission
        with self.assertRaises(ValidationError):
            payment.amount = 2000.0
        
        # Should not be able to modify partner after submission
        with self.assertRaises(ValidationError):
            payment.partner_id = self.env['res.partner'].create({'name': 'New Partner'})

    def test_payment_dashboard_data(self):
        """Test payment approval dashboard data"""
        # Create payments in different states
        payment1 = self._create_test_payment()
        payment1.action_submit_for_approval()
        
        payment2 = self._create_test_payment()
        payment2.action_submit_for_approval()
        payment2.with_user(self.user_reviewer).action_review()
        
        payment3 = self._create_test_payment()
        payment3.action_submit_for_approval()
        payment3.with_user(self.user_reviewer).action_review()
        payment3.with_user(self.user_approver).action_approve()
        
        # Test dashboard data
        dashboard_data = self.env['account.payment'].get_approval_dashboard_data()
        
        self.assertTrue(dashboard_data['success'])
        self.assertIn('stats', dashboard_data)
        self.assertIn('user_permissions', dashboard_data)
        
        stats = dashboard_data['stats']
        self.assertGreaterEqual(stats.get('pending_review', 0), 1)
        self.assertGreaterEqual(stats.get('pending_approval', 0), 1)
        self.assertGreaterEqual(stats.get('pending_authorization', 0), 1)

    def test_payment_search_and_filtering(self):
        """Test payment search and filtering capabilities"""
        # Create payments with different states
        draft_payment = self._create_test_payment()
        submitted_payment = self._create_test_payment()
        submitted_payment.action_submit_for_approval()
        
        # Test domain filters
        draft_payments = self.env['account.payment'].search([('voucher_state', '=', 'draft')])
        self.assertIn(draft_payment, draft_payments)
        
        submitted_payments = self.env['account.payment'].search([('voucher_state', '=', 'submitted')])
        self.assertIn(submitted_payment, submitted_payments)
        
        # Test amount filters
        high_amount_payments = self.env['account.payment'].search([('amount', '>', 500)])
        self.assertIn(draft_payment, high_amount_payments)

    def test_payment_reporting(self):
        """Test payment reporting functionality"""
        payment = self._create_test_payment()
        payment.action_submit_for_approval()
        
        # Test PDF generation (basic check)
        report_action = self.env.ref('account_payment_approval.action_report_payment_voucher')
        self.assertTrue(report_action)
        
        # Test QR verification report
        qr_report_action = self.env.ref('account_payment_approval.action_report_qr_verification')
        self.assertTrue(qr_report_action)

    def test_currency_and_multi_company(self):
        """Test currency handling and multi-company scenarios"""
        # Create USD currency payment
        usd_currency = self.env.ref('base.USD')
        payment_usd = self.env['account.payment'].create({
            'partner_id': self.test_partner.id,
            'payment_type': 'outbound',
            'amount': 1000.0,
            'currency_id': usd_currency.id,
            'ref': 'USD Test payment',
            'journal_id': self.test_journal.id,
        })
        
        self.assertEqual(payment_usd.currency_id, usd_currency)
        self.assertIn('dollar', payment_usd.amount_in_words.lower())

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        payment = self._create_test_payment()
        
        # Test invalid state transitions
        with self.assertRaises((UserError, ValidationError)):
            payment.voucher_state = 'posted'  # Skip workflow
        
        # Test invalid amount
        with self.assertRaises(ValidationError):
            invalid_payment = self.env['account.payment'].create({
                'partner_id': self.test_partner.id,
                'payment_type': 'outbound',
                'amount': -100.0,  # Negative amount
                'journal_id': self.test_journal.id,
            })

    def test_workflow_completion_time_tracking(self):
        """Test workflow completion time tracking"""
        payment = self._create_test_payment()
        
        start_time = datetime.now()
        payment.action_submit_for_approval()
        
        # Check that workflow times are being tracked
        self.assertTrue(payment.creator_signature_date)
        self.assertGreaterEqual(payment.creator_signature_date, start_time.replace(microsecond=0))
        
        # Continue workflow and check timing
        payment.with_user(self.user_reviewer).action_review()
        self.assertTrue(payment.reviewer_signature_date)
        self.assertGreater(payment.reviewer_signature_date, payment.creator_signature_date)
