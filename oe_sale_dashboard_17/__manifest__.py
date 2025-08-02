{
    'name': 'OSUS Executive Sales Dashboard - Production Ready',
    'version': '17.0.2.0.0',
    'category': 'Sales',
    'summary': 'Production-ready executive sales dashboard with enhanced analytics and agent1+partner integration.',
    'description': """
        Production-Ready Executive Sales Dashboard
        
        🚀 **Enhanced Features:**
        - **Agent1+Partner Integration**: Uses commission_ax module's agent1_partner_id and agent1_amount fields
        - **Robust Error Handling**: Comprehensive fallback mechanisms and defensive programming
        - **Field Compatibility**: Auto-detection of booking_date, sale_value, and commission fields
        - **Chart.js Integration**: Modern charts with fallback CDN loading
        - **Responsive Design**: Mobile-first approach with adaptive layouts
        - **Real-time Analytics**: Performance metrics with conversion rates and deal insights
        
        📊 **Core Analytics:**
        - **Executive KPIs**: Total quotations, sales orders, invoiced amounts with conversion tracking
        - **Agent Rankings**: Top performing agents based on agent1_partner_id commission data
        - **Agency Performance**: Broker rankings using broker_partner_id and broker_amount
        - **Sales Trends**: Line charts showing revenue progression over time
        - **Category Distribution**: Pie charts with sales type breakdowns
        - **Recent Activity**: Latest orders with status tracking
        
        🔧 **Technical Excellence:**
        - **Production-Ready**: Comprehensive error handling and graceful degradation
        - **Odoo 17 Compliance**: Modern OWL components with proper backend integration
        - **Commission Integration**: Full support for commission_ax module fields
        - **Performance Optimized**: Efficient data loading and chart rendering
        - **Browser Compatible**: Cross-browser support with fallbacks
        
        Transform your sales data into actionable business insights with this comprehensive
        dashboard that leverages agent commission data for accurate performance tracking.
    """,
    'author': 'RENBRAN - Production Enhanced',
    'website': 'WWW.TACHIMAO.COM',
    'depends': ['web', 'sale_management', 'le_sale_type'],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_helpers'),
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js',
            'oe_sale_dashboard_17/static/src/scss/dashboard.scss',
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
        'web.qunit_suite_tests': [
            'oe_sale_dashboard_17/static/tests/**/*.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'price': 0.0,
    'currency': 'USD',
    'support': 'WWW.TACHIMAO.COM',
}
