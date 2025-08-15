from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import qrcode
import io
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Core workflow fields
    custom_status_id = fields.Many2one('order.status', string='Custom Status', 
                                      tracking=True, copy=False)
    custom_status_history_ids = fields.One2many('order.status.history', 'order_id', 
                                            string='Status History', copy=False)
    
    # User assignments for each stage
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible')
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible')
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible')
    
    # Real Estate specific fields
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, tracking=True)
    project_id = fields.Many2one('product.template', string='Project', tracking=True)
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)
    
    # Commission fields - External
    broker_partner_id = fields.Many2one('res.partner', string="Broker Partner", tracking=True)
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Rate (%)", default=0.0, digits=(5, 2))
    broker_amount = fields.Monetary(string="Broker Commission Amount", 
                                  compute="_compute_commissions", store=True)
    
    referrer_partner_id = fields.Many2one('res.partner', string="Referrer Partner", tracking=True)
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Rate (%)", default=0.0, digits=(5, 2))
    referrer_amount = fields.Monetary(string="Referrer Commission Amount", 
                                    compute="_compute_commissions", store=True)
    
    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner", tracking=True)
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate (%)", default=0.0, digits=(5, 2))
    cashback_amount = fields.Monetary(string="Cashback Amount", 
                                    compute="_compute_commissions", store=True)
    
    # Commission fields - Internal
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1", tracking=True)
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 1 Commission Type", default='percent_unit_price')
    agent1_rate = fields.Float(string="Agent 1 Rate (%)", default=0.0, digits=(5, 2))
    agent1_amount = fields.Monetary(string="Agent 1 Commission", 
                                  compute="_compute_commissions", store=True)
    
    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2", tracking=True)
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 2 Commission Type", default='percent_unit_price')
    agent2_rate = fields.Float(string="Agent 2 Rate (%)", default=0.0, digits=(5, 2))
    agent2_amount = fields.Monetary(string="Agent 2 Commission", 
                                  compute="_compute_commissions", store=True)
    
    manager_partner_id = fields.Many2one('res.partner', string="Manager Partner", tracking=True)
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_unit_price')
    manager_rate = fields.Float(string="Manager Rate (%)", default=0.0, digits=(5, 2))
    manager_amount = fields.Monetary(string="Manager Commission Amount", 
                                   compute="_compute_commissions", store=True)
    
    director_partner_id = fields.Many2one('res.partner', string="Director Partner", tracking=True)
    director_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Commission Type", default='percent_unit_price')
    director_rate = fields.Float(string="Director Rate (%)", default=3.0, digits=(5, 2))
    director_amount = fields.Monetary(string="Director Commission Amount", 
                                    compute="_compute_commissions", store=True)
    
    # Summary fields
    total_external_commission_amount = fields.Monetary(string="Total External Commissions", 
                                                     compute="_compute_commissions", store=True)
    total_internal_commission_amount = fields.Monetary(string="Total Internal Commissions", 
                                                     compute="_compute_commissions", store=True)
    total_commission_amount = fields.Monetary(string="Total Commission Amount", 
                                            compute="_compute_commissions", store=True)
    
    # QR Code for verification
    qr_code = fields.Binary(string="QR Code", compute="_compute_qr_code", store=True)
    
    # Report fields - Legacy compatibility
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
    
    @api.depends('broker_rate', 'broker_commission_type', 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type', 'agent1_rate', 'agent1_commission_type',
                 'agent2_rate', 'agent2_commission_type', 'manager_rate', 'manager_commission_type',
                 'director_rate', 'director_commission_type', 'amount_untaxed', 'order_line.price_unit')
    def _compute_commissions(self):
        """Calculate all commission amounts based on configured rates and types"""
        for order in self:
            # External commissions
            order.broker_amount = order._calculate_commission_amount(
                order.broker_rate, order.broker_commission_type, order)
            order.referrer_amount = order._calculate_commission_amount(
                order.referrer_rate, order.referrer_commission_type, order)
            order.cashback_amount = order._calculate_commission_amount(
                order.cashback_rate, order.cashback_commission_type, order)
            
            # Internal commissions
            order.agent1_amount = order._calculate_commission_amount(
                order.agent1_rate, order.agent1_commission_type, order)
            order.agent2_amount = order._calculate_commission_amount(
                order.agent2_rate, order.agent2_commission_type, order)
            order.manager_amount = order._calculate_commission_amount(
                order.manager_rate, order.manager_commission_type, order)
            order.director_amount = order._calculate_commission_amount(
                order.director_rate, order.director_commission_type, order)
            
            # Summary totals
            order.total_external_commission_amount = (
                order.broker_amount + order.referrer_amount + order.cashback_amount)
            order.total_internal_commission_amount = (
                order.agent1_amount + order.agent2_amount + 
                order.manager_amount + order.director_amount)
            order.total_commission_amount = (
                order.total_external_commission_amount + order.total_internal_commission_amount)

    def _calculate_commission_amount(self, rate, commission_type, order):
        """Calculate commission amount based on rate and type"""
        if not rate or rate <= 0:
            return 0.0
        
        if commission_type == 'fixed':
            return rate
        elif commission_type == 'percent_unit_price':
            # Calculate based on unit price of first line
            if order.order_line:
                unit_price = order.order_line[0].price_unit
                return (rate / 100) * unit_price
            return 0.0
        elif commission_type == 'percent_untaxed_total':
            return (rate / 100) * order.amount_untaxed
        
        return 0.0

    @api.depends('name', 'partner_id.name')
    def _compute_qr_code(self):
        """Generate QR code for order verification"""
        for order in self:
            if order.name:
                qr_data = f"Order: {order.name}\nCustomer: {order.partner_id.name}\nAmount: {order.amount_total} {order.currency_id.name}"
                
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    order.qr_code = base64.b64encode(buffer.getvalue())
                except Exception as e:
                    _logger.warning(f"Failed to generate QR code for order {order.name}: {e}")
                    order.qr_code = False
            else:
                order.qr_code = False
    
    # Report fields - Legacy compatibility
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

    @api.depends('partner_id', 'order_line', 'order_line.product_id')
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