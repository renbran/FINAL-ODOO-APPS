import xml.etree.ElementTree as ET
import os

os.chdir('account_payment_final')

def check_xpath_expressions(xml_file):
    print(f'\nChecking XPath in {xml_file}:')
    
    try:
        tree = ET.parse(xml_file)
        xpath_elements = tree.findall('.//xpath')
        
        safe_count = 0
        warning_count = 0
        
        for xpath_elem in xpath_elements:
            expr = xpath_elem.get('expr', '')
            
            if expr in ['//header', '//search', '//form', '//tree', '//sheet', '//notebook']:
                print(f'  ✅ Safe: {expr}')
                safe_count += 1
            elif 'field[@name=' in expr:
                print(f'  ✅ Field-based: {expr}')
                safe_count += 1
            elif 'button[@name=' in expr:
                print(f'  ✅ Button-based: {expr}')
                safe_count += 1
            else:
                print(f'  ⚠️ Review: {expr}')
                warning_count += 1
        
        print(f'  📊 {safe_count} safe, {warning_count} need review')
        
    except Exception as e:
        print(f'  ❌ Error: {e}')

view_files = [
    'views/account_payment_views.xml',
    'views/account_move_views.xml',
    'views/payment_verification_views.xml'
]

print('=== XPath Expression Analysis ===')
for xml_file in view_files:
    check_xpath_expressions(xml_file)
