#!/usr/bin/env python3
"""
Test script for commission calculation logic in order_status_override module
Tests the new net commission formula: net commission = amount_total - (total internal - total external)
"""

def test_commission_calculation():
    """Test the commission calculation logic"""
    
    # Test data scenarios
    test_scenarios = [
        {
            'name': 'Basic commission test',
            'amount_total': 100000,
            'internal_commissions': {
                'agent1_rate': 2.0,
                'agent2_rate': 1.5,
                'manager_rate': 1.0,
                'director_rate': 0.5
            },
            'external_commissions': {
                'broker_rate': 3.0,
                'referrer_rate': 1.0,
                'cashback_rate': 0.5
            }
        },
        {
            'name': 'High external commission test',
            'amount_total': 200000,
            'internal_commissions': {
                'agent1_rate': 1.0,
                'agent2_rate': 1.0,
            },
            'external_commissions': {
                'broker_rate': 5.0,
                'referrer_rate': 2.0,
            }
        },
        {
            'name': 'Only internal commissions',
            'amount_total': 150000,
            'internal_commissions': {
                'agent1_rate': 3.0,
                'manager_rate': 2.0,
            },
            'external_commissions': {}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n=== {scenario['name']} ===")
        print(f"Amount Total: ${scenario['amount_total']:,.2f}")
        
        # Calculate internal commissions
        total_internal = 0
        for commission_type, rate in scenario['internal_commissions'].items():
            amount = scenario['amount_total'] * (rate / 100.0)
            total_internal += amount
            print(f"  {commission_type}: {rate}% = ${amount:,.2f}")
        
        print(f"Total Internal Commission: ${total_internal:,.2f}")
        
        # Calculate external commissions
        total_external = 0
        for commission_type, rate in scenario['external_commissions'].items():
            amount = scenario['amount_total'] * (rate / 100.0)
            total_external += amount
            print(f"  {commission_type}: {rate}% = ${amount:,.2f}")
        
        print(f"Total External Commission: ${total_external:,.2f}")
        
        # Calculate net commission using the new formula
        # net commission = amount_total - (total internal - total external)
        net_commission = scenario['amount_total'] - (total_internal - total_external)
        
        print(f"\nFormula: ${scenario['amount_total']:,.2f} - (${total_internal:,.2f} - ${total_external:,.2f})")
        print(f"Net Commission: ${net_commission:,.2f}")
        
        # Calculate what remains for the company
        company_net = scenario['amount_total'] - total_internal - total_external
        print(f"Company Net (after all commissions): ${company_net:,.2f}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("Testing Commission Calculation Logic")
    print("Formula: net commission = amount_total - (total internal - total external)")
    test_commission_calculation()
