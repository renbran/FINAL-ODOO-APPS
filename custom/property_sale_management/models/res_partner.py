from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    blacklisted = fields.Boolean(
        string='Blacklisted',
        default=False,
        tracking=True,
        help="Mark partner as blacklisted for business transactions"
    )
    blacklist_date = fields.Date(
        string='Blacklist Date',
        readonly=True,
        tracking=True,
        help="Date when the partner was blacklisted"
    )
    blacklist_reason = fields.Text(
        string='Blacklist Reason',
        tracking=True,
        help="Detailed reason for blacklisting the partner"
    )

    @api.constrains('blacklisted', 'blacklist_reason')
    def _check_blacklist_reason(self):
        for record in self:
            if record.blacklisted and not record.blacklist_reason:
                raise ValidationError(_("Blacklist reason is required when blacklisting a partner"))

    def action_add_blacklist(self):
        self.ensure_one()
        return self.write({
            'blacklisted': True,
            'blacklist_date': fields.Date.context_today(self),
            'blacklist_reason': self.blacklist_reason or _("Blacklisted by system")
        })

    def action_remove_blacklist(self):
        self.ensure_one()
        return self.write({
            'blacklisted': False,
            'blacklist_date': None,
            'blacklist_reason': None
        })