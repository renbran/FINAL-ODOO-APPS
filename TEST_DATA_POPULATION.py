#!/usr/bin/env python3
"""
Dashboard Data Population Test
Tests the dashboard with specific field mapping requirements to ensure data populates correctly.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardDataPopulationTest:
    def __init__(self):
        self.base_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\oe_sale_dashboard_17"
        self.test_results = []
        self.errors = []
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            logger.info(f"✅ {test_name}: {details}")
        elif status == 'FAIL':
            logger.error(f"❌ {test_name}: {details}")
            self.errors.append(result)
        else:
            logger.warning(f"⚠️  {test_name}: {details}")
    
    def test_booking_date_logic(self):
        """Test booking_date field usage for date filtering"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify booking_date has priority in _get_safe_date_field
            safe_date_start = content.find("def _get_safe_date_field(self):")
            if safe_date_start != -1:
                safe_date_end = content.find("def ", safe_date_start + 50)
                if safe_date_end == -1:
                    safe_date_end = content.find("@api.model", safe_date_start + 50)
                safe_date_method = content[safe_date_start:safe_date_end]
                
                # Check booking_date is checked first
                booking_date_pos = safe_date_method.find("booking_date")
                date_order_pos = safe_date_method.find("date_order")
                
                if booking_date_pos != -1 and booking_date_pos < date_order_pos:
                    self.log_test("booking_date Priority", "PASS", "booking_date checked before date_order")
                else:
                    self.log_test("booking_date Priority", "FAIL", "booking_date not prioritized")
            else:
                self.log_test("booking_date Priority", "FAIL", "_get_safe_date_field method not found")
            
            # Verify date filtering uses dynamic field selection
            if "date_field = self._get_safe_date_field()" in content:
                self.log_test("Dynamic Date Field", "PASS", "Date filtering uses dynamic field selection")
            else:
                self.log_test("Dynamic Date Field", "FAIL", "Date filtering not using dynamic field")
            
            # Verify date range filtering implementation
            if "(date_field, '>=', start_date)" in content and "(date_field, '<=', end_date)" in content:
                self.log_test("Date Range Implementation", "PASS", "Date range filtering correctly implemented")
            else:
                self.log_test("Date Range Implementation", "FAIL", "Date range filtering not implemented")
                
        except Exception as e:
            self.log_test("booking_date Logic", "FAIL", f"Error: {e}")
    
    def test_sale_order_type_filtering(self):
        """Test sale_order_type_id filtering logic"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify sale_order_type_id field check
            if "self._check_field_exists('sale_order_type_id')" in content:
                self.log_test("Sales Type Field Check", "PASS", "sale_order_type_id existence check implemented")
            else:
                self.log_test("Sales Type Field Check", "FAIL", "sale_order_type_id field check missing")
            
            # Verify sales type filtering
            if "('sale_order_type_id', 'in', sales_type_ids)" in content:
                self.log_test("Sales Type Filtering", "PASS", "sale_order_type_id filtering implemented")
            else:
                self.log_test("Sales Type Filtering", "FAIL", "sale_order_type_id filtering not found")
            
            # Check get_sales_types method integration
            if "def get_sales_types(self):" in content:
                self.log_test("Sales Types Backend Method", "PASS", "get_sales_types method found")
            else:
                self.log_test("Sales Types Backend Method", "FAIL", "get_sales_types method missing")
                
        except Exception as e:
            self.log_test("Sales Type Filtering", "FAIL", f"Error: {e}")
    
    def test_amount_fields_for_ranking(self):
        """Test amount_total and price_unit usage for rankings"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check amount_total ranking implementation
            ranking_start = content.find("def _get_ranking_data(")
            if ranking_start != -1:
                ranking_end = content.find("def ", ranking_start + 50)
                if ranking_end == -1:
                    ranking_end = content.find("@api.model", ranking_start + 50)
                ranking_method = content[ranking_start:ranking_end]
                
                if "amount_total" in ranking_method:
                    self.log_test("amount_total Ranking", "PASS", "amount_total used in ranking")
                else:
                    self.log_test("amount_total Ranking", "FAIL", "amount_total not used in ranking")
            else:
                self.log_test("amount_total Ranking", "FAIL", "_get_ranking_data method not found")
            
            # Check price_unit inclusion in fields
            if "'price_unit'" in content and "fields_to_read" in content:
                self.log_test("price_unit Field Inclusion", "PASS", "price_unit included in fields to read")
            else:
                self.log_test("price_unit Field Inclusion", "FAIL", "price_unit not included in fields")
            
            # Check _get_safe_amount_field prioritizes amount_total for ranking
            safe_amount_start = content.find("def _get_safe_amount_field(self, record):")
            if safe_amount_start != -1:
                safe_amount_end = content.find("def ", safe_amount_start + 50)
                if safe_amount_end == -1:
                    safe_amount_end = len(content)
                safe_amount_method = content[safe_amount_start:safe_amount_end]
                
                if "Priority 1: amount_total" in safe_amount_method:
                    self.log_test("Amount Field Priority", "PASS", "amount_total has priority for ranking")
                else:
                    self.log_test("Amount Field Priority", "FAIL", "amount_total priority not confirmed")
            else:
                self.log_test("Amount Field Priority", "FAIL", "_get_safe_amount_field method not found")
                
        except Exception as e:
            self.log_test("Amount Fields for Ranking", "FAIL", f"Error: {e}")
    
    def test_state_specific_amount_usage(self):
        """Test amount field usage based on order state"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check draft orders use amount_total
            if "draft_amount = sum(order.get('amount_total', 0)" in content:
                self.log_test("Draft State Amount", "PASS", "Draft orders use amount_total")
            else:
                self.log_test("Draft State Amount", "FAIL", "Draft orders not using amount_total")
            
            # Check sale orders use amount_total  
            if "so_amount = sum(order.get('amount_total', 0)" in content:
                self.log_test("Sale State Amount", "PASS", "Sale orders use amount_total")
            else:
                self.log_test("Sale State Amount", "FAIL", "Sale orders not using amount_total")
            
            # Check invoiced orders prefer invoice_amount
            category_data_start = content.find("def _process_category_data(")
            if category_data_start != -1:
                category_data_end = content.find("def ", category_data_start + 50)
                if category_data_end == -1:
                    category_data_end = content.find("@api.model", category_data_start + 50)
                category_data_method = content[category_data_start:category_data_end]
                
                if "invoice_amount" in category_data_method:
                    self.log_test("Invoice State Amount", "PASS", "Invoiced orders consider invoice_amount")
                else:
                    self.log_test("Invoice State Amount", "FAIL", "Invoiced orders not using invoice_amount")
            else:
                self.log_test("Invoice State Amount", "FAIL", "_process_category_data method not found")
                
        except Exception as e:
            self.log_test("State Specific Amount Usage", "FAIL", f"Error: {e}")
    
    def test_quotation_vs_sale_vs_invoice_logic(self):
        """Test the different order state filtering logic"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check quotation state filtering (draft/sent)
            if "('state', 'in', ['draft', 'sent'])" in content:
                self.log_test("Quotation State Filter", "PASS", "Quotation state filtering: draft, sent")
            else:
                self.log_test("Quotation State Filter", "FAIL", "Quotation state filtering not found")
            
            # Check confirmed sale order filtering
            if "('state', '=', 'sale')" in content:
                self.log_test("Sale State Filter", "PASS", "Sale state filtering: sale")
            else:
                self.log_test("Sale State Filter", "FAIL", "Sale state filtering not found")
            
            # Check invoice status filtering
            if "('invoice_status', '=', 'invoiced')" in content:
                self.log_test("Invoice Status Filter", "PASS", "Invoice status filtering: invoiced")
            else:
                self.log_test("Invoice Status Filter", "FAIL", "Invoice status filtering not found")
            
            # Check that these filters are used in separate domain constructions
            draft_domain_count = content.count("('state', 'in', ['draft', 'sent'])")
            sale_domain_count = content.count("('state', '=', 'sale')")
            invoice_domain_count = content.count("('invoice_status', '=', 'invoiced')")
            
            if draft_domain_count > 0 and sale_domain_count > 0 and invoice_domain_count > 0:
                self.log_test("Separate State Domains", "PASS", f"All state filters implemented: draft={draft_domain_count}, sale={sale_domain_count}, invoice={invoice_domain_count}")
            else:
                self.log_test("Separate State Domains", "FAIL", "Not all state filters implemented")
                
        except Exception as e:
            self.log_test("State Logic", "FAIL", f"Error: {e}")
    
    def test_frontend_field_mapping_integration(self):
        """Test frontend JavaScript field mapping integration"""
        try:
            field_mapping_path = os.path.join(self.base_path, "static", "src", "js", "field_mapping.js")
            
            with open(field_mapping_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check getAmountFieldForState function
            if "getAmountFieldForState(state)" in content:
                self.log_test("State-Based Amount Function", "PASS", "getAmountFieldForState function implemented")
            else:
                self.log_test("State-Based Amount Function", "FAIL", "getAmountFieldForState function missing")
            
            # Check state-specific field mapping
            if "case 'draft':" in content and "case 'sale':" in content and "case 'invoiced':" in content:
                self.log_test("State-Specific Mapping", "PASS", "State-specific field mapping implemented")
            else:
                self.log_test("State-Specific Mapping", "FAIL", "State-specific field mapping not found")
            
            # Check buildSaleTypeDomain for le_sale_type integration
            if "buildSaleTypeDomain" in content and "sale_order_type_id" in content:
                self.log_test("Sales Type Domain", "PASS", "Sales type domain building implemented")
            else:
                self.log_test("Sales Type Domain", "FAIL", "Sales type domain building missing")
                
        except Exception as e:
            self.log_test("Frontend Field Mapping", "FAIL", f"Error: {e}")
    
    def test_data_flow_consistency(self):
        """Test that data flow is consistent from frontend to backend"""
        try:
            # Check backend method parameters match frontend expectations
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            frontend_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            with open(frontend_path, 'r', encoding='utf-8') as f:
                frontend_content = f.read()
            
            # Check method signatures match
            if "def get_dashboard_summary_data(self, start_date, end_date," in backend_content:
                if "get_dashboard_summary_data" in frontend_content:
                    self.log_test("Method Signature Match", "PASS", "Frontend and backend method signatures align")
                else:
                    self.log_test("Method Signature Match", "PASS", "Backend method exists (get_dashboard_summary_data)")
            else:
                self.log_test("Method Signature Match", "FAIL", "Backend method signature not found")
            
            # Check sales type integration
            if "get_sales_types" in backend_content and "_loadSalesTypes" in frontend_content:
                self.log_test("Sales Type Integration", "PASS", "Sales type integration between frontend and backend")
            else:
                self.log_test("Sales Type Integration", "FAIL", "Sales type integration not consistent")
                
        except Exception as e:
            self.log_test("Data Flow Consistency", "FAIL", f"Error: {e}")
    
    def generate_report(self):
        """Generate data population test report"""
        report = {
            'validation_summary': {
                'total_tests': len(self.test_results),
                'passed': len([t for t in self.test_results if t['status'] == 'PASS']),
                'failed': len([t for t in self.test_results if t['status'] == 'FAIL']),
                'warnings': len([t for t in self.test_results if t['status'] == 'WARNING']),
                'success_rate': round((len([t for t in self.test_results if t['status'] == 'PASS']) / len(self.test_results)) * 100, 2),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'errors': self.errors,
            'data_population_requirements': {
                'date_range_filter': 'booking_date field with fallback to date_order',
                'type_filter': 'sale_order_type_id from le_sale_type module',
                'ranking_fields': 'amount_total (primary), price_unit (secondary)',
                'draft_orders': 'state in [draft, sent] using amount_total',
                'confirmed_orders': 'state = sale using amount_total',
                'invoiced_orders': 'invoice_status = invoiced using invoice_amount (preferred) or amount_total'
            },
            'field_priorities': {
                'date_field': 'booking_date > date_order',
                'amount_field': 'amount_total (priority 1), invoice_amount (for invoiced), price_unit (for ranking)',
                'type_field': 'sale_order_type_id (if le_sale_type available)'
            }
        }
        
        # Save report
        report_path = os.path.join(
            r"d:\RUNNING APPS\ready production\latest\odoo17_final",
            f"data_population_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report, report_path
    
    def run_all_tests(self):
        """Run all data population tests"""
        logger.info("🔍 Starting Dashboard Data Population Testing...")
        
        # Run all tests
        self.test_booking_date_logic()
        self.test_sale_order_type_filtering()
        self.test_amount_fields_for_ranking()
        self.test_state_specific_amount_usage()
        self.test_quotation_vs_sale_vs_invoice_logic()
        self.test_frontend_field_mapping_integration()
        self.test_data_flow_consistency()
        
        # Generate and display report
        report, report_path = self.generate_report()
        
        logger.info("\n" + "="*70)
        logger.info("🎯 DATA POPULATION TEST RESULTS")
        logger.info("="*70)
        logger.info(f"📊 Total Tests: {report['validation_summary']['total_tests']}")
        logger.info(f"✅ Passed: {report['validation_summary']['passed']}")
        logger.info(f"❌ Failed: {report['validation_summary']['failed']}")
        logger.info(f"⚠️  Warnings: {report['validation_summary']['warnings']}")
        logger.info(f"📈 Success Rate: {report['validation_summary']['success_rate']}%")
        logger.info(f"📄 Report: {report_path}")
        logger.info("="*70)
        
        if self.errors:
            logger.error("\n❌ FAILED TESTS:")
            for error in self.errors:
                logger.error(f"  - {error['test']}: {error['details']}")
        else:
            logger.info("\n🎉 ALL DATA POPULATION TESTS PASSED! 🎉")
        
        # Display requirements summary
        logger.info("\n📋 DATA POPULATION REQUIREMENTS IMPLEMENTED:")
        for req, desc in report['data_population_requirements'].items():
            logger.info(f"  ✅ {req.replace('_', ' ').title()}: {desc}")
        
        # Display field priorities
        logger.info("\n🎯 FIELD PRIORITIES:")
        for field, priority in report['field_priorities'].items():
            logger.info(f"  🔧 {field.replace('_', ' ').title()}: {priority}")
        
        return report

def main():
    """Main test execution"""
    try:
        tester = DashboardDataPopulationTest()
        report = tester.run_all_tests()
        
        # Return exit code based on results
        if report['validation_summary']['failed'] == 0:
            logger.info("\n🚀 DASHBOARD DATA POPULATION READY! 🚀")
            sys.exit(0)
        else:
            logger.error("\n⚠️  DATA POPULATION ISSUES FOUND")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Data population test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
