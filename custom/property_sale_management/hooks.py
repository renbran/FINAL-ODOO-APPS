from odoo import api, SUPERUSER_ID

def _post_install_initialize(cr, registry):
    """
    Post-installation initialization logic for the property_sale_management module.
    This runs after the module is installed.
    
    :param cr: Cursor
    :param registry: Registry
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Only run this if we're in a new database installation
    if not env['property.type'].search_count([]):
        _create_property_types(env)
    
    if not env['property.status'].search_count([]):
        _create_property_statuses(env)
    
    if not env['commission.structure'].search_count([]):
        _create_commission_structures(env)
    
    # Set up default configuration parameters
    _configure_default_settings(env)
    
    # Create property tags
    _create_property_tags(env)
    
    # Create account analytic tags for property sales if accounting is installed
    if env['ir.module.module'].search([('name', '=', 'account'), ('state', '=', 'installed')]):
        _create_accounting_configuration(env)


def _create_property_types(env):
    """Create default property types"""
    property_types = [
        {'name': 'Apartment', 'code': 'APT', 'sequence': 10},
        {'name': 'Villa', 'code': 'VIL', 'sequence': 20},
        {'name': 'Townhouse', 'code': 'TWH', 'sequence': 30},
        {'name': 'Penthouse', 'code': 'PEN', 'sequence': 40},
        {'name': 'Office', 'code': 'OFF', 'sequence': 50},
        {'name': 'Retail', 'code': 'RET', 'sequence': 60},
        {'name': 'Land', 'code': 'LND', 'sequence': 70},
    ]
    for prop_type in property_types:
        env['property.type'].create(prop_type)


def _create_property_statuses(env):
    """Create default property statuses"""
    statuses = [
        {'name': 'Available', 'code': 'AVL', 'sequence': 10, 'is_active': True},
        {'name': 'Reserved', 'code': 'RSV', 'sequence': 20, 'is_active': True},
        {'name': 'Under Contract', 'code': 'UND', 'sequence': 30, 'is_active': True},
        {'name': 'Sold', 'code': 'SLD', 'sequence': 40, 'is_active': False},
        {'name': 'Off Market', 'code': 'OFF', 'sequence': 50, 'is_active': False},
    ]
    for status in statuses:
        env['property.status'].create(status)


def _create_commission_structures(env):
    """Create default commission structures"""
    structures = [
        {
            'name': 'Standard Sales',
            'code': 'STD',
            'internal_rate': 2.0,
            'broker_rate': 1.0,
            'description': 'Standard commission rates for all regular sales'
        },
        {
            'name': 'Premium Properties',
            'code': 'PRM',
            'internal_rate': 2.5,
            'broker_rate': 1.5,
            'description': 'Higher rates for luxury and high-value properties'
        },
        {
            'name': 'Developer Direct',
            'code': 'DEV',
            'internal_rate': 3.0,
            'broker_rate': 2.0,
            'description': 'Special rates when selling directly for developers'
        },
    ]
    for structure in structures:
        env['commission.structure'].create(structure)


def _create_property_tags(env):
    """Create common property tags"""
    tags = [
        {'name': 'Beachfront', 'color': 1},  # Red
        {'name': 'City View', 'color': 2},   # Orange
        {'name': 'Furnished', 'color': 3},   # Yellow
        {'name': 'Pet-Friendly', 'color': 4}, # Green
        {'name': 'Investment', 'color': 5},  # Blue
        {'name': 'New Development', 'color': 6}, # Purple
        {'name': 'Exclusive', 'color': 7},   # Turquoise
        {'name': 'Distressed Sale', 'color': 8}, # Pink
    ]
    for tag in tags:
        env['property.tag'].create(tag)


def _configure_default_settings(env):
    """Set up default configuration parameters"""
    # Create configuration parameters
    IrConfig = env['ir.config_parameter'].sudo()
    
    # Default currency for property valuations if not set
    if not IrConfig.get_param('property_sale_management.default_currency_id'):
        company_currency = env.company.currency_id
        IrConfig.set_param('property_sale_management.default_currency_id', company_currency.id)
    
    # Default payment terms
    if not IrConfig.get_param('property_sale_management.default_payment_term_id'):
        payment_term = env['account.payment.term'].search([('name', 'ilike', '30 days')], limit=1)
        if payment_term:
            IrConfig.set_param('property_sale_management.default_payment_term_id', payment_term.id)
    
    # Auto-generate property codes
    IrConfig.set_param('property_sale_management.auto_property_code', True)
    
    # Default commission calculation method (percentage or fixed)
    IrConfig.set_param('property_sale_management.commission_calculation', 'percentage')


def _create_accounting_configuration(env):
    """Set up accounting configuration for property sales"""
    # Create analytic tags for property transactions
    AnalyticTag = env['account.analytic.tag']
    
    tags = [
        {'name': 'Property Sale', 'color': 4},  # Green
        {'name': 'Internal Commission', 'color': 1},  # Red
        {'name': 'Broker Commission', 'color': 5},  # Blue
    ]
    
    for tag in tags:
        if not AnalyticTag.search([('name', '=', tag['name'])]):
            AnalyticTag.create(tag)
    
    # Link default income account to property sales if journal items exist
    company = env.company
    if company.property_account_income_categ_id:
        IrConfig = env['ir.config_parameter'].sudo()
        IrConfig.set_param('property_sale_management.default_income_account_id', 
                          company.property_account_income_categ_id.id)