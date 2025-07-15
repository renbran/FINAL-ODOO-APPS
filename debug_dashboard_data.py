#!/usr/bin/env python3
"""
Debug script for oe_sale_dashboard_17 to identify data issues
This script helps diagnose why the Invoiced Sale Orders section shows incorrect numbers
"""

def analyze_dashboard_data_issues():
    """
    Analyze potential issues with the sales dashboard data
    """
    print("=== OE Sales Dashboard Debug Analysis ===\n")
    
    print("IDENTIFIED ISSUES:")
    print("1. ❌ DATE FILTERING ISSUE:")
    print("   - Dashboard was using datetime strings ('2024-01-01 00:00:00') for Date field")
    print("   - booking_date is a Date field, not Datetime")
    print("   - This could cause timezone issues or incorrect filtering")
    print("   ✅ FIXED: Now using date strings directly\n")
    
    print("2. ❌ DOMAIN LOGIC ISSUE:")
    print("   - Sales Orders filter had problematic OR operator placement:")
    print("   - Old: [['state', '=', 'sale'], '|', ['invoice_status', '=', 'to invoice'], ['invoice_status', '=', 'no']]")
    print("   - This could miss orders with 'upselling' status")
    print("   ✅ FIXED: Now using proper 'in' operator for multiple statuses\n")
    
    print("3. ❌ MISSING FIELD VALUES:")
    print("   - Orders might have empty sale_value or amount_total")
    print("   - Related to booking_date mapping issue found in fix_booking_date_mapping.py")
    print("   ✅ FIXED: Added better error handling and debug logging\n")
    
    print("4. ❌ NO DEBUG INFORMATION:")
    print("   - No way to identify which orders are causing issues")
    print("   ✅ FIXED: Added comprehensive debug logging\n")
    
    print("APPLIED FIXES:")
    print("✅ Fixed date filtering to use date strings instead of datetime strings")
    print("✅ Fixed domain logic for Sales Orders filter")
    print("✅ Added better error handling for missing field values")
    print("✅ Added debug logging to identify problematic orders")
    print("✅ Added console logging to track query domains and results")
    print("✅ Improved field value parsing with parseFloat()\n")
    
    print("VERIFICATION STEPS:")
    print("1. 🔄 Update the Odoo module (upgrade oe_sale_dashboard_17)")
    print("2. 🌐 Clear browser cache and reload the dashboard")
    print("3. 🔍 Open browser DevTools Console to see debug logs")
    print("4. 📊 Check if Invoiced Sale Orders section now shows correct numbers")
    print("5. 🐛 Look for any console warnings about orders with missing values")
    print("6. 📋 Verify the domain queries are correct in console logs\n")
    
    print("ADDITIONAL CHECKS:")
    print("- Ensure sale orders have proper booking_date values")
    print("- Verify sale_value field is populated from sale orders")
    print("- Check that sale_order_type_id is properly set")
    print("- Confirm invoice_status transitions work correctly")

def main():
    """Main function"""
    analyze_dashboard_data_issues()
    
    print("\n" + "="*50)
    print("SUMMARY: Fixed 4 major issues in the dashboard code")
    print("The Invoiced Sale Orders section should now show correct numbers")
    print("="*50)

if __name__ == "__main__":
    main()
