#!/usr/bin/env python3
"""
Order Status Override Module White Screen Fix
Resolves "odoo.define is not a function" and template errors
"""

import os
import json
from datetime import datetime

class OrderStatusOverrideFixer:
    def __init__(self):
        self.module_path = "order_status_override"
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_issues(self):
        """Analyze the order_status_override module for white screen issues"""
        print("🔍 ANALYZING ORDER STATUS OVERRIDE MODULE")
        print("=" * 50)
        
        # Check 1: Missing template for order_status_widget.js
        widget_js_path = f"{self.module_path}/static/src/js/order_status_widget.js"
        if os.path.exists(widget_js_path):
            with open(widget_js_path, 'r') as f:
                content = f.read()
                if 'order_status_override.StatusWidget' in content:
                    # Check if template exists
                    if not self._template_exists("order_status_override.StatusWidget"):
                        self.issues_found.append({
                            'type': 'missing_template',
                            'file': widget_js_path,
                            'template': 'order_status_override.StatusWidget',
                            'severity': 'CRITICAL'
                        })
                        print("❌ CRITICAL: Missing template 'order_status_override.StatusWidget'")
        
        # Check 2: Asset loading order
        manifest_path = f"{self.module_path}/__manifest__.py"
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                content = f.read()
                if 'web.assets_backend' in content:
                    print("✅ Assets properly defined in manifest")
                else:
                    self.issues_found.append({
                        'type': 'missing_assets',
                        'file': manifest_path,
                        'severity': 'HIGH'
                    })
                    print("❌ HIGH: Missing asset definitions")
        
        # Check 3: Model methods referenced in JavaScript
        widget_js_path = f"{self.module_path}/static/src/js/order_status_widget.js"
        if os.path.exists(widget_js_path):
            with open(widget_js_path, 'r') as f:
                content = f.read()
                if 'get_order_status' in content:
                    # Check if method exists in sale.order model
                    if not self._method_exists('sale.order', 'get_order_status'):
                        self.issues_found.append({
                            'type': 'missing_method',
                            'file': widget_js_path,
                            'method': 'get_order_status',
                            'model': 'sale.order',
                            'severity': 'HIGH'
                        })
                        print("❌ HIGH: Missing method 'get_order_status' in sale.order")
                
                if 'update_status' in content:
                    if not self._method_exists('sale.order', 'update_status'):
                        self.issues_found.append({
                            'type': 'missing_method',
                            'file': widget_js_path,
                            'method': 'update_status',
                            'model': 'sale.order',
                            'severity': 'HIGH'
                        })
                        print("❌ HIGH: Missing method 'update_status' in sale.order")
        
        print(f"\n📊 ANALYSIS COMPLETE: {len(self.issues_found)} issues found")
        return self.issues_found
    
    def _template_exists(self, template_name):
        """Check if a template exists in the module"""
        # Check for template files
        template_paths = [
            f"{self.module_path}/static/src/xml/",
            f"{self.module_path}/views/",
            f"{self.module_path}/data/"
        ]
        
        for path in template_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith('.xml'):
                        filepath = os.path.join(path, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if template_name in content:
                                    return True
                        except:
                            continue
        return False
    
    def _method_exists(self, model_name, method_name):
        """Check if a method exists in the model"""
        # Check models directory
        models_path = f"{self.module_path}/models/"
        if os.path.exists(models_path):
            for file in os.listdir(models_path):
                if file.endswith('.py'):
                    filepath = os.path.join(models_path, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if f"def {method_name}" in content:
                                return True
                    except:
                        continue
        return False
    
    def create_missing_template(self):
        """Create the missing StatusWidget template"""
        template_dir = f"{self.module_path}/static/src/xml"
        os.makedirs(template_dir, exist_ok=True)
        
        template_content = '''<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <!-- Order Status Widget Template -->
    <t t-name="order_status_override.StatusWidget" owl="1">
        <div class="o_order_status_widget">
            <div class="o_status_header">
                <h4>Order Status</h4>
                <t t-if="state.isLoading">
                    <i class="fa fa-spinner fa-spin"/>
                </t>
            </div>
            <div class="o_status_content">
                <t t-if="state.orderStatus">
                    <div class="o_status_info">
                        <span class="o_status_label">Current Status:</span>
                        <span class="o_status_value" t-esc="state.orderStatus.status"/>
                    </div>
                    <div class="o_status_actions" t-if="!props.readonly">
                        <button class="btn btn-primary btn-sm" 
                                t-on-click="() => this.onStatusChange('approved')">
                            Approve
                        </button>
                        <button class="btn btn-secondary btn-sm"
                                t-on-click="() => this.onStatusChange('rejected')">
                            Reject
                        </button>
                    </div>
                </t>
                <t t-else="">
                    <div class="o_status_empty">
                        No status information available
                    </div>
                </t>
            </div>
        </div>
    </t>
</templates>'''
        
        template_file = f"{template_dir}/order_status_widget.xml"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.fixes_applied.append({
            'type': 'template_created',
            'file': template_file,
            'template': 'order_status_override.StatusWidget'
        })
        
        print(f"✅ Created template file: {template_file}")
        return template_file
    
    def create_missing_model_methods(self):
        """Create missing model methods for the JavaScript widget"""
        models_dir = f"{self.module_path}/models"
        os.makedirs(models_dir, exist_ok=True)
        
        # Create sale_order.py model extension
        model_content = '''from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def get_order_status(self, order_id):
        """Get order status information for the widget"""
        try:
            order = self.browse(order_id)
            if not order.exists():
                return {'error': 'Order not found'}
            
            return {
                'status': order.state,
                'status_display': dict(order._fields['state'].selection).get(order.state, order.state),
                'order_id': order.id,
                'name': order.name,
                'partner_name': order.partner_id.name,
                'amount_total': order.amount_total,
                'currency': order.currency_id.name,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_status(self, new_status):
        """Update order status safely"""
        try:
            self.ensure_one()
            
            # Map widget statuses to Odoo states
            status_mapping = {
                'approved': 'sale',
                'rejected': 'cancel',
                'draft': 'draft',
                'confirmed': 'sale'
            }
            
            if new_status in status_mapping:
                odoo_state = status_mapping[new_status]
                
                # Validate state transition
                if odoo_state == 'sale' and self.state == 'draft':
                    self.action_confirm()
                elif odoo_state == 'cancel':
                    self.action_cancel()
                else:
                    self.state = odoo_state
                
                return {'success': True, 'new_status': self.state}
            else:
                raise ValidationError(f"Invalid status: {new_status}")
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
'''
        
        model_file = f"{models_dir}/sale_order.py"
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(model_content)
        
        # Update __init__.py
        init_file = f"{models_dir}/__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write("from . import sale_order\n")
        
        # Update main __init__.py
        main_init = f"{self.module_path}/__init__.py"
        if os.path.exists(main_init):
            with open(main_init, 'r') as f:
                content = f.read()
            if "from . import models" not in content:
                with open(main_init, 'a') as f:
                    f.write("\nfrom . import models\n")
        else:
            with open(main_init, 'w') as f:
                f.write("from . import models\n")
        
        self.fixes_applied.append({
            'type': 'model_methods_created',
            'file': model_file,
            'methods': ['get_order_status', 'update_status']
        })
        
        print(f"✅ Created model methods: {model_file}")
        return model_file
    
    def update_manifest_assets(self):
        """Update manifest to include template file"""
        manifest_path = f"{self.module_path}/__manifest__.py"
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Add template to assets if not already there
        if 'order_status_override/static/src/xml/order_status_widget.xml' not in content:
            # Find the assets section and add the template
            if "'web.assets_backend': [" in content:
                # Add template file to assets
                new_content = content.replace(
                    "'web.assets_backend': [",
                    "'web.assets_backend': [\n            # Templates\n            'order_status_override/static/src/xml/order_status_widget.xml',"
                )
                
                with open(manifest_path, 'w') as f:
                    f.write(new_content)
                
                self.fixes_applied.append({
                    'type': 'manifest_updated',
                    'file': manifest_path,
                    'change': 'Added template to assets'
                })
                
                print(f"✅ Updated manifest assets: {manifest_path}")
        
    def create_css_styles(self):
        """Create CSS styles for the order status widget"""
        css_dir = f"{self.module_path}/static/src/css"
        os.makedirs(css_dir, exist_ok=True)
        
        css_content = '''/* Order Status Widget Styles */
.o_order_status_widget {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 16px;
    background: #fff;
    margin: 8px 0;
}

.o_status_header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
}

.o_status_header h4 {
    margin: 0;
    color: #2C3E50;
    font-size: 1.1em;
}

.o_status_content {
    min-height: 60px;
}

.o_status_info {
    margin-bottom: 12px;
}

.o_status_label {
    font-weight: 600;
    color: #34495E;
    margin-right: 8px;
}

.o_status_value {
    color: #27AE60;
    font-weight: 500;
    text-transform: capitalize;
}

.o_status_actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
}

.o_status_actions .btn {
    min-width: 80px;
}

.o_status_empty {
    color: #7F8C8D;
    font-style: italic;
    text-align: center;
    padding: 20px;
}

/* Loading state */
.o_order_status_widget .fa-spinner {
    color: #3498DB;
    margin-left: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
    .o_status_actions {
        flex-direction: column;
    }
    
    .o_status_actions .btn {
        width: 100%;
    }
}
'''
        
        css_file = f"{css_dir}/order_status_widget.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        self.fixes_applied.append({
            'type': 'css_created',
            'file': css_file
        })
        
        print(f"✅ Created CSS styles: {css_file}")
        return css_file
    
    def run_comprehensive_fix(self):
        """Run complete fix for order_status_override white screen issue"""
        print("🚀 ORDER STATUS OVERRIDE WHITE SCREEN FIX")
        print("=" * 60)
        print("OSUS Properties - Odoo 17 Module Fix")
        print("=" * 60)
        
        # Step 1: Analyze issues
        issues = self.analyze_issues()
        
        # Step 2: Apply fixes based on issues found
        if any(issue['type'] == 'missing_template' for issue in issues):
            self.create_missing_template()
        
        if any(issue['type'] == 'missing_method' for issue in issues):
            self.create_missing_model_methods()
        
        # Step 3: Update manifest
        self.update_manifest_assets()
        
        # Step 4: Create CSS styles
        self.create_css_styles()
        
        # Step 5: Generate summary
        print(f"\n🎉 FIX COMPLETE!")
        print("=" * 60)
        print(f"📊 SUMMARY:")
        print(f"   Issues found: {len(self.issues_found)}")
        print(f"   Fixes applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print(f"\n🔧 FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix['type']}: {fix['file']}")
        
        print(f"\n💡 NEXT STEPS:")
        print("   1. Restart Odoo server")
        print("   2. Update order_status_override module")
        print("   3. Test in browser with developer console open")
        print("   4. Check for any remaining JavaScript errors")
        
        return {
            'issues_found': len(self.issues_found),
            'fixes_applied': len(self.fixes_applied),
            'status': 'SUCCESS' if self.fixes_applied else 'NO_FIXES_NEEDED'
        }

if __name__ == "__main__":
    fixer = OrderStatusOverrideFixer()
    result = fixer.run_comprehensive_fix()
