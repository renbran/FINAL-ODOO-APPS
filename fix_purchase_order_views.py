#!/usr/bin/env python3
"""
Purchase Order Views Fix for Odoo 17.0
Fixes the XPath error in commission_fields module
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def fix_purchase_order_views():
    """Fix the purchase order views XML file"""
    print("🔧 Fixing Purchase Order Views for Odoo 17.0...")
    
    file_path = Path("commission_fields/views/purchase_order_views.xml")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Read the current file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create new XML content with multiple fallback strategies
        new_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add default account field to purchase order form -->
    <record id="view_purchase_order_form_commission_default_account" model="ir.ui.view">
        <field name="name">purchase.order.form.commission.default.account</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='partner_id']" position="after">
                <field name="default_account_id"/>
            </xpath>
        </field>
    </record>

    <!-- Add commission fields to purchase order form - Strategy 1: Add after partner_ref -->
    <record id="view_purchase_order_form_commission_fields" model="ir.ui.view">
        <field name="name">purchase.order.form.commission.fields</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='partner_ref']" position="after">
                <separator string="External Commission" colspan="4"/>
                <group string="External Commission" name="external_commission_group" colspan="4">
                    <field name="external_commission_type"/>
                    <field name="external_percentage" invisible="not show_external_percentage"/>
                    <field name="external_fixed_amount" invisible="not show_external_fixed_amount"/>
                    <field name="show_external_percentage" invisible="1"/>
                    <field name="show_external_fixed_amount" invisible="1"/>
                </group>
            </xpath>
        </field>
    </record>

    <!-- Alternative: Add commission fields as a separate page if notebook exists -->
    <record id="view_purchase_order_form_commission_page" model="ir.ui.view">
        <field name="name">purchase.order.form.commission.page</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook[last()]" position="inside">
                <page string="Commission" name="commission_page">
                    <group string="External Commission Details">
                        <group>
                            <field name="external_commission_type"/>
                            <field name="external_percentage" invisible="not show_external_percentage"/>
                            <field name="external_fixed_amount" invisible="not show_external_fixed_amount"/>
                        </group>
                        <group>
                            <field name="show_external_percentage" invisible="1"/>
                            <field name="show_external_fixed_amount" invisible="1"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>

    <!-- Add account field to purchase order line tree view -->
    <record id="view_purchase_order_line_tree_commission_account" model="ir.ui.view">
        <field name="name">purchase.order.line.tree.commission.account</field>
        <field name="model">purchase.order.line</field>
        <field name="inherit_id" ref="purchase.purchase_order_line_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='product_id']" position="after">
                <field name="account_id"/>
            </xpath>
        </field>
    </record>
</odoo>
'''
        
        # Write the new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed purchase order views: {file_path}")
        
        # Validate the XML
        try:
            ET.parse(file_path)
            print("✅ XML validation passed")
            return True
        except ET.ParseError as e:
            print(f"❌ XML validation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing purchase order views: {e}")
        return False

def create_safe_purchase_order_views():
    """Create a completely safe version of the purchase order views"""
    print("🛡️ Creating safe purchase order views...")
    
    file_path = Path("commission_fields/views/purchase_order_views_safe.xml")
    
    safe_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Safe version: Add commission fields directly to the main group -->
    <record id="view_purchase_order_form_commission_safe" model="ir.ui.view">
        <field name="name">purchase.order.form.commission.safe</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <!-- Add commission fields after the currency field -->
            <xpath expr="//field[@name='currency_id']" position="after">
                <field name="external_commission_type"/>
                <field name="external_percentage" invisible="not show_external_percentage"/>
                <field name="external_fixed_amount" invisible="not show_external_fixed_amount"/>
                <field name="show_external_percentage" invisible="1"/>
                <field name="show_external_fixed_amount" invisible="1"/>
                <field name="default_account_id"/>
            </xpath>
        </field>
    </record>

    <!-- Safe tree view for purchase order lines -->
    <record id="view_purchase_order_line_tree_commission_safe" model="ir.ui.view">
        <field name="name">purchase.order.line.tree.commission.safe</field>
        <field name="model">purchase.order.line</field>
        <field name="inherit_id" ref="purchase.purchase_order_line_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='name']" position="after">
                <field name="account_id" optional="hide"/>
            </xpath>
        </field>
    </record>
</odoo>
'''
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(safe_content)
        
        # Validate the XML
        ET.parse(file_path)
        print(f"✅ Created safe purchase order views: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating safe views: {e}")
        return False

def update_manifest_for_safe_views():
    """Update the manifest to use the safe views"""
    print("📋 Updating manifest for safe views...")
    
    manifest_path = Path("commission_fields/__manifest__.py")
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the views reference
        if 'purchase_order_views.xml' in content:
            content = content.replace(
                'views/purchase_order_views.xml',
                'views/purchase_order_views_safe.xml'
            )
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Updated manifest to use safe views")
            return True
        else:
            print("⚠️  purchase_order_views.xml not found in manifest")
            return False
            
    except Exception as e:
        print(f"❌ Error updating manifest: {e}")
        return False

def main():
    """Run the purchase order views fix"""
    print("🚀 Starting Purchase Order Views Fix...")
    print("=" * 50)
    
    success = True
    
    # Try to fix the existing file first
    if not fix_purchase_order_views():
        print("⚠️  Primary fix failed, creating safe version...")
        success = create_safe_purchase_order_views()
        if success:
            update_manifest_for_safe_views()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Purchase Order Views Fix Complete!")
        print("\nNext steps:")
        print("1. Restart your Odoo service")
        print("2. Try to upgrade the commission_fields module")
        print("3. Check the purchase order form for commission fields")
    else:
        print("\n" + "=" * 50)
        print("❌ Fix failed. Manual intervention required.")
        print("\nManual fix steps:")
        print("1. Remove the problematic view from purchase_order_views.xml")
        print("2. Add commission fields to a different location")
        print("3. Test the module installation")
    
    return success

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Script failed: {e}")
        exit(1)
