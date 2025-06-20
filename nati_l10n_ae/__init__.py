# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, SUPERUSER_ID

def load_translations(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        template = env.ref('nati_l10n_ae.account_arabic_coa_general', raise_if_not_found=False)
        if template:
            template.process_coa_translations()
