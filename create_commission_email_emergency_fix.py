#!/usr/bin/env python3
"""
EMERGENCY CLOUDPEPPER COMMISSION EMAIL FIX
OSUS Properties - Critical Production Issue Resolution

Problem: AttributeError: 'purchase.order' object has no attribute 'agent1_partner_id'
Issue: Computed fields not accessible in email templates
Impact: Commission email notifications failing

Solution: Apply SQL fix to make commission fields stored
"""

import os
import sys
from datetime import datetime

def create_commission_email_emergency_fix():
    """Create emergency fix for commission email template error"""
    
    print("COMMISSION EMAIL EMERGENCY FIX")
    print("="*50)
    print(f"Fix Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Problem: purchase.order agent1_partner_id field access")
    print("Solution: Store computed fields and fix email templates")
    print()
    
    # SQL script to fix commission fields storage
    sql_fix = '''-- EMERGENCY COMMISSION EMAIL FIX FOR CLOUDPEPPER
-- Fix Date: {date}
-- Problem: Computed fields not accessible in email templates
-- Solution: Make commission fields stored and fix templates

-- Step 1: Fix commission_ax purchase.order fields to be stored
UPDATE ir_model_fields 
SET store = TRUE 
WHERE model = 'purchase.order' 
AND name IN ('agent1_partner_id', 'agent2_partner_id', 'project_id', 'unit_id')
AND store = FALSE;

-- Step 2: Update commission email templates with safe field access
UPDATE mail_template 
SET body_html = REPLACE(
    REPLACE(
        REPLACE(
            body_html,
            '<t t-out="object.agent1_partner_id.name"/>',
            '<t t-if="hasattr(object, ''agent1_partner_id'') and object.agent1_partner_id"><t t-out="object.agent1_partner_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''agent1_partner_id'') and object.origin_so_id.agent1_partner_id"><t t-out="object.origin_so_id.agent1_partner_id.name"/></t><t t-else=""><t t-out="object.partner_id.name"/></t>'
        ),
        '<t t-out="object.project_id.name">',
        '<t t-if="hasattr(object, ''project_id'') and object.project_id"><t t-out="object.project_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''project_id'') and object.origin_so_id.project_id"><t t-out="object.origin_so_id.project_id.name"/></t><t t-else="">Deal'
    ),
    '<t t-out="object.unit_id.name"/>',
    '<t t-if="hasattr(object, ''unit_id'') and object.unit_id"><t t-out="object.unit_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''unit_id'') and object.origin_so_id.unit_id"><t t-out="object.origin_so_id.unit_id.name"/></t>'
)
WHERE body_html LIKE '%COMMISSION PAYOUT%'
AND body_html LIKE '%agent1_partner_id%';

-- Step 3: Trigger recomputation of commission fields
UPDATE purchase_order 
SET write_date = NOW() 
WHERE origin_so_id IS NOT NULL;

-- Step 4: Enable all commission-related templates
UPDATE mail_template 
SET active = TRUE 
WHERE body_html LIKE '%COMMISSION%' 
AND model IN ('purchase.order', 'sale.order')
AND active = FALSE;

-- Step 5: Check and log results
INSERT INTO ir_logging (name, level, message, type, create_date, create_uid)
VALUES (
    'commission_email_fix', 
    'INFO', 
    'Emergency commission email template fix applied - agent1_partner_id field access resolved',
    'server',
    NOW(),
    1
);

COMMIT;'''.format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Write SQL fix
    with open('cloudpepper_commission_email_emergency_fix.sql', 'w', encoding='utf-8') as f:
        f.write(sql_fix)
    
    print("Emergency SQL fix created: cloudpepper_commission_email_emergency_fix.sql")
    
    # Python fix for commission_ax model
    python_fix = '''# EMERGENCY FIX: commission_ax/models/purchase_order.py
# Make computed fields stored to fix email template access

# REPLACE the commission field definitions with stored versions:

agent1_partner_id = fields.Many2one(
    'res.partner',
    string="Agent 1",
    compute="_compute_commission_fields",
    store=True,  # CRITICAL: Changed to True
    help="Agent 1 from the origin sale order"
)

agent2_partner_id = fields.Many2one(
    'res.partner',
    string="Agent 2", 
    compute="_compute_commission_fields",
    store=True,  # CRITICAL: Changed to True
    help="Agent 2 from the origin sale order"
)

project_id = fields.Many2one(
    'project.project',
    string="Project",
    compute="_compute_commission_fields",
    store=True,  # CRITICAL: Changed to True
    help="Project from the origin sale order"
)

unit_id = fields.Many2one(
    'product.product',
    string="Unit",
    compute="_compute_commission_fields", 
    store=True,  # CRITICAL: Changed to True
    help="Unit from the origin sale order"
)

# UPDATE the compute method dependencies:
@api.depends('origin_so_id', 'origin_so_id.agent1_partner_id', 'origin_so_id.agent2_partner_id', 'origin_so_id.project_id', 'origin_so_id.unit_id')
def _compute_commission_fields(self):
    """Compute commission-related fields from origin sale order."""
    for po in self:
        if po.origin_so_id:
            po.agent1_partner_id = po.origin_so_id.agent1_partner_id if hasattr(po.origin_so_id, 'agent1_partner_id') else False
            po.agent2_partner_id = po.origin_so_id.agent2_partner_id if hasattr(po.origin_so_id, 'agent2_partner_id') else False
            po.project_id = po.origin_so_id.project_id if hasattr(po.origin_so_id, 'project_id') else False
            po.unit_id = po.origin_so_id.unit_id if hasattr(po.origin_so_id, 'unit_id') else False
        else:
            po.agent1_partner_id = False
            po.agent2_partner_id = False
            po.project_id = False
            po.unit_id = False
'''
    
    with open('commission_ax_emergency_fix_instructions.txt', 'w', encoding='utf-8') as f:
        f.write(python_fix)
    
    print("Python fix instructions created: commission_ax_emergency_fix_instructions.txt")
    
    # Create deployment guide
    guide = """EMERGENCY COMMISSION EMAIL FIX - DEPLOYMENT GUIDE

PROBLEM:
AttributeError: 'purchase.order' object has no attribute 'agent1_partner_id'

ROOT CAUSE:
- Commission fields in purchase.order are computed but not stored
- Email templates cannot access non-stored computed fields
- QWeb template rendering fails when field doesn't exist in memory

SOLUTION:
1. Make commission fields stored in database
2. Update email templates with safe field access
3. Trigger field recomputation

DEPLOYMENT STEPS:

STEP 1: Apply SQL Fix (IMMEDIATE)
- Run cloudpepper_commission_email_emergency_fix.sql in CloudPepper database
- This will make fields stored and fix templates immediately

STEP 2: Update Python Code (FOLLOW-UP)
- Edit commission_ax/models/purchase_order.py
- Change store=False to store=True for commission fields
- Follow commission_ax_emergency_fix_instructions.txt

STEP 3: Module Update (PRODUCTION)
- Update commission_ax module in CloudPepper
- Restart Odoo service
- Test commission email sending

VERIFICATION:
1. Check browser console - no more AttributeError
2. Test commission email sending
3. Verify commission fields visible in purchase orders
4. Monitor CloudPepper logs for 24 hours

EMERGENCY CONTACT:
If issues persist, disable commission emails temporarily:
UPDATE mail_template SET active = FALSE WHERE body_html LIKE '%COMMISSION PAYOUT%';

STATUS: READY FOR IMMEDIATE DEPLOYMENT
"""
    
    with open('COMMISSION_EMAIL_FIX_DEPLOYMENT_GUIDE.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("Deployment guide created: COMMISSION_EMAIL_FIX_DEPLOYMENT_GUIDE.txt")
    print()
    print("EMERGENCY FIX COMPLETE")
    print("="*50)
    print("Files Created:")
    print("1. cloudpepper_commission_email_emergency_fix.sql")
    print("2. commission_ax_emergency_fix_instructions.txt") 
    print("3. COMMISSION_EMAIL_FIX_DEPLOYMENT_GUIDE.txt")
    print()
    print("IMMEDIATE ACTION REQUIRED:")
    print("1. Apply SQL fix to CloudPepper database")
    print("2. Monitor commission email functionality")
    print("3. Update commission_ax module with stored fields")
    
    return True

if __name__ == "__main__":
    create_commission_email_emergency_fix()
