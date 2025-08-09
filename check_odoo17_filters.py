#!/usr/bin/env python3
"""
Check common Odoo 17 account.move search filter names
"""

print("🔍 Checking Common Odoo 17 Account Move Filter Names...")
print("=" * 60)

# Common Odoo 17 search filter patterns for account.move
common_filters = [
    # State-based filters
    "state_draft",
    "state_posted", 
    "state_cancel",
    "draft",
    "posted",
    "cancel",
    
    # Date filters
    "filter_date",
    "filter_this_month",
    "filter_this_year",
    
    # Type filters
    "filter_invoice",
    "filter_bill",
    "filter_refund",
    
    # Status filters  
    "unpaid",
    "paid",
    "overdue",
    
    # Common Odoo patterns
    "all",
    "my",
    "unassigned"
]

print("📋 Most likely filter names for account.move in Odoo 17:")
print()
for filter_name in common_filters:
    print(f"   • {filter_name}")

print()
print("💡 Recommendation:")
print("   Instead of trying to extend after 'state_posted', use a safer approach:")
print("   1. Add filters at the end of the search view")
print("   2. Or reference a more common element like the last filter")
print("   3. Or add to the beginning with position='before' on first element")

print()
print("🎯 Solution: Use a safer XPath that doesn't depend on specific filter names")
print("   Example: <xpath expr=\"//search\" position=\"inside\">")
print("            or <xpath expr=\"//filter[last()]\" position=\"after\">")
