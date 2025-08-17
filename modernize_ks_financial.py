#!/usr/bin/env python3
"""
Comprehensive jQuery to Modern JS Converter for ks_dynamic_financial_report.js    # 9. Replace $(event.currentTarget).parent().attr() patterns
    content = re.sub(
        r'var total_pages = parseInt\(\$\(event\.currentTarget\)\.parent\(\)\.attr\(\'total_pages\'\)\);',
        'const totalPages = parseInt(event.currentTarget.parentElement.getAttribute(\'total_pages\'));',
        content
    )
    
    # 10. Replace complex jQuery navigation patterns
    content = re.sub(
        r'\$\(event\.currentTarget\)\.parent\(\)\.parent\(\)\.find\("\.ks_new_text"\)\[0\]\.innerText = ([^;]+);',
        r'const textElement = event.currentTarget.parentElement.parentElement.querySelector(".ks_new_text");\n                if (textElement) textElement.innerText = \1;',
        content
    )
    
    # 11. Replace $(ev).parent().attr() patterns
    content = re.sub(
        r'var offset = parseInt\(\$\(ev\)\.parent\(\)\.attr\(\'offset\'\)\);',
        'const offset = parseInt(ev.parentElement.getAttribute(\'offset\'));',
        content
    )
    
    # 12. Replace $(ev).next('tr').find('td') patterns
    content = re.sub(
        r'var td = \$\(ev\)\.next\(\'tr\'\)\.find\(\'td\'\);',
        'const nextRow = ev.nextElementSibling;\n            const td = nextRow ? nextRow.querySelectorAll(\'td\') : [];',
        content
    )
    
    # 13. Replace remaining $(selector) patterns with modern equivalents
    content = re.sub(
        r'\$\(([^)]+)\)\.([a-zA-Z_][a-zA-Z0-9_]*)\(',
        lambda m: f"this.modernJQuery({m.group(1)})?.{m.group(2)}(",
        content
    )les all jQuery patterns and converts them to modern DOM API calls
"""

import re
import sys

def modernize_jquery_patterns(content):
    """Convert all jQuery patterns to modern JavaScript"""
    
    # Helper function for creating elements from HTML
    helper_function = '''
    /**
     * Helper method to create DOM elements from HTML string
     */
    createElementFromHTML(htmlString) {
        const template = document.createElement('template');
        template.innerHTML = htmlString.trim();
        return template.content.firstChild;
    }
    
    /**
     * Helper method to safely query elements
     */
    safeQuerySelector(selector) {
        try {
            return document.querySelector(selector);
        } catch (e) {
            console.warn('Invalid selector:', selector);
            return null;
        }
    }
    
    /**
     * Helper method to safely query all elements
     */
    safeQuerySelectorAll(selector) {
        try {
            return document.querySelectorAll(selector);
        } catch (e) {
            console.warn('Invalid selector:', selector);
            return [];
        }
    }
    
    /**
     * Modern jQuery replacement helper
     */
    modernJQuery(selector) {
        // Handle different selector types
        if (typeof selector === 'string') {
            return this.safeQuerySelector(selector);
        } else if (selector && selector.nodeType) {
            // Already a DOM element
            return selector;
        }
        return null;
    }'''
    
    # 1. Replace pager jQuery pattern
    content = re.sub(
        r"\$\('\.ks_pager'\)\.find\('\.ks_load_next'\)\.addClass\('ks_event_offer_list'\);",
        """const ksPager = document.querySelector('.ks_pager');
                    if (ksPager) {
                        const ksLoadNext = ksPager.querySelector('.ks_load_next');
                        if (ksLoadNext) {
                            ksLoadNext.classList.add('ks_event_offer_list');
                        }
                    }""",
        content
    )
    
    # 2. Replace jQuery element creation patterns
    content = re.sub(
        r'this\.\$ks_buttons = \$\((.*?)\);',
        r'this.ksButtonsElement = this.createElementFromHTML(\1);',
        content
    )
    
    content = re.sub(
        r'this\.\$ks_searchview_buttons = \$\((.*?)\);',
        r'this.ksSearchviewButtonsElement = this.createElementFromHTML(\1);',
        content
    )
    
    # 3. Replace $('.o_filter_menu').removeClass('ks_d_block')
    content = re.sub(
        r"\$\('\.o_filter_menu'\)\.removeClass\('ks_d_block'\)",
        "const filterMenu = document.querySelector('.o_filter_menu');\n             if (filterMenu) filterMenu.classList.remove('ks_d_block')",
        content
    )
    
    # 4. Replace $(ev).data('bsPartnerId') patterns
    content = re.sub(
        r'var partner_id = \$\(ev\)\.data\(\'bsPartnerId\'\);',
        'const partnerId = ev.currentTarget.dataset.bsPartnerId;',
        content
    )
    
    # 5. Replace $(event.currentTarget).hasClass() patterns
    content = re.sub(
        r'\$\(event\.currentTarget\)\.hasClass\(\'([^\']+)\'\)',
        r'event.currentTarget.classList.contains(\'\1\')',
        content
    )
    
    # 6. Replace $(event.currentTarget).parent().attr() patterns
    content = re.sub(
        r'var offset = parseInt\(\$\(event\.currentTarget\)\.parent\(\)\.attr\(\'offset\'\)\);',
        'const offset = parseInt(event.currentTarget.parentElement.getAttribute(\'offset\'));',
        content
    )
    
    content = re.sub(
        r'\$\(event\.currentTarget\)\.parent\(\)\.attr\(\'offset\', offset\)',
        'event.currentTarget.parentElement.setAttribute(\'offset\', offset)',
        content
    )
    
    # 7. Replace general jQuery selectors with modern equivalents
    content = re.sub(
        r'\$\(\'([^\']+)\'\)\.([a-zA-Z]+)\(',
        lambda m: f"this.safeQuerySelector('{m.group(1)}')?.{m.group(2)}(",
        content
    )
    
    # 8. Replace commented jQuery patterns
    content = re.sub(
        r'//\s*self\.\$\(\'\.o_content\'\)\.html\(QWeb\.render\(.*?\)',
        '// Modern template rendering handled by OWL framework',
        content
    )
    
    # Add helper functions to the class
    if 'createElementFromHTML(' not in content:
        # Find the class definition and add helper methods
        class_match = re.search(r'(export class ksDynamicReportsWidget extends Component \{[^}]*setup\(\) \{[^}]*\}\s*)', content, re.DOTALL)
        if class_match:
            class_def = class_match.group(1)
            new_class_def = class_def + '\n' + helper_function + '\n'
            content = content.replace(class_def, new_class_def)
    
    return content

def main():
    """Main function to modernize the file"""
    file_path = "ks_dynamic_financial_report/static/src/js/ks_dynamic_financial_report.js"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Modernizing {file_path}...")
        modernized_content = modernize_jquery_patterns(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modernized_content)
        
        print("✅ Modernization completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
