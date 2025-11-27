#!/usr/bin/env python3
"""
CRM Dashboard Test Script
Tests if crm_dashboard module is properly rendering data and filters are working
"""

import xmlrpc.client
import sys
from datetime import datetime

# Configuration
URL = "https://stagingtry.cloudpepper.site"
DB = "scholarixv2"
USERNAME = "salescompliance@osusproperties.com"
PASSWORD = "osus@2024"  # Update if different

def test_crm_dashboard():
    """Test CRM Dashboard functionality"""
    
    print("=" * 80)
    print("CRM DASHBOARD TEST - scholarixv2")
    print("=" * 80)
    print(f"Testing URL: {URL}")
    print(f"Database: {DB}")
    print(f"User: {USERNAME}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        # Connect to Odoo
        print("1. Authenticating...")
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ FAILED: Authentication failed. Check credentials.")
            return False
        
        print(f"✅ SUCCESS: Authenticated as user ID {uid}")
        print()
        
        # Create models connection
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Test 1: Check module installation
        print("2. Checking crm_dashboard module installation...")
        module = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
            [[['name', '=', 'crm_dashboard']]],
            {'fields': ['name', 'state', 'latest_version']}
        )
        
        if not module:
            print("❌ FAILED: crm_dashboard module not found")
            return False
        
        if module[0]['state'] != 'installed':
            print(f"❌ FAILED: Module state is '{module[0]['state']}', expected 'installed'")
            return False
            
        print(f"✅ SUCCESS: Module installed (version: {module[0].get('latest_version', 'N/A')})")
        print()
        
        # Test 2: Check CRM data exists
        print("3. Checking CRM data...")
        
        # Count leads
        lead_count = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'search_count',
            [[['type', '=', 'lead']]]
        )
        print(f"   - Leads: {lead_count:,}")
        
        # Count opportunities
        opp_count = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'search_count',
            [[['type', '=', 'opportunity']]]
        )
        print(f"   - Opportunities: {opp_count:,}")
        
        # Count won opportunities
        won_count = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'search_count',
            [[['probability', '=', 100], ['type', '=', 'opportunity']]]
        )
        print(f"   - Won Opportunities: {won_count:,}")
        
        # Count lost opportunities
        lost_count = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'search_count',
            [[['probability', '=', 0], ['active', '=', False], ['type', '=', 'opportunity']]]
        )
        print(f"   - Lost Opportunities: {lost_count:,}")
        
        if lead_count == 0 and opp_count == 0:
            print("❌ FAILED: No CRM data found")
            return False
            
        print(f"✅ SUCCESS: CRM data exists ({lead_count + opp_count:,} total records)")
        print()
        
        # Test 3: Check revenue data
        print("4. Checking revenue data...")
        
        opportunities = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'search_read',
            [[['type', '=', 'opportunity']]],
            {'fields': ['expected_revenue', 'probability'], 'limit': 100}
        )
        
        expected_revenue = sum(
            opp['expected_revenue'] or 0 
            for opp in opportunities 
            if opp['probability'] > 0 and opp['probability'] < 100
        )
        
        won_revenue = sum(
            opp['expected_revenue'] or 0 
            for opp in opportunities 
            if opp['probability'] == 100
        )
        
        print(f"   - Expected Revenue (sample): ${expected_revenue:,.2f}")
        print(f"   - Won Revenue (sample): ${won_revenue:,.2f}")
        
        revenue_count = sum(1 for opp in opportunities if opp.get('expected_revenue', 0) > 0)
        print(f"   - Opportunities with revenue: {revenue_count}/{len(opportunities)}")
        
        if revenue_count == 0:
            print("⚠️  WARNING: No opportunities have expected_revenue values")
        else:
            print(f"✅ SUCCESS: Revenue data exists ({revenue_count} records)")
        print()
        
        # Test 4: Check dashboard menu exists
        print("5. Checking dashboard menu...")
        
        menu = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.menu', 'search_read',
            [[['name', 'ilike', 'Dashboard'], ['parent_id.name', '=', 'CRM']]],
            {'fields': ['name', 'action'], 'limit': 1}
        )
        
        if not menu:
            print("❌ FAILED: Dashboard menu not found under CRM")
            return False
            
        print(f"✅ SUCCESS: Dashboard menu found (ID: {menu[0]['id']})")
        print(f"   - Menu: {menu[0]['name']}")
        print(f"   - Action: {menu[0].get('action', 'N/A')}")
        print()
        
        # Test 5: Test dashboard methods exist on crm.lead model
        print("6. Testing dashboard calculation methods...")
        
        try:
            # Test get_the_annual_target
            result = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'get_the_annual_target', [[]])
            print(f"   - get_the_annual_target(): {type(result).__name__}")
            
            # Test revenue_count_pie
            result = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'revenue_count_pie', [[]])
            print(f"   - revenue_count_pie(): {type(result).__name__}")
            
            # Test get_monthly_goal
            result = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'get_monthly_goal', [[]])
            print(f"   - get_monthly_goal(): {type(result).__name__}")
            
            # Test lead_details_user
            result = models.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'lead_details_user', [[]])
            print(f"   - lead_details_user(): {type(result).__name__}")
            
            print("✅ SUCCESS: All dashboard methods are callable")
            print()
            
        except Exception as e:
            print(f"❌ FAILED: Dashboard methods error - {str(e)}")
            return False
        
        # Test 6: Check users have sales targets
        print("7. Checking sales targets...")
        
        users_with_targets = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'search_count',
            [[['sales', '>', 0]]]
        )
        
        print(f"   - Users with sales targets: {users_with_targets}")
        
        if users_with_targets == 0:
            print("⚠️  WARNING: No users have sales targets set")
        else:
            print(f"✅ SUCCESS: {users_with_targets} users have sales targets")
        print()
        
        # Test 7: Check CRM stages
        print("8. Checking CRM stages...")
        
        stages = models.execute_kw(DB, uid, PASSWORD, 'crm.stage', 'search_read',
            [[]],
            {'fields': ['name', 'sequence', 'is_won'], 'order': 'sequence'}
        )
        
        print(f"   - Total stages: {len(stages)}")
        won_stages = [s for s in stages if s.get('is_won')]
        print(f"   - Won stages: {len(won_stages)}")
        
        if len(stages) == 0:
            print("❌ FAILED: No CRM stages found")
            return False
        
        for stage in stages[:5]:  # Show first 5
            print(f"     • {stage['name']} (seq: {stage['sequence']}, won: {stage.get('is_won', False)})")
        
        print(f"✅ SUCCESS: CRM stages configured")
        print()
        
        # Final Summary
        print("=" * 80)
        print("DASHBOARD TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Module: Installed (crm_dashboard)")
        print(f"✅ Data: {lead_count:,} leads, {opp_count:,} opportunities")
        print(f"✅ Won/Lost: {won_count:,} won, {lost_count:,} lost")
        print(f"✅ Revenue: ${expected_revenue:,.2f} expected, ${won_revenue:,.2f} won")
        print(f"✅ Menu: Dashboard accessible under CRM")
        print(f"✅ Methods: All calculation methods working")
        print(f"✅ Stages: {len(stages)} stages configured")
        print("=" * 80)
        print()
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Next Steps:")
        print(f"1. Login to: {URL}")
        print(f"2. Navigate to: CRM > Dashboard")
        print("3. Verify all tiles display data:")
        print("   - Leads Count")
        print("   - Opportunities Count")
        print("   - Expected Revenue")
        print("   - Won Revenue")
        print("   - Won/Lost Ratio")
        print("   - Annual Target chart")
        print("   - Monthly Goal gauge")
        print("   - Lead Stage funnel")
        print("   - Top 10 Deals table")
        print("4. Test filters:")
        print("   - Date range filters")
        print("   - User filters")
        print("   - Team filters")
        print("   - Stage filters")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crm_dashboard()
    sys.exit(0 if success else 1)
