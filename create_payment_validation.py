#!/usr/bin/env python3
"""
Payment Approval State Validation Script
Checks which payments need approval state migration
"""

import sys
import json

def create_validation_query():
    """Create SQL query to check payment states"""
    
    query = '''
-- Payment Approval State Validation Query
-- Run this query to see which payments need migration

SELECT 
    'NEEDS_MIGRATION' as category,
    state as payment_state,
    approval_state,
    COUNT(*) as count,
    STRING_AGG(name, ', ') as examples
FROM account_payment 
WHERE (
    (state = 'posted' AND approval_state != 'posted') OR
    (state = 'cancel' AND approval_state != 'cancelled') OR
    (state = 'draft' AND approval_state NOT IN ('draft', 'under_review'))
)
GROUP BY state, approval_state

UNION ALL

SELECT 
    'ALREADY_SYNCED' as category,
    state as payment_state,
    approval_state,
    COUNT(*) as count,
    '' as examples
FROM account_payment 
WHERE (
    (state = 'posted' AND approval_state = 'posted') OR
    (state = 'cancel' AND approval_state = 'cancelled') OR
    (state = 'draft' AND approval_state IN ('draft', 'under_review'))
)
GROUP BY state, approval_state

ORDER BY category, payment_state, approval_state;

-- Summary query
SELECT 
    CASE 
        WHEN (state = 'posted' AND approval_state = 'posted') OR
             (state = 'cancel' AND approval_state = 'cancelled') OR
             (state = 'draft' AND approval_state IN ('draft', 'under_review'))
        THEN 'SYNCED'
        ELSE 'NEEDS_MIGRATION'
    END as sync_status,
    COUNT(*) as count
FROM account_payment
GROUP BY sync_status;
'''
    
    with open('payment_state_validation.sql', 'w', encoding='utf-8') as f:
        f.write(query)
    
    print("✅ Created payment_state_validation.sql")

def create_python_validation():
    """Create Python validation script"""
    
    validation_script = '''#!/usr/bin/env python3
"""
Python Payment Validation Script
Run in Odoo shell to validate payment states
"""

from odoo import api, SUPERUSER_ID

def validate_payment_states(cr, registry):
    """Validate current payment approval states"""
    
    print("🔍 PAYMENT APPROVAL STATE VALIDATION")
    print("=" * 50)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get all payments
    all_payments = env['account.payment'].search([])
    
    # Categorize payments
    synced_payments = []
    needs_migration = []
    
    for payment in all_payments:
        if ((payment.state == 'posted' and payment.approval_state == 'posted') or
            (payment.state == 'cancel' and payment.approval_state == 'cancelled') or
            (payment.state == 'draft' and payment.approval_state in ['draft', 'under_review'])):
            synced_payments.append(payment)
        else:
            needs_migration.append({
                'payment': payment,
                'name': payment.name,
                'state': payment.state,
                'approval_state': payment.approval_state,
                'partner': payment.partner_id.name if payment.partner_id else 'N/A',
                'amount': payment.amount
            })
    
    print(f"📊 VALIDATION RESULTS:")
    print(f"   ✅ Already synced: {len(synced_payments)} payments")
    print(f"   ⚠️  Need migration: {len(needs_migration)} payments")
    
    if needs_migration:
        print(f"\\n🔍 PAYMENTS NEEDING MIGRATION:")
        print("-" * 80)
        print(f"{'Name':<20} {'State':<10} {'Approval':<15} {'Partner':<20} {'Amount':<10}")
        print("-" * 80)
        
        for item in needs_migration[:20]:  # Show first 20
            print(f"{item['name']:<20} {item['state']:<10} {item['approval_state']:<15} {item['partner']:<20} {item['amount']:<10}")
        
        if len(needs_migration) > 20:
            print(f"... and {len(needs_migration) - 20} more")
    
    # Group by state combinations
    state_combinations = {}
    for item in needs_migration:
        key = f"{item['state']} -> {item['approval_state']}"
        if key not in state_combinations:
            state_combinations[key] = 0
        state_combinations[key] += 1
    
    if state_combinations:
        print(f"\\n📈 STATE COMBINATION BREAKDOWN:")
        for combo, count in state_combinations.items():
            print(f"   {combo}: {count} payments")
    
    # Recommendations
    print(f"\\n💡 RECOMMENDATIONS:")
    if not needs_migration:
        print("   ✅ All payments are already in sync! No migration needed.")
    else:
        print("   🔧 Run migration script to sync approval states")
        print("   📋 Use one of the generated migration options:")
        print("      - manual_payment_update.py (for CloudPepper)")
        print("      - payment_approval_migration.py (for Odoo shell)")
        print("      - Auto-migration on module update")
    
    return len(needs_migration)

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print(">>> exec(open('payment_validation.py').read())")
    print(">>> validate_payment_states(cr, registry)")
'''
    
    with open('payment_validation.py', 'w', encoding='utf-8') as f:
        f.write(validation_script)
    
    print("✅ Created payment_validation.py")

def create_summary_report():
    """Create a summary of the migration process"""
    
    summary = '''# 📋 PAYMENT APPROVAL STATE MIGRATION SUMMARY

## 🎯 OBJECTIVE
Sync existing payment records so their `approval_state` matches their current `state`:
- If `state = 'posted'` → Set `approval_state = 'posted'`  
- If `state = 'cancel'` → Set `approval_state = 'cancelled'`
- If `state = 'draft'` → Set `approval_state = 'draft'`

## 📊 MIGRATION SCENARIOS

### Scenario 1: Posted Payments ✅
**Problem**: Payment is posted but approval_state is still 'draft', 'under_review', etc.
**Solution**: 
- Set `approval_state = 'posted'`
- Populate missing workflow users (reviewer_id, approver_id, authorizer_id)
- Set approval dates based on create_date/write_date

### Scenario 2: Cancelled Payments ❌
**Problem**: Payment is cancelled but approval_state is not 'cancelled'
**Solution**: Set `approval_state = 'cancelled'`

### Scenario 3: Draft Payments 📝
**Problem**: Payment is draft but approval_state is advanced state
**Solution**: Reset `approval_state = 'draft'`

## 🔧 AVAILABLE MIGRATION TOOLS

### 1. **Automatic Module Migration** (RECOMMENDED)
- **File**: `account_payment_final/migrations/17.0.1.1.0/post-migrate.py`
- **Trigger**: Runs automatically when module version changes from 17.0.1.0.0 → 17.0.1.1.0
- **Usage**: Simply update the module in CloudPepper
- **Best For**: Production deployment

### 2. **Manual Web Update** (CLOUDPEPPER)
- **File**: `manual_payment_update.py`
- **Usage**: Run from terminal or adapt for web interface
- **Benefits**: Works via XML-RPC, no shell access needed
- **Best For**: CloudPepper environment without shell access

### 3. **Odoo Shell Script** (DEVELOPMENT)
- **File**: `payment_approval_migration.py`
- **Usage**: Run in Odoo shell environment
- **Command**: `odoo shell -d database; exec(open('payment_approval_migration.py').read())`
- **Best For**: Development environment with shell access

### 4. **Direct SQL** (DATABASE)
- **File**: `payment_approval_migration.sql`
- **Usage**: Run directly on PostgreSQL database
- **Benefits**: Fastest execution, direct database access
- **Best For**: Database administrators

## 🚀 DEPLOYMENT STEPS FOR CLOUDPEPPER

### Step 1: Backup Database ⚠️
```sql
-- Create backup before migration
pg_dump your_database > payment_migration_backup.sql
```

### Step 2: Validate Current State 🔍
```python
# Run validation to see what needs migration
python payment_validation.py
```

### Step 3: Choose Migration Method 🔧
**Option A: Automatic (Recommended)**
1. Upload updated module with version 17.0.1.1.0
2. Go to Apps → account_payment_final → Update
3. Migration runs automatically

**Option B: Manual**
1. Run `python manual_payment_update.py`
2. Enter CloudPepper credentials
3. Confirm migration when prompted

### Step 4: Verify Results ✅
```sql
-- Check migration results
SELECT state, approval_state, COUNT(*) 
FROM account_payment 
GROUP BY state, approval_state;
```

## 📈 EXPECTED RESULTS

### Before Migration:
```
state   | approval_state | count
--------|----------------|-------
posted  | draft         | 25
posted  | under_review  | 8  
cancel  | draft         | 3
```

### After Migration:
```
state   | approval_state | count
--------|----------------|-------
posted  | posted        | 33
cancel  | cancelled     | 3
draft   | draft         | 45
```

## 🛡️ SAFETY MEASURES

1. **Backup Required**: Always backup before migration
2. **Validation**: Run validation script first
3. **Test Environment**: Test on staging before production
4. **Rollback Plan**: Keep backup for quick rollback
5. **User Permissions**: Migration preserves user permissions and security

## 📞 TROUBLESHOOTING

### Common Issues:
1. **Permission Error**: Ensure user has write access to account.payment
2. **Missing Users**: Migration handles missing workflow users gracefully
3. **Network Timeout**: Use SQL method for large datasets
4. **Validation Errors**: Check constrains in account_payment model

### Recovery:
If migration fails, restore from backup:
```sql
psql your_database < payment_migration_backup.sql
```

---
*Migration tools generated automatically - Test before production use*
'''
    
    with open('PAYMENT_MIGRATION_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ Created PAYMENT_MIGRATION_SUMMARY.md")

def main():
    """Create validation and summary files"""
    print("\n🔍 CREATING VALIDATION TOOLS...")
    print("=" * 50)
    
    create_validation_query()
    create_python_validation()
    create_summary_report()
    
    print("\n📋 VALIDATION TOOLS CREATED:")
    print("=" * 50)
    print("1. 📄 payment_state_validation.sql - SQL validation query")
    print("2. 📄 payment_validation.py - Python validation script")
    print("3. 📄 PAYMENT_MIGRATION_SUMMARY.md - Complete migration guide")
    
    print("\n🎯 NEXT STEPS:")
    print("=" * 50)
    print("1. Run validation to see current state")
    print("2. Choose appropriate migration method")
    print("3. Update module version triggers auto-migration")
    print("4. Verify results after migration")

if __name__ == "__main__":
    main()
