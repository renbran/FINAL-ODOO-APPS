# -*- coding: utf-8 -*-
# Payment Approval Pro Models

import logging
from odoo import api, fields, models

from . import payment_voucher
from . import payment_workflow
from . import account_payment_extension
from . import payment_report_wizard

_logger = logging.getLogger(__name__)
