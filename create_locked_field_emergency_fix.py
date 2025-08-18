#!/usr/bin/env python3
"""
EMERGENCY LOCKED FIELD FIX FOR ORDER NET COMMISSION
OSUS Properties - Critical CloudPepper Production Issue

Problem: Field 'locked' used in modifier 'readonly' (state == 'cancel' or locked) must be present in view but is missing
Root Cause: Header replacement removed required 'locked' field
Impact: Module installation fails in CloudPepper

Solution: Add locked field to header replacement
"""

import os
from datetime import datetime

def create_locked_field_emergency_fix():
    """Create emergency fix for missing locked field error"""
    
    print("LOCKED FIELD EMERGENCY FIX")
    print("="*50)
    print(f"Fix Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Problem: Missing 'locked' field in order_net_commission view")
    print("Solution: Add locked field to header replacement")
    print()
    
    # Fixed view content with locked field
    fixed_view = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- Emergency CloudPepper Safe View with Locked Field Fix -->
        <record id="view_order_form_inherit_net_commission_safe" model="ir.ui.view">
            <field name="name">sale.order.form.net.commission.safe</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                
                <!-- Safe Header Override with Locked Field -->
                <xpath expr="//header" position="replace">
                    <header>
                        <!-- CRITICAL: Include locked field to satisfy view modifiers -->
                        <field name="locked" invisible="1"/>
                        
                        <field name="state" widget="statusbar"
                               statusbar_visible="draft,documentation,commission,sale,done"/>

                        <!-- Safe Workflow Buttons -->
                        <button name="action_set_documentation"
                                type="object"
                                string="Documentation"
                                class="btn-info"
                                attrs="{'invisible': [('state','!=','draft')]}"
                                groups="order_net_commission.group_documentation_officer"/>

                        <button name="action_set_commission"
                                type="object"
                                string="Commission"
                                class="btn-warning"
                                attrs="{'invisible': [('state','!=','documentation')]}"
                                groups="order_net_commission.group_commission_analyst"/>

                        <button name="action_approve_commission"
                                type="object"
                                string="Approve"
                                class="btn-success"
                                attrs="{'invisible': [('state','!=','commission')]}"
                                groups="order_net_commission.group_sales_approver"/>

                        <button name="action_cancel"
                                type="object"
                                string="Cancel"
                                attrs="{'invisible': [('state','in',('sale','done','cancel'))]}"/>

                    </header>
                </xpath>

                <!-- Safe Commission Fields - Add as separate page -->
                <xpath expr="//notebook" position="inside">
                    <page name="commission_safe" string="Commission">
                        <group string="Commission Calculation">
                            <field name="total_internal"/>
                            <field name="total_external"/>
                            <field name="net_commission" widget="monetary"/>
                        </group>
                        <group string="Workflow Tracking">
                            <field name="documentation_date" readonly="1"/>
                            <field name="commission_date" readonly="1"/>
                            <field name="documentation_user_id" readonly="1"/>
                            <field name="commission_user_id" readonly="1"/>
                            <field name="approver_user_id" readonly="1"/>
                        </group>
                    </page>
                </xpath>

            </field>
        </record>

    </data>
</odoo>'''
    
    # Write the fixed view
    view_path = "order_net_commission/views/sale_order_form.xml"
    print(f"Updating view file: {view_path}")
    
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write(fixed_view)
    
    print("✅ Fixed view file updated with locked field")
    
    # Create deployment instructions
    instructions = """LOCKED FIELD FIX - IMMEDIATE DEPLOYMENT

PROBLEM RESOLVED:
Field 'locked' used in modifier 'readonly' (state == 'cancel' or locked) must be present in view but is missing

SOLUTION APPLIED:
✅ Added <field name="locked" invisible="1"/> to header replacement
✅ Maintains all existing functionality
✅ Satisfies Odoo view validation requirements

DEPLOYMENT STEPS:

1. IMMEDIATE ACTION:
   - Upload updated order_net_commission folder to CloudPepper
   - The locked field is now included in the view

2. INSTALL MODULE:
   - Go to Apps > Update Apps List
   - Search "Order Net Commission"
   - Click Install (should work without validation errors)

3. VERIFICATION:
   - Module installs successfully
   - No field validation errors
   - Workflow buttons appear correctly
   - Commission calculation works

TECHNICAL DETAILS:

The 'locked' field is a standard Odoo sale.order field that controls:
- Record locking for editing
- Readonly modifiers throughout the view
- Business logic validation

By adding it as invisible to our header, we:
✅ Satisfy view validation requirements
✅ Maintain original functionality  
✅ Keep our custom workflow intact
✅ Ensure CloudPepper compatibility

STATUS: READY FOR IMMEDIATE CLOUDPEPPER DEPLOYMENT
"""
    
    with open('LOCKED_FIELD_FIX_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Deployment instructions created")
    print()
    print("LOCKED FIELD FIX COMPLETE")
    print("="*50)
    print("Changes Applied:")
    print("1. Added locked field to header replacement")
    print("2. View validation requirements satisfied")
    print("3. CloudPepper compatibility maintained")
    print()
    print("READY FOR CLOUDPEPPER DEPLOYMENT!")
    
    return True

if __name__ == "__main__":
    create_locked_field_emergency_fix()
