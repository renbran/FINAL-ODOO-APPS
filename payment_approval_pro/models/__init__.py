# -*- coding: utf-8 -*-
# Payment Approval Pro Models

import logging
from odoo import api, fields, models

from . import payment_voucher
from . import payment_workflow

_logger = logging.getLogger(__name__)
