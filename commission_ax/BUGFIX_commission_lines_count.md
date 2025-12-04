# Bug Fix: Missing Field `commission_lines_count`

## Issue
**Error Type**: RPC_ERROR  
**Module**: commission_ax  
**File**: views/sale_order.xml  
**Date Fixed**: December 4, 2025

### Error Message
```
Field `commission_lines_count` does not exist

View error context:
{'file': '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views/sale_order.xml',
 'line': 1,
 'name': 'sale.order.form.inherit.commission.enhanced',
 'view': ir.ui.view(7006,),
 'view.model': 'sale.order',
 'view.parent': ir.ui.view(2118,),
 'xmlid': 'view_order_form_inherit_commission_enhanced'}
```

## Root Cause
The `commission_lines_count` field was being referenced by Odoo's view rendering system but was not defined in the `sale.order` model within the `commission_ax` module. This is a CloudPepper compatibility issue where certain fields are expected to exist for proper rendering.

## Solution
Added the missing field and compute method to `commission_ax/models/sale_order.py`:

### 1. Field Definition
```python
# Commission lines count for compatibility
commission_lines_count = fields.Integer(
    string="Commission Partners Count",
    compute="_compute_commission_lines_count",
    help="Number of commission partners configured for this order"
)
```

### 2. Compute Method
```python
@api.depends(
    'broker_partner_id', 'broker_amount',
    'referrer_partner_id', 'referrer_amount',
    'cashback_partner_id', 'cashback_amount',
    'other_external_partner_id', 'other_external_amount',
    'agent1_partner_id', 'agent1_amount',
    'agent2_partner_id', 'agent2_amount',
    'manager_partner_id', 'manager_amount',
    'director_partner_id', 'director_amount',
    'consultant_id', 'salesperson_commission',
    'manager_id', 'manager_commission',
    'second_agent_id', 'second_agent_commission',
    'director_id', 'director_commission'
)
def _compute_commission_lines_count(self):
    """Compute the number of active commission partners."""
    for order in self:
        count = 0
        # Count external commission partners
        if order.broker_partner_id and order.broker_amount:
            count += 1
        if order.referrer_partner_id and order.referrer_amount:
            count += 1
        if order.cashback_partner_id and order.cashback_amount:
            count += 1
        if order.other_external_partner_id and order.other_external_amount:
            count += 1
        # Count internal commission partners
        if order.agent1_partner_id and order.agent1_amount:
            count += 1
        if order.agent2_partner_id and order.agent2_amount:
            count += 1
        if order.manager_partner_id and order.manager_amount:
            count += 1
        if order.director_partner_id and order.director_amount:
            count += 1
        # Count legacy commission partners
        if order.consultant_id and order.salesperson_commission:
            count += 1
        if order.manager_id and order.manager_commission:
            count += 1
        if order.second_agent_id and order.second_agent_commission:
            count += 1
        if order.director_id and order.director_commission:
            count += 1
        order.commission_lines_count = count
```

## Features
The `commission_lines_count` field:
- **Automatically computes** the number of active commission partners
- **Considers all types**: External (Broker, Referrer, Cashback, Other) and Internal (Agent 1, Agent 2, Manager, Director)
- **Includes legacy partners**: Consultant, Legacy Manager, Second Agent, Legacy Director
- **Only counts active commissions**: Partners with actual commission amounts
- **Updates automatically**: Recomputes when any partner or amount changes

## Testing
After deployment, verify:
1. Navigate to Sales → Orders → Any order with commissions
2. The view should load without RPC errors
3. The commission_lines_count should accurately reflect the number of configured commission partners
4. Changing commission partners/amounts should update the count

## Deployment Instructions
```bash
# SSH to CloudPepper server
ssh user@cloudpepper.site

# Navigate to module directory
cd /var/odoo/osusproperties/extra-addons/commission_ax

# Update module
odoo -u commission_ax --stop-after-init

# Restart Odoo service
sudo systemctl restart odoo

# Monitor logs
tail -f /var/log/odoo/odoo.log
```

## Related Files Modified
- `commission_ax/models/sale_order.py` (Added field and compute method)

## Impact
- **Severity**: Critical (blocking module upgrade)
- **Affected Users**: All users accessing Sale Orders with commission_ax module
- **Resolution Time**: Immediate upon deployment
- **Data Migration**: None required (computed field)

## Prevention
This issue highlights the importance of:
1. Ensuring all fields referenced in views exist in models
2. Running validation scripts before deployment
3. Testing module upgrades in staging environment
4. Maintaining CloudPepper compatibility layers

## Status
✅ **RESOLVED** - Field added with proper compute logic and dependencies
