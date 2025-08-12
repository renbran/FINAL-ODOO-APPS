from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Add missing field that was referenced in view but not defined
    journal_restrict_mode = fields.Selection(
        selection=[
            ('none', 'No Restriction'),
            ('restrict', 'Restricted'),
            ('strict', 'Strict Mode'),
        ],
        string="Journal Restriction Mode",
        default='none',
        help="Controls journal access restrictions for this move"
    )
