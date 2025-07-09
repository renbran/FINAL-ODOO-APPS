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
from odoo import fields, models


class AccountMove(models.Model):
    """This class inherits "account.move" and add state for approval """
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('submit_review', 'Submit for Review'),
                       ('waiting_approval', 'Waiting For Approval'),
                       ('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'submit_review': 'set default', 'waiting_approval': 'set default', 'approved': 'set default',
                  'rejected': 'set default'}, help="States of approval.")

    def button_submit_review(self):
        """Set the state to 'submit_review'."""
        self.state = 'submit_review'

    def button_approve(self):
        """Set the state to 'approved'."""
        self.state = 'approved'

    def button_reject(self):
        """Set the state to 'rejected'."""
        self.state = 'rejected'

    def button_reset_to_draft(self):
        """Reset the state to 'draft'."""
        self.state = 'draft'
