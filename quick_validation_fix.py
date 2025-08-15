#!/usr/bin/env python3
"""
Quick validation script for the account_move_enhanced_views.xml fix
"""

import xml.etree.ElementTree as ET
import os

def validate_account_move_views():
    """Validate the fixed account_move_enhanced_views.xml file"""
    
    file_path = 'account_payment_approval/views/account_move_enhanced_views.xml'
    
    print("üîç Validating account_move_enhanced_views.xml...")
    
    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        print("‚úÖ XML is valid and parseable")
        
        # Check each view record
        views_checked = 0
        for record in root.findall('.//record[@model="ir.ui.view"]'):
            view_id = record.get('id')
            print(f"\nüìã Checking view: {view_id}")
            views_checked += 1
            
            # Get model
            model_field = record.find('.//field[@name="model"]')
            if model_field is not None:
                model_name = model_field.text
                print(f"   Model: {model_name}")
                
                # Check XPath expressions
                arch = record.find('.//field[@name="arch"]')
                if arch is not None:
                    xpaths = arch.findall('.//xpath')
                    print(f"   XPaths found: {len(xpaths)}")
                    
                    for xpath in xpaths:
                        expr = xpath.get('expr')
                        position = xpath.get('position', 'inside')
                        print(f"   - {expr} (position: {position})")
                        
                        # Check for problematic patterns
                        if 'amount_group' in expr:
                            print(f"   ‚ö†Ô∏è  WARNING: amount_group pattern found!")
                        elif 'oe_button_box' in expr and model_name == 'account.move.line':
                            print(f"   ‚ö†Ô∏è  WARNING: button_box in move.line view!")
                        else:
                            print(f"   ‚úÖ XPath looks good")
        
        print(f"\n‚úÖ Validation complete! Checked {views_checked} views")
        return True
        
    except ET.ParseError as e:
        print(f"‚ùå XML Parse Error: {e}")
        return False
    except FileNotFoundError:
        print(f"‚ùå File not found: {file_path}")
        return False
    except Exception as e:
        print(f"‚ùå Unexpected error: {e}")
        return False

if __name__ == "__main__":
    validate_account_move_views()
