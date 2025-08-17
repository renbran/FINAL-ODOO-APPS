#!/usr/bin/env python3
"""
Enhanced Burgundy Brand Validation for oe_sale_dashboard_17
Validates brand consistency across responsive charts and scorecards
"""

import os
import re
import json
from datetime import datetime

def validate_burgundy_branding():
    """Validate burgundy brand implementation across the dashboard"""
    
    results = {
        'validation_time': datetime.now().isoformat(),
        'brand_colors': {
            'primary_burgundy': '#800020',
            'secondary_burgundy': '#A0002A', 
            'deep_burgundy': '#600018',
            'gold_accent': '#FFD700',
            'dark_gold': '#B8860B'
        },
        'validations': {},
        'summary': {'total_checks': 0, 'passed': 0, 'failed': 0}
    }
    
    dashboard_path = 'oe_sale_dashboard_17'
    
    print("🎨 Enhanced Burgundy Brand Validation")
    print("=" * 50)
    
    # 1. Validate JavaScript Chart Colors
    js_file = f'{dashboard_path}/static/src/js/enhanced_sales_dashboard.js'
    results['validations']['javascript_colors'] = validate_js_chart_colors(js_file)
    
    # 2. Validate CSS Brand Classes
    css_file = f'{dashboard_path}/static/src/css/enhanced_dashboard.css'
    results['validations']['css_branding'] = validate_css_branding(css_file)
    
    # 3. Validate XML Template Brand Elements
    xml_file = f'{dashboard_path}/static/src/xml/enhanced_sales_dashboard.xml'
    results['validations']['xml_branding'] = validate_xml_branding(xml_file)
    
    # 4. Validate Responsive Design
    results['validations']['responsive_design'] = validate_responsive_design(css_file)
    
    # Calculate summary
    for category, validation in results['validations'].items():
        results['summary']['total_checks'] += len(validation.get('checks', []))
        results['summary']['passed'] += len([c for c in validation.get('checks', []) if c.get('status') == 'PASS'])
        results['summary']['failed'] += len([c for c in validation.get('checks', []) if c.get('status') == 'FAIL'])
    
    # Print summary
    print_validation_summary(results)
    
    # Save results
    with open('burgundy_brand_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def validate_js_chart_colors(js_file):
    """Validate JavaScript chart color implementations"""
    validation = {
        'file': js_file,
        'checks': [],
        'status': 'CHECKING'
    }
    
    if not os.path.exists(js_file):
        validation['checks'].append({
            'test': 'File exists',
            'status': 'FAIL',
            'message': 'JavaScript file not found'
        })
        return validation
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for burgundy color usage
    burgundy_patterns = [
        r'#800020',  # Primary burgundy
        r'#A0002A',  # Secondary burgundy
        r'#600018',  # Deep burgundy
        r'rgba\(128,\s*0,\s*32',  # RGBA burgundy
    ]
    
    burgundy_found = 0
    for pattern in burgundy_patterns:
        matches = re.findall(pattern, content)
        burgundy_found += len(matches)
    
    validation['checks'].append({
        'test': 'Burgundy colors in charts',
        'status': 'PASS' if burgundy_found >= 10 else 'FAIL',
        'message': f'Found {burgundy_found} burgundy color references',
        'expected': '>=10 burgundy color uses'
    })
    
    # Check for gold accent usage
    gold_patterns = [
        r'#FFD700',  # Gold
        r'#B8860B',  # Dark gold
        r'rgba\(255,\s*215,\s*0',  # RGBA gold
    ]
    
    gold_found = 0
    for pattern in gold_patterns:
        matches = re.findall(pattern, content)
        gold_found += len(matches)
    
    validation['checks'].append({
        'test': 'Gold accent colors in charts',
        'status': 'PASS' if gold_found >= 5 else 'FAIL',
        'message': f'Found {gold_found} gold accent references',
        'expected': '>=5 gold accent uses'
    })
    
    # Check for hover effects with brand colors
    hover_effects = [
        'hoverBackgroundColor',
        'hoverBorderColor',
        'hoverBorderWidth'
    ]
    
    hover_found = sum(1 for effect in hover_effects if effect in content)
    validation['checks'].append({
        'test': 'Interactive hover effects',
        'status': 'PASS' if hover_found >= 2 else 'FAIL',
        'message': f'Found {hover_found}/3 hover effect types',
        'expected': 'Hover effects on charts'
    })
    
    return validation

def validate_css_branding(css_file):
    """Validate CSS brand implementation"""
    validation = {
        'file': css_file,
        'checks': [],
        'status': 'CHECKING'
    }
    
    if not os.path.exists(css_file):
        validation['checks'].append({
            'test': 'File exists',
            'status': 'FAIL',
            'message': 'CSS file not found'
        })
        return validation
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for brand color classes
    brand_classes = [
        '.text-maroon',
        '.bg-maroon',
        '.text-gold',
        '.bg-gold',
        '.bg-light-maroon',
        '.bg-light-gold'
    ]
    
    brand_classes_found = sum(1 for cls in brand_classes if cls in content)
    validation['checks'].append({
        'test': 'Brand color classes',
        'status': 'PASS' if brand_classes_found >= 4 else 'FAIL',
        'message': f'Found {brand_classes_found}/{len(brand_classes)} brand classes',
        'expected': 'Brand utility classes defined'
    })
    
    # Check for enhanced KPI styling
    kpi_enhancements = [
        'kpi_card_enhanced',
        'kpi_icon_enhanced',
        'kpi_content_enhanced',
        'linear-gradient'
    ]
    
    kpi_found = sum(1 for enhancement in kpi_enhancements if enhancement in content)
    validation['checks'].append({
        'test': 'Enhanced KPI scorecard styling',
        'status': 'PASS' if kpi_found >= 3 else 'FAIL',
        'message': f'Found {kpi_found}/{len(kpi_enhancements)} KPI enhancements',
        'expected': 'Enhanced scorecard styling'
    })
    
    # Check for chart wrapper styling
    chart_styling = [
        'chart_wrapper',
        'box-shadow',
        'border-radius',
        'background: linear-gradient'
    ]
    
    chart_found = sum(1 for style in chart_styling if style in content)
    validation['checks'].append({
        'test': 'Enhanced chart container styling',
        'status': 'PASS' if chart_found >= 3 else 'FAIL',
        'message': f'Found {chart_found}/{len(chart_styling)} chart style features',
        'expected': 'Professional chart containers'
    })
    
    return validation

def validate_xml_branding(xml_file):
    """Validate XML template brand elements"""
    validation = {
        'file': xml_file,
        'checks': [],
        'status': 'CHECKING'
    }
    
    if not os.path.exists(xml_file):
        validation['checks'].append({
            'test': 'File exists',
            'status': 'FAIL',
            'message': 'XML template file not found'
        })
        return validation
    
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for brand class usage
    brand_usage = [
        'text-maroon',
        'kpi_card_enhanced',
        'kpi_icon_enhanced',
        'chart_wrapper'
    ]
    
    brand_found = sum(1 for usage in brand_usage if usage in content)
    validation['checks'].append({
        'test': 'Brand classes in template',
        'status': 'PASS' if brand_found >= 2 else 'FAIL',
        'message': f'Found {brand_found}/{len(brand_usage)} brand class uses',
        'expected': 'Brand classes applied in template'
    })
    
    # Check for responsive grid
    responsive_elements = [
        'col-xl-',
        'col-lg-',
        'col-md-',
        'col-sm-'
    ]
    
    responsive_found = sum(1 for element in responsive_elements if element in content)
    validation['checks'].append({
        'test': 'Responsive grid classes',
        'status': 'PASS' if responsive_found >= 3 else 'FAIL',
        'message': f'Found {responsive_found}/{len(responsive_elements)} responsive grid types',
        'expected': 'Bootstrap responsive grid'
    })
    
    return validation

def validate_responsive_design(css_file):
    """Validate responsive design implementation"""
    validation = {
        'file': css_file,
        'checks': [],
        'status': 'CHECKING'
    }
    
    if not os.path.exists(css_file):
        validation['checks'].append({
            'test': 'File exists',
            'status': 'FAIL',
            'message': 'CSS file not found'
        })
        return validation
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for media queries
    media_queries = re.findall(r'@media[^{]+{', content)
    validation['checks'].append({
        'test': 'Responsive media queries',
        'status': 'PASS' if len(media_queries) >= 3 else 'FAIL',
        'message': f'Found {len(media_queries)} media queries',
        'expected': '>=3 responsive breakpoints'
    })
    
    # Check for mobile-first approach
    mobile_patterns = [
        'max-width.*576px',
        'max-width.*768px',
        'max-width.*992px',
        'max-width.*1200px'
    ]
    
    mobile_found = sum(1 for pattern in mobile_patterns if re.search(pattern, content))
    validation['checks'].append({
        'test': 'Mobile-first breakpoints',
        'status': 'PASS' if mobile_found >= 2 else 'FAIL',
        'message': f'Found {mobile_found}/4 standard breakpoints',
        'expected': 'Mobile-first responsive design'
    })
    
    # Check for flexible layouts
    flex_features = [
        'display: flex',
        'flex-direction',
        'flex-wrap',
        'justify-content',
        'align-items'
    ]
    
    flex_found = sum(1 for feature in flex_features if feature in content)
    validation['checks'].append({
        'test': 'Flexible layout properties',
        'status': 'PASS' if flex_found >= 3 else 'FAIL',
        'message': f'Found {flex_found}/{len(flex_features)} flex properties',
        'expected': 'Modern CSS layout'
    })
    
    return validation

def print_validation_summary(results):
    """Print validation summary"""
    print("\\n📊 Validation Summary")
    print("-" * 30)
    print(f"Total Checks: {results['summary']['total_checks']}")
    print(f"✅ Passed: {results['summary']['passed']}")
    print(f"❌ Failed: {results['summary']['failed']}")
    
    success_rate = (results['summary']['passed'] / results['summary']['total_checks'] * 100) if results['summary']['total_checks'] > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\\n🎨 Brand Color Validation")
    print("-" * 30)
    for color, code in results['brand_colors'].items():
        print(f"{color.replace('_', ' ').title()}: {code}")
    
    print("\\n📝 Detailed Results")
    print("-" * 30)
    for category, validation in results['validations'].items():
        print(f"\\n{category.replace('_', ' ').title()}:")
        for check in validation.get('checks', []):
            status_emoji = "✅" if check['status'] == 'PASS' else "❌"
            print(f"  {status_emoji} {check['test']}: {check['message']}")

if __name__ == "__main__":
    validate_burgundy_branding()
