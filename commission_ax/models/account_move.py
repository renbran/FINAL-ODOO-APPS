# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Override invoice posting to send email to agent1_partner when deal is invoiced."""
        result = super(AccountMove, self).action_post()
        
        for move in self:
            # Only process customer invoices
            if move.move_type == 'out_invoice' and move.state == 'posted':
                # Check if this invoice is related to a sale order with agent1_partner
                sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
                
                for order in sale_orders:
                    # Skip if email already sent or no agent1_partner
                    if not order.agent1_partner_id or order.agent_email_sent:
                        continue
                        
                    # Skip if agent1_partner has no email
                    if not order.agent1_partner_id.email:
                        _logger.warning(f"Agent 1 ({order.agent1_partner_id.name}) has no email address for order {order.name}")
                        continue
                        
                    try:
                        # Get email template with ID 53
                        email_template = self.env['mail.template'].browse(53)
                        
                        if email_template and email_template.exists():
                            # Prepare template context
                            template_context = move._get_invoice_agent_email_context()
                            
                            # Send email to agent1_partner
                            email_template.with_context(**template_context).send_mail(
                                move.id,
                                force_send=True,
                                email_values={
                                    'email_to': order.agent1_partner_id.email,
                                    'recipient_ids': [(4, order.agent1_partner_id.id)]
                                }
                            )
                            
                            # Mark email as sent
                            order.agent_email_sent = True
                            
                            # Log the action
                            order.message_post(
                                body=_("Invoice notification email sent to Agent 1: %s (%s)") % (
                                    order.agent1_partner_id.name, 
                                    order.agent1_partner_id.email
                                ),
                                subject=_("Agent Invoice Notification Sent")
                            )
                            
                            _logger.info(f"Invoice notification email sent to {order.agent1_partner_id.name} for order {order.name}")
                        else:
                            _logger.warning(f"Email template with ID 53 not found for order {order.name}")
                            
                    except Exception as e:
                        _logger.error(f"Failed to send invoice notification email for order {order.name}: {str(e)}")
                        
        return result
    
    def _get_invoice_agent_email_context(self):
        """Prepare context for agent email template."""
        sale_orders = self.invoice_line_ids.mapped('sale_line_ids.order_id')
        order = sale_orders and sale_orders[0]  # Get first order
        
        return {
            'invoice_id': self.id,
            'invoice_name': self.name,
            'invoice_amount': self.amount_total,
            'sale_order_id': order.id if order else False,
            'sale_order_name': order.name if order else False,
            'agent_name': order.agent1_partner_id.name if order and order.agent1_partner_id else False,
            'customer_name': self.partner_id.name,
            'invoice_date': self.invoice_date,
        }
    
    def action_resend_agent_email(self):
        """Manual action to resend agent notification email."""
        for move in self:
            if move.move_type == 'out_invoice' and move.state == 'posted':
                sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
                
                for order in sale_orders:
                    if order.agent1_partner_id and order.agent1_partner_id.email:
                        try:
                            # Get email template with ID 53
                            email_template = self.env['mail.template'].browse(53)
                            
                            if email_template and email_template.exists():
                                # Prepare template context
                                template_context = move._get_invoice_agent_email_context()
                                
                                # Send email to agent1_partner
                                email_template.with_context(**template_context).send_mail(
                                    move.id,
                                    force_send=True,
                                    email_values={
                                        'email_to': order.agent1_partner_id.email,
                                        'recipient_ids': [(4, order.agent1_partner_id.id)]
                                    }
                                )
                                
                                # Update tracking field
                                order.agent_email_sent = True
                                
                                # Log the action
                                move.message_post(
                                    body=_("Agent notification email manually resent to: %s (%s)") % (
                                        order.agent1_partner_id.name, 
                                        order.agent1_partner_id.email
                                    ),
                                    subject=_("Agent Invoice Notification Resent")
                                )
                                
                                return {
                                    'type': 'ir.actions.client',
                                    'tag': 'display_notification',
                                    'params': {
                                        'message': _("Email sent successfully to %s") % order.agent1_partner_id.name,
                                        'type': 'success',
                                        'sticky': False,
                                    }
                                }
                            else:
                                return {
                                    'type': 'ir.actions.client',
                                    'tag': 'display_notification',
                                    'params': {
                                        'message': _("Email template with ID 53 not found"),
                                        'type': 'warning',
                                        'sticky': False,
                                    }
                                }
                                
                        except Exception as e:
                            _logger.error(f"Failed to resend agent email: {str(e)}")
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'message': _("Failed to send email: %s") % str(e),
                                    'type': 'danger',
                                    'sticky': True,
                                }
                            }

    def _get_invoice_agent_email_context(self):
        """Get context variables for agent email template."""
        self.ensure_one()
        sale_orders = self.invoice_line_ids.mapped('sale_line_ids.order_id')
        
        context = {}
        if sale_orders:
            order = sale_orders[0]  # Take first order if multiple
            context.update({
                'agent_name': order.agent1_partner_id.name if order.agent1_partner_id else '',
                'agent_email': order.agent1_partner_id.email if order.agent1_partner_id else '',
                'order_name': order.name,
                'order_amount': order.amount_total,
                'invoice_number': self.name,
                'invoice_amount': self.amount_total,
                'customer_name': self.partner_id.name,
                'invoice_date': self.invoice_date,
                'commission_amount': order.agent1_amount if hasattr(order, 'agent1_amount') else 0.0,
            })
        
        return context
