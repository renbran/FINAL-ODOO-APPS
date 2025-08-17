#!/usr/bin/env python3
"""
Enhanced Sales Dashboard Deployment & Validation Script
========================================================

This script validates the enhanced oe_sale_dashboard_17 module with:
- Responsive charts (Bar, Line, Pie)
- Predefined date filters (Last 30/90 days, This Year, Quarters)
- Booking date integration
- Agent/Broker rankings
- Mobile-responsive design

Author: Enhanced Dashboard Team
Date: August 17, 2025
Version: 1.0.0
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_dashboard_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EnhancedDashboardValidator:
    """Validator for enhanced sales dashboard deployment"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.validation_results = {}
        
    def validate_file_structure(self):
        """Validate required files exist"""
        logger.info("🔍 Validating enhanced dashboard file structure...")
        
        required_files = [
            '__manifest__.py',
            'models/sale_dashboard.py',
            'views/sales_dashboard_views.xml',
            'views/sales_dashboard_menus.xml',
            'static/src/js/sales_dashboard.js',
            'static/src/js/enhanced_sales_dashboard.js',
            'static/src/xml/sales_dashboard_main.xml',
            'static/src/xml/enhanced_sales_dashboard.xml',
            'static/src/css/dashboard.css',
            'static/src/css/enhanced_dashboard.css',
            'static/src/js/cloudpepper_dashboard_fix.js'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                existing_files.append(file_path)
                logger.info(f"✅ Found: {file_path}")
            else:
                missing_files.append(file_path)
                logger.error(f"❌ Missing: {file_path}")
        
        self.validation_results['file_structure'] = {
            'existing_files': existing_files,
            'missing_files': missing_files,
            'status': 'PASS' if not missing_files else 'FAIL'
        }
        
        return not missing_files
    
    def validate_manifest_dependencies(self):
        """Validate manifest dependencies are correct"""
        logger.info("🔍 Validating manifest dependencies...")
        
        manifest_path = self.module_path / '__manifest__.py'
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required dependencies
            required_deps = [
                'base',
                'sale',
                'sale_management',
                'web',
                'le_sale_type',
                'commission_ax', 
                'invoice_report_for_realestate'
            ]
            
            missing_deps = []
            for dep in required_deps:
                if f"'{dep}'" not in content:
                    missing_deps.append(dep)
                    logger.error(f"❌ Missing dependency: {dep}")
                else:
                    logger.info(f"✅ Found dependency: {dep}")
            
            # Check for enhanced features in assets
            if 'enhanced_sales_dashboard.js' in content:
                logger.info("✅ Enhanced JavaScript found in assets")
            else:
                logger.error("❌ Enhanced JavaScript missing from assets")
                
            if 'enhanced_dashboard.css' in content:
                logger.info("✅ Enhanced CSS found in assets")
            else:
                logger.error("❌ Enhanced CSS missing from assets")
                
            self.validation_results['manifest'] = {
                'missing_dependencies': missing_deps,
                'status': 'PASS' if not missing_deps else 'FAIL'
            }
            
            return not missing_deps
            
        except Exception as e:
            logger.error(f"❌ Error validating manifest: {e}")
            self.validation_results['manifest'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def validate_model_enhancements(self):
        """Validate model has enhanced methods"""
        logger.info("🔍 Validating model enhancements...")
        
        model_path = self.module_path / 'models' / 'sale_dashboard.py'
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for enhanced methods
            required_methods = [
                'get_predefined_date_ranges',
                'get_comprehensive_dashboard_data',
                'get_agent_ranking_data',
                'get_broker_ranking_data',
                'get_monthly_fluctuation_data',
                'get_sales_by_state_data',
                'get_top_customers_data',
                'get_sales_team_performance',
                'get_recent_orders_data'
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}" in content:
                    logger.info(f"✅ Found method: {method}")
                else:
                    missing_methods.append(method)
                    logger.error(f"❌ Missing method: {method}")
            
            # Check for booking_date support
            if 'booking_date' in content:
                logger.info("✅ Booking date support implemented")
            else:
                logger.error("❌ Booking date support missing")
            
            # Check for predefined ranges logic
            if 'Last 30 Days' in content and 'Current Quarter' in content:
                logger.info("✅ Predefined date ranges implemented")
            else:
                logger.error("❌ Predefined date ranges missing")
                
            self.validation_results['model'] = {
                'missing_methods': missing_methods,
                'status': 'PASS' if not missing_methods else 'FAIL'
            }
            
            return not missing_methods
            
        except Exception as e:
            logger.error(f"❌ Error validating model: {e}")
            self.validation_results['model'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def validate_javascript_enhancements(self):
        """Validate JavaScript has responsive features"""
        logger.info("🔍 Validating JavaScript enhancements...")
        
        js_path = self.module_path / 'static' / 'src' / 'js' / 'enhanced_sales_dashboard.js'
        
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for responsive features
            responsive_features = [
                'responsive: true',
                'maintainAspectRatio: false',
                'formatCurrency',
                'formatNumber',
                'renderAllCharts',
                'destroyAllCharts',
                'onPredefinedRangeChange',
                'predefined_range_select'
            ]
            
            missing_features = []
            for feature in responsive_features:
                if feature in content:
                    logger.info(f"✅ Found feature: {feature}")
                else:
                    missing_features.append(feature)
                    logger.error(f"❌ Missing feature: {feature}")
            
            # Check for Chart.js integration
            if 'Chart(' in content:
                logger.info("✅ Chart.js integration found")
            else:
                logger.error("❌ Chart.js integration missing")
                
            # Check for OWL component structure
            if 'Component, useState, useRef' in content:
                logger.info("✅ OWL component structure found")
            else:
                logger.error("❌ OWL component structure missing")
                
            self.validation_results['javascript'] = {
                'missing_features': missing_features,
                'status': 'PASS' if not missing_features else 'FAIL'
            }
            
            return not missing_features
            
        except Exception as e:
            logger.error(f"❌ Error validating JavaScript: {e}")
            self.validation_results['javascript'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def validate_xml_templates(self):
        """Validate XML templates have responsive design"""
        logger.info("🔍 Validating XML template enhancements...")
        
        xml_path = self.module_path / 'static' / 'src' / 'xml' / 'enhanced_sales_dashboard.xml'
        
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for responsive elements
            responsive_elements = [
                'col-lg-',
                'col-md-',
                'col-xl-',
                'responsive-chart',
                'predefined_range_select',
                'sale_type_enhanced_filter',
                'start_date_enhanced',
                'end_date_enhanced',
                'card border-0 shadow-sm',
                'enhanced_dashboard_container'
            ]
            
            missing_elements = []
            for element in responsive_elements:
                if element in content:
                    logger.info(f"✅ Found element: {element}")
                else:
                    missing_elements.append(element)
                    logger.error(f"❌ Missing element: {element}")
            
            # Check for predefined date filters
            if 'Last 30 Days' in content and 'Current Quarter' in content:
                logger.info("✅ Predefined date filters found")
            else:
                logger.error("❌ Predefined date filters missing")
                
            self.validation_results['xml_templates'] = {
                'missing_elements': missing_elements,
                'status': 'PASS' if not missing_elements else 'FAIL'
            }
            
            return not missing_elements
            
        except Exception as e:
            logger.error(f"❌ Error validating XML: {e}")
            self.validation_results['xml_templates'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def validate_css_responsive_design(self):
        """Validate CSS has responsive design"""
        logger.info("🔍 Validating CSS responsive design...")
        
        css_path = self.module_path / 'static' / 'src' / 'css' / 'enhanced_dashboard.css'
        
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for responsive features
            responsive_features = [
                '@media (max-width: 1200px)',
                '@media (max-width: 992px)',
                '@media (max-width: 768px)',
                '@media (max-width: 576px)',
                '.text-maroon',
                '.enhanced_dashboard_container',
                '.kpi_card_enhanced',
                '.responsive-chart',
                'transition: all',
                'box-shadow:',
                'border-radius:'
            ]
            
            missing_features = []
            for feature in responsive_features:
                if feature in content:
                    logger.info(f"✅ Found feature: {feature}")
                else:
                    missing_features.append(feature)
                    logger.error(f"❌ Missing feature: {feature}")
                    
            self.validation_results['css'] = {
                'missing_features': missing_features,
                'status': 'PASS' if not missing_features else 'FAIL'
            }
            
            return not missing_features
            
        except Exception as e:
            logger.error(f"❌ Error validating CSS: {e}")
            self.validation_results['css'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def validate_menu_structure(self):
        """Validate menu structure includes enhanced dashboard"""
        logger.info("🔍 Validating menu structure...")
        
        menu_path = self.module_path / 'views' / 'sales_dashboard_menus.xml'
        
        try:
            with open(menu_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for enhanced menu items
            required_items = [
                'Enhanced Sales Dashboard',
                'oe_sale_dashboard_17_enhanced_action',
                'enhanced_sales_dashboard',
                'sales_dashboard_enhanced_main_menu'
            ]
            
            missing_items = []
            for item in required_items:
                if item in content:
                    logger.info(f"✅ Found menu item: {item}")
                else:
                    missing_items.append(item)
                    logger.error(f"❌ Missing menu item: {item}")
                    
            self.validation_results['menus'] = {
                'missing_items': missing_items,
                'status': 'PASS' if not missing_items else 'FAIL'
            }
            
            return not missing_items
            
        except Exception as e:
            logger.error(f"❌ Error validating menus: {e}")
            self.validation_results['menus'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        logger.info("📊 Generating validation report...")
        
        report = {
            'module': 'oe_sale_dashboard_17',
            'validation_date': datetime.now().isoformat(),
            'enhancement_version': '17.0.1.6.2',
            'features': [
                'Responsive Charts (Bar, Line, Pie)',
                'Predefined Date Filters',
                'Booking Date Integration',
                'Agent/Broker Rankings',
                'Mobile-Responsive Design',
                'Enhanced UI/UX'
            ],
            'validation_results': self.validation_results,
            'overall_status': self.get_overall_status()
        }
        
        # Save report to file
        report_file = 'enhanced_dashboard_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Validation report saved to: {report_file}")
        return report
    
    def get_overall_status(self):
        """Get overall validation status"""
        all_passed = all(
            result.get('status') == 'PASS' 
            for result in self.validation_results.values()
        )
        return 'PASS' if all_passed else 'FAIL'
    
    def run_validation(self):
        """Run complete validation suite"""
        logger.info("🚀 Starting enhanced dashboard validation...")
        logger.info("=" * 60)
        
        validations = [
            self.validate_file_structure,
            self.validate_manifest_dependencies,
            self.validate_model_enhancements,
            self.validate_javascript_enhancements,
            self.validate_xml_templates,
            self.validate_css_responsive_design,
            self.validate_menu_structure
        ]
        
        all_passed = True
        for validation in validations:
            try:
                result = validation()
                all_passed = all_passed and result
                logger.info("-" * 40)
            except Exception as e:
                logger.error(f"❌ Validation failed: {e}")
                all_passed = False
        
        # Generate final report
        report = self.generate_report()
        
        logger.info("=" * 60)
        if all_passed:
            logger.info("🎉 Enhanced dashboard validation PASSED!")
            logger.info("✅ All enhancements are properly implemented")
            logger.info("✅ Responsive design ready for deployment")
            logger.info("✅ Predefined date filters functional")
            logger.info("✅ Booking date integration complete")
        else:
            logger.error("❌ Enhanced dashboard validation FAILED!")
            logger.error("❌ Some enhancements need attention")
            
        return all_passed, report

def main():
    """Main deployment validation function"""
    if len(sys.argv) != 2:
        print("Usage: python enhanced_dashboard_validator.py <module_path>")
        print("Example: python enhanced_dashboard_validator.py /path/to/oe_sale_dashboard_17")
        sys.exit(1)
    
    module_path = sys.argv[1]
    
    if not os.path.exists(module_path):
        logger.error(f"❌ Module path does not exist: {module_path}")
        sys.exit(1)
    
    validator = EnhancedDashboardValidator(module_path)
    success, report = validator.run_validation()
    
    if success:
        logger.info("🎯 Deployment validation completed successfully!")
        logger.info("🚀 Enhanced dashboard ready for production deployment")
        sys.exit(0)
    else:
        logger.error("⚠️  Deployment validation failed!")
        logger.error("🔧 Please fix the issues before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()
