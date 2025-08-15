{
    'name': 'OSUS Enhanced Sales Order Workflow',
    'version': '17.0.2.0.0',
    'summary': 'Enterprise Sales Order Workflow with Commission Integration',
    'description': '''
        OSUS Enhanced Sales Order Workflow Management System
        
        Core Workflow: Draft -> Documentation -> Commission Calculation -> Approved -> Post
        
        Key Features:
        - Modern UI/UX with OSUS branding (#800020, white, gold)
        - Seamless integration with commission_ax for commission calculations
        - Mobile-responsive design for desktop and mobile users
        - Advanced workflow automation with proper access controls
        - Real-time deal summaries and commission tracking
        - Digital signatures and approval workflows
        - Comprehensive audit trails and notifications
        - Performance-optimized status transitions
        
        Technical Excellence:
        - Enterprise-grade error handling and logging
        - Scalable architecture with proper inheritance
        - RESTful API endpoints for external integrations
        - Advanced reporting and analytics
        - Multi-user collaboration features
        
        Transform your sales process with this professional, scalable solution
        designed for modern business workflows.
    ''',
    'category': 'Sales/Workflow',
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': ['sale', 'mail', 'commission_ax', 'account', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/order_status_data.xml',
        'data/email_templates.xml',
        'views/assets.xml',
        'views/order_status_views.xml',
        'views/order_views_enhanced.xml',
        'views/commission_integration_views.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'order_status_override/static/src/scss/osus_branding.scss',
            'order_status_override/static/src/scss/workflow_components.scss',
            'order_status_override/static/src/scss/mobile_responsive.scss',
            'order_status_override/static/src/js/workflow_manager.js',
            'order_status_override/static/src/js/commission_calculator.js',
            'order_status_override/static/src/js/status_dashboard.js',
        ],
        'web.assets_frontend': [
            'order_status_override/static/src/scss/frontend_portal.scss',
            'order_status_override/static/src/js/portal_workflow.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}