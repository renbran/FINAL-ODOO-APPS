# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree
from odoo import api


class AccountPayment(models.Model):
    """This class inherits model "account.payment" and adds required fields """
    _inherit = "account.payment"
    _inherits = {'account.move': 'move_id'}

    def _compute_is_approve_person(self):
        """This function fetches the value of the
        'account_payment_approval.payment_approval' parameter using the
        get_param method and converts to integer, it checks if the current
        user's ID matches the ID stored in the 'approval_user_id'
        parameter. If both conditions are met, it sets the is_approve_person
         field to True"""
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        approver_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id'))
        self.is_approve_person = True if (self.env.user.id == approver_id and
                                          approval) else False

    is_approve_person = fields.Boolean(string='Approving Person',
                                       compute=_compute_is_approve_person,
                                       readonly=True,
                                       help="Enable/disable if approving"
                                            " person")

    is_locked = fields.Boolean(string='Locked', compute='_compute_is_locked', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.depends('state')
    def _compute_is_locked(self):
        for rec in self:
            # Allow editing only in draft and rejected states
            # Approved payments should be locked for editing but allow posting
            rec.is_locked = rec.state not in ['draft', 'rejected']

    def write(self, vals):
        """Override write to add workflow validation"""
        if 'state' in vals:
            for record in self:
                # Validate state transitions
                if record.state == 'posted' and vals['state'] != 'cancel':
                    raise UserError(_("Posted payments can only be cancelled."))
                if record.state == 'waiting_approval' and vals['state'] not in ['approved', 'rejected', 'cancel']:
                    raise UserError(_("Payments waiting for approval can only be approved, rejected, or cancelled."))
                if record.state == 'approved' and vals['state'] not in ['posted', 'cancel']:
                    raise UserError(_("Approved payments can only be posted or cancelled."))
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Overwrites the action_post() to validate the payment in the 'approved'
         stage too.
        currently Odoo allows payment posting only in draft stage."""
        # Skip approval check if called from approve_transfer or if already approved
        if not self.env.context.get('skip_approval_check') and self.state == 'draft':
            validation = self._check_payment_approval()
            if not validation:
                return False
                
        # Allow posting from both draft and approved states
        if self.state in ('posted', 'cancel', 'waiting_approval', 'rejected'):
            raise UserError(
                _("Only a draft or approved payment can be posted."))
        if any(inv.state != 'posted' for inv in
               self.reconciled_invoice_ids):
            raise ValidationError(_("The payment cannot be processed "
                                    "because the invoice is not open!"))
        # Call the parent's action_post method to ensure proper sequence generation
        # and all standard Odoo posting logic
        return super(AccountPayment, self).action_post()

    def _check_payment_approval(self):
        """This function checks the payment approval if payment_amount grater
         than amount,then state changed to waiting_approval """
        self.ensure_one()
        if self.state == "draft":
            first_approval = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval')
            if first_approval:
                amount = float(self.env['ir.config_parameter'].sudo().get_param(
                    'account_payment_approval.approval_amount'))
                payment_currency_id = int(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'account_payment_approval.approval_currency_id'))
                payment_amount = self.amount
                if payment_currency_id:
                    if (self.currency_id and
                            self.currency_id.id != payment_currency_id):
                        currency_id = self.env['res.currency'].browse(
                            payment_currency_id)
                        payment_amount = (self.currency_id._convert(
                            self.amount, currency_id, self.company_id,
                            self.date or fields.Date.today(), round=True))
                if payment_amount > amount:
                    self.write({
                        'state': 'waiting_approval'
                    })
                    return False
        return True

    def action_submit_review(self):
        """Submit the payment for review"""
        for record in self:
            if record.state == 'draft':
                record.state = 'waiting_approval'

    def approve_transfer(self):
        """This function changes state to approved state if approving person
         approves payment and automatically posts the payment"""
        for record in self:
            if record.state == 'waiting_approval' and record.is_approve_person:
                # First, set state to approved
                record.write({
                    'state': 'approved'
                })
                # Ensure the record is refreshed before posting
                record.invalidate_recordset()
                # Automatically post the payment after approval
                try:
                    # Post the payment directly from approved state
                    result = record.with_context(skip_approval_check=True).action_post()
                    return result
                except Exception as e:
                    # If posting fails, keep approved state and log the error
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.error(f"Failed to auto-post payment after approval: {str(e)}")
                    # Raise a user-friendly error but keep the approved state
                    raise UserError(f"Payment approved successfully but failed to post automatically: {str(e)}. You can manually post it from the approved state.")

    def reject_transfer(self):
        """Reject the payment transfer"""
        for record in self:
            if record.state == 'waiting_approval' and record.is_approve_person:
                record.state = 'rejected'
                # Allow draft and cancel actions after rejection
                record.is_locked = False

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                # Allow editing only in draft and rejected states
                node.set('edit', "0" if self.state not in ['draft', 'rejected'] else "1")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
