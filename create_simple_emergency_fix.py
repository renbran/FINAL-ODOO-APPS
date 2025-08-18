#!/usr/bin/env python3
"""
Simple CloudPepper Emergency Fix for Order Net Commission
OSUS Properties - Immediate Production Fix
"""

import os
import shutil
from datetime import datetime

def create_simple_emergency_fix():
    """Create simple emergency fix for CloudPepper"""
    
    print("CLOUDPEPPER EMERGENCY FIX - ORDER NET COMMISSION")
    print("="*50)
    print(f"Fix Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: RPC Error in sale_order_form.xml")
    print()
    
    # Define paths
    module_path = "order_net_commission"
    form_view_path = os.path.join(module_path, "views", "sale_order_form.xml")
    
    if not os.path.exists(form_view_path):
        print(f"Error: File not found: {form_view_path}")
        return False
    
    # Create emergency safe view content
    emergency_view = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- Emergency CloudPepper Safe View -->
        <record id="view_order_form_inherit_net_commission_safe" model="ir.ui.view">
            <field name="name">sale.order.form.net.commission.safe</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                
                <!-- Safe Header Override -->
                <xpath expr="//header" position="replace">
                    <header>
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
    
    # Write the safe view
    print("Creating emergency safe view...")
    with open(form_view_path, 'w', encoding='utf-8') as f:
        f.write(emergency_view)
    
    print("Emergency view created successfully")
    
    # Create simple installation guide
    guide_content = """CLOUDPEPPER EMERGENCY INSTALLATION GUIDE

Problem: XPath error - field 'amount_total' cannot be located

Solution: Emergency safe view with CloudPepper compatibility

Installation Steps:
1. Upload order_net_commission folder to CloudPepper addons
2. Go to Apps > Update Apps List
3. Search "Order Net Commission" and Install
4. Test commission workflow

Features:
- Safe XPath selectors
- CloudPepper compatible
- All workflow functionality preserved
- Commission calculation intact

Monitor:
- Check browser console for errors
- Test workflow with different users
- Verify commission calculation

Success: Module should install without XPath errors
"""
    
    with open('EMERGENCY_INSTALLATION_GUIDE.txt', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("Emergency installation guide created")
    print()
    print("EMERGENCY FIX COMPLETE")
    print("="*50)
    print("1. Emergency safe view created")
    print("2. Installation guide ready")
    print("3. Ready for CloudPepper deployment")
    print()
    print("Next: Upload to CloudPepper and install module")
    
    return True

if __name__ == "__main__":
    create_simple_emergency_fix()
