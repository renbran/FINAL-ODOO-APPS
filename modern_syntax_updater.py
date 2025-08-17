#!/usr/bin/env python3
"""
Odoo 17 Modern JS/CSS Compliance Updater
Updates JavaScript and CSS files to use modern Odoo 17 syntax and patterns
"""

import os
import re
from pathlib import Path

class ModernSyntaxUpdater:
    def __init__(self):
        self.osus_colors = {
            'primary': '#800020',
            'gold': '#FFD700',
            'light_gold': '#FFF8DC',
            'dark_gold': '#B8860B',
            'white': '#FFFFFF',
            'accent': '#A0522D'
        }
        self.updates_applied = []

    def update_javascript_to_modern_odoo17(self, js_file_path):
        """Update JavaScript to modern Odoo 17 syntax"""
        print(f"🔧 Modernizing JavaScript: {js_file_path}")
        
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Ensure @odoo-module declaration
        if '/** @odoo-module **/' not in content:
            content = '/** @odoo-module **/\n\n' + content
        
        # Update import statements to modern syntax
        if 'odoo.define(' in content:
            # Convert legacy odoo.define to modern imports
            content = self.convert_legacy_define_to_imports(content)
        
        # Add modern error handling patterns
        if 'try {' not in content and 'async ' in content:
            content = self.add_async_error_handling(content)
        
        # Update jQuery to modern alternatives where possible
        content = self.modernize_jquery_usage(content)
        
        # Add OSUS color constants
        if 'brandColors' not in content and ('Chart' in content or 'color' in content):
            content = self.add_osus_brand_colors(content)
        
        # Update to use modern OWL patterns
        content = self.modernize_owl_patterns(content)
        
        if content != original_content:
            # Create backup
            backup_path = f"{js_file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write updated content
            with open(js_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updates_applied.append(f"Updated JavaScript: {js_file_path}")
            return True
        
        return False

    def convert_legacy_define_to_imports(self, content):
        """Convert legacy odoo.define to modern import statements"""
        # This is a simplified conversion - real implementation would be more complex
        if "odoo.define(" in content:
            # Add comment about legacy code
            content = content.replace(
                "odoo.define(",
                "// Legacy odoo.define - consider modernizing to ES6 imports\nodoo.define("
            )
        
        return content

    def add_async_error_handling(self, content):
        """Add proper async error handling"""
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            updated_lines.append(line)
            if 'async ' in line and 'function' in line and 'try' not in line:
                # Add comment suggesting error handling
                updated_lines.append('        // TODO: Add try-catch for error handling')
        
        return '\n'.join(updated_lines)

    def modernize_jquery_usage(self, content):
        """Replace jQuery with modern alternatives where appropriate"""
        # Replace common jQuery patterns
        replacements = [
            (r'\$\(document\)\.ready\(', 'document.addEventListener("DOMContentLoaded", '),
            (r'\$\(\'\.([^\']+)\'\)', 'document.querySelector(".$1")'),
            (r'\$\(\"\.([^\"]+)\"\)', 'document.querySelector(".$1")'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        return content

    def add_osus_brand_colors(self, content):
        """Add OSUS brand colors for consistency"""
        osus_colors_js = f"""
        // OSUS Properties Brand Colors
        const brandColors = {{
            primary: '{self.osus_colors["primary"]}',
            gold: '{self.osus_colors["gold"]}',
            lightGold: '{self.osus_colors["light_gold"]}',
            darkGold: '{self.osus_colors["dark_gold"]}',
            white: '{self.osus_colors["white"]}',
            accent: '{self.osus_colors["accent"]}',
            
            chartColors: [
                '{self.osus_colors["primary"]}',
                '{self.osus_colors["gold"]}',
                '{self.osus_colors["accent"]}',
            ],
            
            chartBackgrounds: [
                '{self.osus_colors["primary"]}20',
                '{self.osus_colors["gold"]}20',
                '{self.osus_colors["accent"]}20',
            ]
        }};
        """
        
        # Insert after @odoo-module declaration
        if '/** @odoo-module **/' in content:
            content = content.replace(
                '/** @odoo-module **/',
                f'/** @odoo-module **/{osus_colors_js}'
            )
        
        return content

    def modernize_owl_patterns(self, content):
        """Update to modern OWL component patterns"""
        # Add modern OWL import suggestions
        if 'Component' in content and 'import' not in content:
            modern_imports = """
// Modern OWL imports for Odoo 17
// import { Component, useState, onMounted, onWillStart } from "@odoo/owl";
// import { useService } from "@web/core/utils/hooks";
// import { registry } from "@web/core/registry";
"""
            content = modern_imports + content
        
        return content

    def update_css_to_modern_odoo17(self, css_file_path):
        """Update CSS to modern Odoo 17 patterns"""
        print(f"🎨 Modernizing CSS: {css_file_path}")
        
        with open(css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add CSS custom properties for OSUS colors
        if ':root' not in content and self.osus_colors['primary'] in content:
            content = self.add_css_custom_properties(content)
        
        # Convert to BEM methodology
        content = self.convert_to_bem_methodology(content)
        
        # Modernize CSS patterns
        content = self.modernize_css_patterns(content)
        
        # Reduce !important usage
        content = self.reduce_important_usage(content)
        
        if content != original_content:
            # Create backup
            backup_path = f"{css_file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write updated content
            with open(css_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updates_applied.append(f"Updated CSS: {css_file_path}")
            return True
        
        return False

    def add_css_custom_properties(self, content):
        """Add CSS custom properties for OSUS brand colors"""
        custom_properties = f"""
/* OSUS Properties Brand Colors */
:root {{
    --osus-primary: {self.osus_colors['primary']};
    --osus-gold: {self.osus_colors['gold']};
    --osus-light-gold: {self.osus_colors['light_gold']};
    --osus-dark-gold: {self.osus_colors['dark_gold']};
    --osus-white: {self.osus_colors['white']};
    --osus-accent: {self.osus_colors['accent']};
    
    /* Transparency variants */
    --osus-primary-10: {self.osus_colors['primary']}1a;
    --osus-primary-20: {self.osus_colors['primary']}33;
    --osus-gold-10: {self.osus_colors['gold']}1a;
    --osus-gold-20: {self.osus_colors['gold']}33;
}}

"""
        return custom_properties + content

    def convert_to_bem_methodology(self, content):
        """Convert CSS classes to follow BEM methodology"""
        # Add BEM-style prefixes where missing
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            # Convert generic class names to BEM with o_ prefix
            if re.match(r'^\s*\.[a-z][a-z_-]*\s*{', line) and not line.strip().startswith('.o_'):
                class_name = re.search(r'\.([a-z][a-z_-]*)', line).group(1)
                if class_name not in ['btn', 'form', 'input', 'table']:  # Skip Bootstrap classes
                    line = line.replace(f'.{class_name}', f'.o_module_{class_name}')
                    updated_lines.append(f'/* Consider using BEM methodology: .o_module_name__{class_name} */')
            
            updated_lines.append(line)
        
        return '\n'.join(updated_lines)

    def modernize_css_patterns(self, content):
        """Modernize CSS patterns for better compatibility"""
        # Replace old color values with custom properties
        for color_name, color_value in self.osus_colors.items():
            if color_value in content:
                var_name = f'--osus-{color_name.replace("_", "-")}'
                content = content.replace(color_value, f'var({var_name})')
        
        # Add modern CSS features suggestions
        if 'display: flex' in content and 'gap:' not in content:
            content = content.replace(
                'display: flex;',
                'display: flex;\n    /* Consider adding gap: 1rem; for modern spacing */'
            )
        
        return content

    def reduce_important_usage(self, content):
        """Reduce excessive !important usage"""
        important_count = content.count('!important')
        if important_count > 3:
            # Add comment about reducing !important
            content = f"""/* 
WARNING: This file contains {important_count} !important declarations.
Consider refactoring to use more specific selectors instead.
*/
""" + content
        
        return content

    def process_module(self, module_path):
        """Process all JS and CSS files in a module"""
        print(f"\n🔄 Processing module: {module_path}")
        
        js_files = []
        css_files = []
        
        # Find all JS and CSS files
        static_path = os.path.join(module_path, 'static', 'src')
        if os.path.exists(static_path):
            for root, dirs, files in os.walk(static_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.js'):
                        js_files.append(file_path)
                    elif file.endswith(('.css', '.scss')):
                        css_files.append(file_path)
        
        # Update JavaScript files
        for js_file in js_files:
            try:
                self.update_javascript_to_modern_odoo17(js_file)
            except Exception as e:
                print(f"❌ Error updating {js_file}: {e}")
        
        # Update CSS files
        for css_file in css_files:
            try:
                self.update_css_to_modern_odoo17(css_file)
            except Exception as e:
                print(f"❌ Error updating {css_file}: {e}")

    def run_modern_syntax_update(self):
        """Run modern syntax update on all priority modules"""
        print("🚀 MODERN ODOO 17 SYNTAX UPDATER")
        print("=" * 50)
        
        priority_modules = [
            'account_payment_final',
            'order_status_override',
            'oe_sale_dashboard_17',
            'commission_ax',
            'enhanced_rest_api',
            'crm_executive_dashboard'
        ]
        
        for module in priority_modules:
            if os.path.exists(module):
                self.process_module(module)
        
        print(f"\n✅ Modern Syntax Update Complete!")
        print(f"📊 Total Updates Applied: {len(self.updates_applied)}")
        for update in self.updates_applied:
            print(f"   - {update}")
        
        return self.updates_applied

if __name__ == "__main__":
    updater = ModernSyntaxUpdater()
    updates = updater.run_modern_syntax_update()
