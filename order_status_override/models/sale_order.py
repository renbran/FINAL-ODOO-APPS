from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_status_id = fields.Many2one('order.status', string='Custom Status', 
                                      tracking=True, copy=False)
    custom_status_history_ids = fields.One2many('order.status.history', 'order_id', 
                                            string='Status History', copy=False)
    
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible')
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible')
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible')
    
    # Commission calculation fields
    internal_commission_ids = fields.One2many(
        'commission.internal', 
        'sale_order_id',
        string='Internal Commissions'
    )
    external_commission_ids = fields.One2many(
        'commission.external', 
        'sale_order_id',
        string='External Commissions'
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_total_commission',
        store=True,
        currency_field='currency_id'
    )
    
    # Report fields
    related_purchase_orders = fields.One2many(
        'purchase.order', 
        compute='_compute_related_documents',
        string='Related Purchase Orders'
    )
    related_vendor_bills = fields.One2many(
        'account.move',
        compute='_compute_related_documents', 
        string='Related Vendor Bills'
    )
    total_payment_out = fields.Monetary(
        string='Total Payment Out',
        compute='_compute_total_payment_out',
        currency_field='currency_id'
    )
    
    @api.depends('internal_commission_ids.amount_fixed', 'external_commission_ids.amount_fixed')
    def _compute_total_commission(self):
        """Calculate total commission from internal and external commission records"""
        for order in self:
            total = 0.0
            
            # Sum internal commissions
            for internal_comm in order.internal_commission_ids:
                total += internal_comm.amount_fixed
                
            # Sum external commissions  
            for external_comm in order.external_commission_ids:
                total += external_comm.amount_fixed
                
            order.total_commission_amount = total

    def _compute_related_documents(self):
        """Compute related purchase orders and vendor bills"""
        for order in self:
            # Find related purchase orders (by partner or project reference)
            purchase_orders = self.env['purchase.order'].search([
                '|',
                ('partner_id', '=', order.partner_id.id),
                ('origin', 'ilike', order.name)
            ])
            order.related_purchase_orders = purchase_orders
            
            # Find related vendor bills
            vendor_bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                '|',
                ('partner_id', '=', order.partner_id.id),
                ('ref', 'ilike', order.name)
            ])
            order.related_vendor_bills = vendor_bills

    @api.depends('related_vendor_bills', 'total_commission_amount')
    def _compute_total_payment_out(self):
        """Calculate total payment out (vendor bills + commissions)"""
        for order in self:
            vendor_total = sum(order.related_vendor_bills.mapped('amount_total'))
            order.total_payment_out = vendor_total + order.total_commission_amount

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        return records
    
    def action_change_status(self):
        """
        Open the status change wizard
        :return: Action dictionary
        """
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }


    def action_start_documentation_review(self):
        """Start documentation review process"""
        self.ensure_one()
        if not self.documentation_user_id:
            raise UserError(_("Please assign a user for documentation review before starting the process."))
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_review')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation Review status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation review started by %s") % self.env.user.name)
        
        # Create activity for documentation user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Review Documentation for Order %s") % self.name,
            note=_("Please review and prepare all required documentation for this order."),
            user_id=self.documentation_user_id.id
        )
        
        # Send notification email
        self._send_workflow_notification('documentation_review')
        
        return True

    def action_start_commission_calculation(self):
        """Start commission calculation process"""
        self.ensure_one()
        if not self.commission_user_id:
            raise UserError(_("Please assign a user for commission calculation before proceeding."))
        
        # Find the commission status
        commission_status = self.env['order.status'].search([('code', '=', 'commission_calculation')], limit=1)
        if not commission_status:
            raise UserError(_("Commission Calculation status not found in the system."))
        
        # Change to commission status
        self._change_status(commission_status.id, _("Commission calculation started by %s") % self.env.user.name)
        
        # Create activity for commission user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Calculate Commissions for Order %s") % self.name,
            note=_("Please calculate all commission amounts for agents, brokers, and other parties."),
            user_id=self.commission_user_id.id
        )
        
        # Send notification email
        self._send_workflow_notification('commission_calculation')
        
        return True

    def action_approve_and_post_order(self):
        """Approve the order and post as Sales Order"""
        self.ensure_one()
        
        # Validate commission calculations are complete
        if not self.total_commission_amount:
            raise UserError(_("Please complete commission calculations before approving the order."))
        
        # Find the approved status
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        # Change to approved status
        self._change_status(approved_status.id, _("Order approved and posted by %s") % self.env.user.name)
        
        # Confirm the sales order if not already confirmed
        if self.state == 'draft':
            self.action_confirm()
        
        # Send approval notification
        self._send_workflow_notification('approved')
        
        # Create success message
        self.message_post(
            body=_("Order has been approved and posted as Sales Order. Total commission amount: %s") % 
                 self.currency_id.symbol + str(self.total_commission_amount),
            subject=_("Order Approved and Posted"),
            message_type='notification'
        )
        
        return True

    def _send_workflow_notification(self, stage):
        """Send automated email notification for workflow stages"""
        email_template = None
        recipient_user = None
        
        if stage == 'documentation_review':
            email_template = self.env.ref('order_status_override.email_template_documentation_review', raise_if_not_found=False)
            recipient_user = self.documentation_user_id
        elif stage == 'commission_calculation':
            email_template = self.env.ref('order_status_override.email_template_commission_calculation', raise_if_not_found=False)
            recipient_user = self.commission_user_id
        elif stage == 'approved':
            email_template = self.env.ref('order_status_override.email_template_order_approved', raise_if_not_found=False)
            # Send to the order creator and sales team
            
        if email_template and recipient_user:
            try:
                email_template.send_mail(self.id, force_send=True)
                _logger.info(f"Workflow notification sent for {stage} to user {recipient_user.name}")
            except Exception as e:
                _logger.warning(f"Failed to send workflow notification: {str(e)}")
    
    def action_reject_order(self):
        """Reject the order and return to draft"""
        self.ensure_one()
        # Check if current user can reject
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can reject orders."))
        
        # Find the draft status
        draft_status = self.env['order.status'].search([('code', '=', 'draft')], limit=1)
        if not draft_status:
            raise UserError(_("Draft status not found in the system."))
        
        # Change to draft status
        self._change_status(draft_status.id, _("Order rejected by %s and returned to draft") % self.env.user.name)
        
        # Send rejection notification
        self.message_post(
            body=_("Order has been rejected and returned to draft status for revision."),
            subject=_("Order Rejected"),
            message_type='notification'
        )
        
        return True

    def action_view_order_reports(self):
        """Open the order reports wizard with current order context"""
        return {
            'name': _('Generate Order Reports'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_date_from': self.date_order.date() if self.date_order else fields.Date.today(),
                'default_date_to': self.date_order.date() if self.date_order else fields.Date.today(),
                'default_partner_ids': [(6, 0, [self.partner_id.id])],
                'default_report_type': 'comprehensive',
            }
        }

    def action_submit_for_review(self):
        """Submit order for final review"""
        self.ensure_one()
        if not self.final_review_user_id:
            raise UserError(_("Please assign a user for final review before submitting."))
        
        # Find the final review status
        review_status = self.env['order.status'].search([('code', '=', 'final_review')], limit=1)
        if not review_status:
            raise UserError(_("Final review status not found in the system."))
        
        # Change to final review status
        self._change_status(review_status.id, _("Order submitted for final review by %s") % self.env.user.name)
        
        # Create activity for reviewer
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Review Order %s") % self.name,
            note=_("This order is ready for final review and approval/rejection."),
            user_id=self.final_review_user_id.id
        )
        
        return True
    
    def action_return_to_previous(self):
        """Return order to previous stage"""
        self.ensure_one()
        # Get previous status from history
        last_history = self.env['order.status.history'].search([
            ('order_id', '=', self.id)
        ], order='create_date desc', limit=2)
        
        if len(last_history) < 2:
            raise UserError(_("No previous status found to return to."))
        
        previous_status = last_history[1].status_id
        
        # Change to previous status
        self._change_status(previous_status.id, _("Order returned to previous stage by %s") % self.env.user.name)
        
        return True
    
    def action_request_documentation(self):
        """Start documentation process"""
        self.ensure_one()
        if not self.documentation_user_id:
            raise UserError(_("Please assign a user for documentation before starting the process."))
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_progress')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation progress status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation process started by %s") % self.env.user.name)
        
        # Create activity for documentation user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Prepare Documentation for Order %s") % self.name,
            note=_("Please prepare all required documentation for this order."),
            user_id=self.documentation_user_id.id
        )
        
        return True
    
    def _change_status(self, new_status_id, notes=False):
        """Helper method to change status and create history entry"""
        old_status_id = self.custom_status_id.id
        self.custom_status_id = new_status_id
        
        # Create history entry
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': new_status_id,
            'previous_status_id': old_status_id,
            'notes': notes or _('Status changed')
        })
        
        # Create activity based on the responsible type
        new_status = self.env['order.status'].browse(new_status_id)
        self._create_activity_for_status(new_status)
        
        return True
    
    def _create_activity_for_status(self, status):
        """Create an activity for the responsible user based on status"""
        user_id = False
        summary = _("Process Sale Order ") + self.name
        note = _("Please process the sale order as per the '%s' stage.") % status.name
        
        if status.responsible_type == 'documentation':
            user_id = self.documentation_user_id.id
        elif status.responsible_type == 'commission':
            user_id = self.commission_user_id.id
        elif status.responsible_type == 'final_review':
            user_id = self.final_review_user_id.id
        
        if user_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=summary,
                note=note,
                user_id=user_id
            )