# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Activate me back when modules are migrated

    module_base_tier_validation_formula = fields.Boolean(string="Tier Formula")

    # Add missing field that was referenced in view but not defined
    payment_approval = fields.Boolean(
        string="Payment Approval",
        help="Enable payment approval workflow"
    )
