/** @odoo-module **/

/**
 * Field Mapping and Validation for Dashboard
 * 
 * This module ensures the dashboard can work with the actual fields
 * from your Odoo instance based on the provided field export.
 * 
 * @version 2.0.0
 * @since Odoo 17.0.0.2.0
 */

// Field mapping based on actual fields from the instance
var fieldMapping = {
    // Date fields - prefer booking_date from osus_invoice_report if available
    booking_date: 'booking_date', // osus_invoice_report.field_sale_order__booking_date
    date_order: 'date_order',     // sale.field_sale_order__date_order
    
    // Amount fields - prefer sale_value from osus_invoice_report if available  
    sale_value: 'sale_value',     // osus_invoice_report.field_sale_order__sale_value
    amount_total: 'amount_total', // sale.field_sale_order__amount_total
    amount_untaxed: 'amount_untaxed', // sale.field_sale_order__amount_untaxed
    
    // Commission fields from commission_ax module
    total_commission_amount: 'total_commission_amount',
    total_external_commission_amount: 'total_external_commission_amount', 
    total_internal_commission_amount: 'total_internal_commission_amount',
    
    // Agent and broker fields from commission_ax
    agent1_partner_id: 'agent1_partner_id',
    agent1_amount: 'agent1_amount',
    agent1_commission_type: 'agent1_commission_type',
    agent1_rate: 'agent1_rate',
    
    broker_partner_id: 'broker_partner_id',
    broker_amount: 'broker_amount',
    broker_commission_type: 'broker_commission_type',
    broker_rate: 'broker_rate',
    
    // Sales type from le_sale_type module
    sale_order_type_id: 'sale_order_type_id', // le_sale_type.field_sale_order__sale_order_type_id
    
    // Custom fields
    deal_id: 'deal_id',           // osus_invoice_report.field_sale_order__deal_id
    buyer_id: 'buyer_id',         // osus_invoice_report.field_sale_order__buyer_id
    project_id: 'project_id',     // osus_invoice_report.field_sale_order__project_id
    unit_id: 'unit_id',           // osus_invoice_report.field_sale_order__unit_id
    
    // Standard fields
    partner_id: 'partner_id',
    user_id: 'user_id',
    state: 'state',
    
    // Track which fields are available
    _available: {}
};

/**
 * Initialize field mapping based on available fields
 * @param {Object} orm - The ORM service
 * @returns {Promise} - Resolves when mapping is initialized
 */
async function initFieldMapping(orm) {
    if (!orm) {
        console.error('ORM service not available for field mapping');
        return fieldMapping;
    }
    
    try {
        // Check which fields exist in sale.order model
        const fieldsToCheck = [
            'booking_date', 'sale_value', 'date_order', 'amount_total', 'amount_untaxed',
            'sale_order_type_id', 'deal_id', 'buyer_id', 'project_id', 'unit_id',
            'total_commission_amount', 'total_external_commission_amount', 'total_internal_commission_amount'
        ];
        
        const fields = await orm.call(
            'sale.order', 
            'fields_get', 
            [fieldsToCheck]
        );
        
        // Update available fields
        fieldsToCheck.forEach(field => {
            fieldMapping._available[field] = !!fields[field];
        });
        
        // Log available fields
        console.log('Dashboard field availability:', fieldMapping._available);
        
        // Set preferred date field
        if (fieldMapping._available.booking_date) {
            console.log('Using booking_date from osus_invoice_report module');
        } else {
            console.warn('booking_date field not found, using date_order as fallback');
            fieldMapping.booking_date = 'date_order';
        }
        
        // Set preferred amount field
        if (fieldMapping._available.sale_value) {
            console.log('Using sale_value from osus_invoice_report module');
        } else {
            console.warn('sale_value field not found, using amount_total as fallback');
            fieldMapping.sale_value = 'amount_total';
        }
        
        // Check sale_order_type_id from le_sale_type module
        if (fieldMapping._available.sale_order_type_id) {
            console.log('sale_order_type_id field found from le_sale_type module');
        } else {
            console.warn('sale_order_type_id field not found, le_sale_type module may not be installed');
        }
        
        return fieldMapping;
    } catch (error) {
        console.error('Error initializing field mapping:', error);
        return fieldMapping;
    }
}

/**
 * Get the appropriate field name to use in a query
 * @param {string} fieldName - The logical field name
 * @returns {string} - The actual field name to use
 */
function getFieldName(fieldName) {
    return fieldMapping[fieldName] || fieldName;
}

/**
 * Build a domain for date range filtering using the appropriate date field
 * @param {string} startDate - The start date (YYYY-MM-DD)
 * @param {string} endDate - The end date (YYYY-MM-DD)
 * @returns {Array} - The domain array for filtering
 */
function buildDateDomain(startDate, endDate) {
    const dateField = getFieldName('booking_date');
    return [
        [dateField, '>=', startDate],
        [dateField, '<=', endDate]
    ];
}

/**
 * Build a domain for sale type filtering
 * @param {integer} saleTypeId - The sale type ID to filter by
 * @returns {Array} - The domain array for filtering
 */
function buildSaleTypeDomain(saleTypeId) {
    if (saleTypeId && fieldMapping._available.sale_order_type_id) {
        return [['sale_order_type_id', '=', saleTypeId]];
    }
    // If sale_order_type_id is not available, return empty domain
    if (saleTypeId && !fieldMapping._available.sale_order_type_id) {
        console.warn('sale_order_type_id field not available, le_sale_type module may not be installed');
    }
    return [];
}

/**
 * Build a field list for amount calculations
 * @returns {Array} - Field list to include in queries
 */
function getAmountFields() {
    const fields = ['amount_total'];
    
    if (fieldMapping._available.sale_value) {
        fields.push('sale_value');
    }
    if (fieldMapping._available.amount_untaxed) {
        fields.push('amount_untaxed');
    }
    if (fieldMapping._available.total_commission_amount) {
        fields.push('total_commission_amount');
    }
    
    return fields;
}

/**
 * Check if a field is available in the current instance
 * @param {string} fieldName - The field name to check
 * @returns {boolean} - True if the field is available
 */
function isFieldAvailable(fieldName) {
    return !!fieldMapping._available[fieldName];
}

// Export the functions
export {
    initFieldMapping,
    getFieldName,
    buildDateDomain,
    buildSaleTypeDomain,
    getAmountFields,
    isFieldAvailable
};
