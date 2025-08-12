# Copyright 2025 Spearhead - Ricardo Jara
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ["account.payment", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["in_process", "paid"]
    _cancel_state = "canceled"

    _tier_validation_manual_config = False

    # Add missing field that was referenced in view but not defined
    authorized_approvers_display = fields.Char(
        string="Authorized Approvers",
        compute="_compute_authorized_approvers_display",
        help="Display of authorized approvers for this payment"
    )

    def _compute_authorized_approvers_display(self):
        """Compute display of authorized approvers based on reviewers."""
        for payment in self:
            if payment.reviewer_ids:
                approvers = payment.reviewer_ids.mapped('name')
                payment.authorized_approvers_display = ', '.join(approvers)
            else:
                payment.authorized_approvers_display = ''
