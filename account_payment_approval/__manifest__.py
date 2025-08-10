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
{
    'name': 'Enhanced Payment Voucher System - OSUS',
    'version': '17.0.2.0.0',
    'category': 'Accounting',
    'summary': """Advanced Payment and Receipt Voucher System with Digital Signatures, 
                  QR Verification, Multi-stage Approval Workflows, and OSUS Branding""",
    'description': """
    Enhanced Payment Voucher System for OSUS Real Estate
    
    Key Features:
    • 4-stage Payment Voucher workflow (Submit → Review → Approve → Authorize → Post)
    • 3-stage Receipt Voucher workflow (Submit → Review → Post) 
    • Digital signature capture for all workflow stages
    • QR code generation with secure verification portal
    • OSUS branded reports with professional styling
    • Email notifications and activity tracking
    • Multi-company support with role-based permissions
    • Mobile-responsive design and verification interface
    • Integration with invoices/bills workflow
    • Comprehensive audit trails and security
    """,
    'author': 'OSUS Properties - Enhanced by AI Assistant',
    'company': 'OSUS Properties',
    'maintainer': 'OSUS Properties',
    'website': "https://www.osusproperties.com",
    'depends': [
        'account', 
        'mail', 
        'web',
        'base'
    ],
    'external_dependencies': {
        'python': ['qrcode', 'PIL']
    },
    'data': [
        # Security
        'security/payment_voucher_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/voucher_sequence.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_items.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/receipt_voucher_report.xml',
        'reports/qr_verification_report.xml',
        'reports/report_actions.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}