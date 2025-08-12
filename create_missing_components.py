#!/usr/bin/env python3
"""
FINAL RESTORATION: Create remaining missing files and directories
"""

import os
from pathlib import Path

def create_missing_components():
    """Create missing reports, wizards, and demo files"""
    
    print("=== CREATING MISSING COMPONENTS ===")
    
    module_path = Path("account_payment_approval")
    
    # 1. Create reports directory and files
    print("\n1. CREATING REPORTS...")
    create_reports(module_path)
    
    # 2. Create wizards directory and files
    print("\n2. CREATING WIZARDS...")
    create_wizards(module_path)
    
    # 3. Create demo directory and files
    print("\n3. CREATING DEMO DATA...")
    create_demo(module_path)
    
    # 4. Create remaining templates
    print("\n4. CREATING TEMPLATES...")
    create_templates(module_path)
    
    print("\n=== ALL COMPONENTS CREATED ===")
    print("✅ Module is now complete with all referenced files")
    
    return True

def create_reports(module_path):
    """Create reports directory and report files"""
    reports_dir = module_path / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    # Payment voucher report
    voucher_report_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Payment Voucher Report -->
        <record id="action_report_payment_voucher" model="ir.actions.report">
            <field name="name">Payment Voucher</field>
            <field name="model">account.payment</field>
            <field name="report_type">qweb-pdf</field>
            <field name="report_name">account_payment_approval.report_payment_voucher</field>
            <field name="report_file">account_payment_approval.report_payment_voucher</field>
            <field name="binding_model_id" ref="account.model_account_payment"/>
            <field name="binding_type">report</field>
        </record>
        
        <!-- Payment Voucher Template -->
        <template id="report_payment_voucher">
            <t t-call="web.html_container">
                <t t-foreach="docs" t-as="doc">
                    <t t-call="web.external_layout">
                        <div class="page">
                            <div class="oe_structure"/>
                            <div class="row">
                                <div class="col-12">
                                    <h2>
                                        <span t-if="doc.voucher_type == 'payment'">Payment Voucher</span>
                                        <span t-if="doc.voucher_type == 'receipt'">Receipt Voucher</span>
                                    </h2>
                                </div>
                            </div>
                            
                            <div class="row mt32 mb32">
                                <div class="col-6">
                                    <strong>Voucher Number:</strong> <span t-field="doc.voucher_number"/>
                                </div>
                                <div class="col-6">
                                    <strong>Date:</strong> <span t-field="doc.date"/>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-6">
                                    <strong>Partner:</strong> <span t-field="doc.partner_id"/>
                                </div>
                                <div class="col-6">
                                    <strong>Amount:</strong> <span t-field="doc.amount"/> <span t-field="doc.currency_id.name"/>
                                </div>
                            </div>
                            
                            <div class="row mt32">
                                <div class="col-12">
                                    <strong>Status:</strong> <span t-field="doc.voucher_state"/>
                                </div>
                            </div>
                            
                            <!-- Signatures Section -->
                            <div class="row mt32" t-if="doc.creator_signature_date">
                                <div class="col-12">
                                    <h4>Signatures</h4>
                                    <table class="table table-sm">
                                        <tr t-if="doc.creator_signature_date">
                                            <td><strong>Created by:</strong></td>
                                            <td><span t-field="doc.create_uid.name"/></td>
                                            <td><span t-field="doc.creator_signature_date"/></td>
                                        </tr>
                                        <tr t-if="doc.reviewer_signature_date">
                                            <td><strong>Reviewed by:</strong></td>
                                            <td><span t-field="doc.reviewer_id.name"/></td>
                                            <td><span t-field="doc.reviewer_signature_date"/></td>
                                        </tr>
                                        <tr t-if="doc.approver_signature_date">
                                            <td><strong>Approved by:</strong></td>
                                            <td><span t-field="doc.approver_id.name"/></td>
                                            <td><span t-field="doc.approver_signature_date"/></td>
                                        </tr>
                                        <tr t-if="doc.authorizer_signature_date">
                                            <td><strong>Authorized by:</strong></td>
                                            <td><span t-field="doc.authorizer_id.name"/></td>
                                            <td><span t-field="doc.authorizer_signature_date"/></td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- QR Code Section -->
                            <div class="row mt32" t-if="doc.qr_code">
                                <div class="col-12 text-center">
                                    <h5>Verification QR Code</h5>
                                    <img t-att-src="image_data_uri(doc.qr_code)" style="max-width: 150px;"/>
                                    <br/>
                                    <small><span t-field="doc.verification_url"/></small>
                                </div>
                            </div>
                            
                            <div class="oe_structure"/>
                        </div>
                    </t>
                </t>
            </t>
        </template>
    </data>
</odoo>'''
    
    with open(reports_dir / 'payment_voucher_report.xml', 'w', encoding='utf-8') as f:
        f.write(voucher_report_content)
    
    # Payment summary report
    summary_report_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Payment Summary Report -->
        <record id="action_report_payment_summary" model="ir.actions.report">
            <field name="name">Payment Summary</field>
            <field name="model">account.payment</field>
            <field name="report_type">qweb-pdf</field>
            <field name="report_name">account_payment_approval.report_payment_summary</field>
            <field name="report_file">account_payment_approval.report_payment_summary</field>
        </record>
        
        <!-- Payment Summary Template -->
        <template id="report_payment_summary">
            <t t-call="web.html_container">
                <div class="page">
                    <div class="oe_structure"/>
                    <div class="row">
                        <div class="col-12">
                            <h2>Payment Summary Report</h2>
                        </div>
                    </div>
                    
                    <table class="table table-sm o_main_table">
                        <thead>
                            <tr>
                                <th>Voucher #</th>
                                <th>Date</th>
                                <th>Partner</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="docs" t-as="doc">
                                <tr>
                                    <td><span t-field="doc.voucher_number"/></td>
                                    <td><span t-field="doc.date"/></td>
                                    <td><span t-field="doc.partner_id.name"/></td>
                                    <td><span t-field="doc.amount"/> <span t-field="doc.currency_id.name"/></td>
                                    <td><span t-field="doc.voucher_state"/></td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                    
                    <div class="oe_structure"/>
                </div>
            </t>
        </template>
    </data>
</odoo>'''
    
    with open(reports_dir / 'payment_summary_report.xml', 'w', encoding='utf-8') as f:
        f.write(summary_report_content)
    
    print("   ✅ Reports created")

def create_wizards(module_path):
    """Create wizards directory and wizard files"""
    wizards_dir = module_path / 'wizards'
    wizards_dir.mkdir(exist_ok=True)
    
    # Wizards __init__.py
    with open(wizards_dir / '__init__.py', 'w', encoding='utf-8') as f:
        f.write('# -*- coding: utf-8 -*-\nfrom . import payment_bulk_approval_wizard\nfrom . import payment_rejection_wizard\n')
    
    # Bulk approval wizard
    bulk_wizard_content = '''# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaymentBulkApprovalWizard(models.TransientModel):
    _name = 'payment.bulk.approval.wizard'
    _description = 'Bulk Payment Approval Wizard'
    
    payment_ids = fields.Many2many('account.payment', string='Payments')
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('authorize', 'Authorize'),
    ], string='Action', required=True)
    
    notes = fields.Text(string='Notes')
    
    def action_process_payments(self):
        """Process bulk payment actions"""
        if not self.payment_ids:
            raise UserError(_("No payments selected"))
        
        processed = 0
        for payment in self.payment_ids:
            try:
                if self.action_type == 'approve':
                    payment.action_approve()
                elif self.action_type == 'reject':
                    payment.action_reject()
                elif self.action_type == 'authorize':
                    payment.action_authorize()
                processed += 1
            except Exception as e:
                continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('%d payments processed successfully') % processed,
                'type': 'success',
                'sticky': False,
            }
        }
'''
    
    with open(wizards_dir / 'payment_bulk_approval_wizard.py', 'w', encoding='utf-8') as f:
        f.write(bulk_wizard_content)
    
    # Rejection wizard
    rejection_wizard_content = '''# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PaymentRejectionWizard(models.TransientModel):
    _name = 'payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'
    
    payment_id = fields.Many2one('account.payment', string='Payment', required=True)
    reason = fields.Text(string='Rejection Reason', required=True)
    
    def action_reject_payment(self):
        """Reject payment with reason"""
        self.payment_id.message_post(
            body=_("Payment rejected. Reason: %s") % self.reason,
            message_type='notification'
        )
        self.payment_id.action_reject()
        
        return {'type': 'ir.actions.act_window_close'}
'''
    
    with open(wizards_dir / 'payment_rejection_wizard.py', 'w', encoding='utf-8') as f:
        f.write(rejection_wizard_content)
    
    print("   ✅ Wizards created")

def create_demo(module_path):
    """Create demo directory and demo data"""
    demo_dir = module_path / 'demo'
    demo_dir.mkdir(exist_ok=True)
    
    demo_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Demo Payment Data -->
        <record id="demo_payment_1" model="account.payment">
            <field name="payment_type">outbound</field>
            <field name="partner_type">supplier</field>
            <field name="partner_id" ref="base.res_partner_12"/>
            <field name="amount">1500.00</field>
            <field name="journal_id" ref="account.bank_journal"/>
            <field name="voucher_state">draft</field>
        </record>
        
        <record id="demo_payment_2" model="account.payment">
            <field name="payment_type">inbound</field>
            <field name="partner_type">customer</field>
            <field name="partner_id" ref="base.res_partner_1"/>
            <field name="amount">2500.00</field>
            <field name="journal_id" ref="account.bank_journal"/>
            <field name="voucher_state">submitted</field>
        </record>
    </data>
</odoo>'''
    
    with open(demo_dir / 'demo_data.xml', 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    print("   ✅ Demo data created")

def create_templates(module_path):
    """Create QR verification templates"""
    views_dir = module_path / 'views'
    
    # QR verification templates
    qr_templates_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- QR Verification Success Template -->
        <template id="verification_success" name="Payment Verification Success">
            <t t-call="website.layout">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="alert alert-success text-center">
                                <h2><i class="fa fa-check-circle"/> Payment Verified</h2>
                                <p>This payment voucher has been successfully verified.</p>
                                
                                <div class="card mt-4">
                                    <div class="card-body">
                                        <h5>Payment Details</h5>
                                        <p><strong>Voucher Number:</strong> <span t-esc="payment.voucher_number"/></p>
                                        <p><strong>Amount:</strong> <span t-esc="payment.amount"/> <span t-esc="payment.currency_id.name"/></p>
                                        <p><strong>Partner:</strong> <span t-esc="payment.partner_id.name"/></p>
                                        <p><strong>Status:</strong> <span t-esc="payment.voucher_state"/></p>
                                        <p><strong>Date:</strong> <span t-esc="payment.date"/></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </t>
        </template>
        
        <!-- QR Verification Error Template -->
        <template id="verification_error" name="Payment Verification Error">
            <t t-call="website.layout">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="alert alert-danger text-center">
                                <h2><i class="fa fa-exclamation-triangle"/> Verification Failed</h2>
                                <p t-esc="error"/>
                                <p>Please contact the payment issuer for assistance.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </t>
        </template>
    </data>
</odoo>'''
    
    with open(views_dir / 'qr_verification_templates.xml', 'w', encoding='utf-8') as f:
        f.write(qr_templates_content)
    
    print("   ✅ Templates created")

if __name__ == "__main__":
    success = create_missing_components()
    exit(0 if success else 1)
