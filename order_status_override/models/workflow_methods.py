    # ============================================================================
    # NEW WORKFLOW ACTION METHODS - Updated per Requirements
    # ============================================================================
    
    def action_move_to_document_review(self):
        """Move order from Draft to Document Review"""
        self.ensure_one()
        if self.order_status != 'draft':
            raise UserError(_("Order must be in Draft status to move to Document Review."))
        
        self.order_status = 'document_review'
        self._send_workflow_notification('document_review')
        self.message_post(
            body=_("Order moved to Document Review stage by %s") % self.env.user.name,
            subject=_("Status Changed: Document Review")
        )
        return True
    
    def action_move_to_allocation(self):
        """Move order from Document Review to Allocation"""
        self.ensure_one()
        if self.order_status != 'document_review':
            raise UserError(_("Order must be in Document Review status to move to Allocation."))
        
        self.order_status = 'allocation'
        self._send_workflow_notification('allocation')
        self.message_post(
            body=_("Order moved to Allocation stage by %s") % self.env.user.name,
            subject=_("Status Changed: Allocation")
        )
        return True
    
    def action_approve_order(self):
        """Move order from Allocation to Approved"""
        self.ensure_one()
        if self.order_status != 'allocation':
            raise UserError(_("Order must be in Allocation status to approve."))
        
        self.order_status = 'approved'
        self._send_workflow_notification('approved')
        self.message_post(
            body=_("Order approved by %s") % self.env.user.name,
            subject=_("Status Changed: Approved")
        )
        return True
    
    def action_post_order(self):
        """Move order from Approved to Post and confirm as Sales Order"""
        self.ensure_one()
        if self.order_status != 'approved':
            raise UserError(_("Order must be in Approved status to post."))
        
        # Post the order (confirm as sales order)
        self.order_status = 'post'
        
        # Confirm the sales order if not already confirmed
        if self.state in ['draft', 'sent']:
            self.action_confirm()
        
        self.message_post(
            body=_("Order posted and confirmed as Sales Order by %s") % self.env.user.name,
            subject=_("Status Changed: Posted")
        )
        return True
    
    def action_reject_order(self):
        """Reject the order and return to draft"""
        self.ensure_one()
        if self.order_status == 'post':
            raise UserError(_("Cannot reject a posted order."))
        
        self.order_status = 'draft'
        self.message_post(
            body=_("Order rejected by %s and returned to draft status for revision.") % self.env.user.name,
            subject=_("Order Rejected"),
            message_type='notification'
        )
        return True
