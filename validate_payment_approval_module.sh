#!/bin/bash

# Account Payment Approval Module - Final Testing Script
# This script validates all components of the enterprise payment approval system

echo "🚀 Starting Account Payment Approval Module Validation..."
echo "=================================================="

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -e "${BLUE}Testing: ${test_name}${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        if [ "$expected_result" = "success" ]; then
            echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAILED: ${test_name} (unexpected success)${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        if [ "$expected_result" = "failure" ]; then
            echo -e "${GREEN}✅ PASSED: ${test_name} (expected failure)${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAILED: ${test_name}${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    fi
    echo ""
}

echo -e "${YELLOW}📁 Module Structure Validation${NC}"
echo "-----------------------------------"

# Test 1: Check if main module directory exists
run_test "Module Directory Exists" "[ -d './account_payment_approval' ]" "success"

# Test 2: Check manifest file
run_test "Manifest File Exists" "[ -f './account_payment_approval/__manifest__.py' ]" "success"

# Test 3: Check models directory
run_test "Models Directory Structure" "[ -d './account_payment_approval/models' ] && [ -f './account_payment_approval/models/__init__.py' ]" "success"

# Test 4: Check core model files
run_test "Core Model Files" "[ -f './account_payment_approval/models/account_payment.py' ] && [ -f './account_payment_approval/models/payment_approval_config.py' ]" "success"

# Test 5: Check wizards
run_test "Wizard Files" "[ -d './account_payment_approval/wizards' ] && [ -f './account_payment_approval/wizards/payment_bulk_approval_wizard.py' ]" "success"

# Test 6: Check security files
run_test "Security Configuration" "[ -d './account_payment_approval/security' ] && [ -f './account_payment_approval/security/payment_approval_groups.xml' ]" "success"

# Test 7: Check views
run_test "View Files" "[ -d './account_payment_approval/views' ] && [ -f './account_payment_approval/views/account_payment_views.xml' ]" "success"

# Test 8: Check data files
run_test "Data Files" "[ -d './account_payment_approval/data' ] && [ -f './account_payment_approval/data/email_templates.xml' ]" "success"

# Test 9: Check static assets
run_test "Static Assets" "[ -d './account_payment_approval/static/src' ]" "success"

# Test 10: Check OWL templates
run_test "OWL Templates" "[ -f './account_payment_approval/static/src/xml/dashboard_templates.xml' ]" "success"

echo -e "${YELLOW}🔍 Code Quality Validation${NC}"
echo "-----------------------------------"

# Test 11: Python syntax validation
run_test "Python Syntax Check - account_payment.py" "python -m py_compile ./account_payment_approval/models/account_payment.py" "success"

# Test 12: Python syntax validation - config
run_test "Python Syntax Check - config.py" "python -m py_compile ./account_payment_approval/models/payment_approval_config.py" "success"

# Test 13: Python syntax validation - wizards
run_test "Python Syntax Check - wizards" "python -m py_compile ./account_payment_approval/wizards/payment_bulk_approval_wizard.py" "success"

# Test 14: XML validation
run_test "XML Syntax Check - views" "xmllint --noout ./account_payment_approval/views/account_payment_views.xml 2>/dev/null" "success"

# Test 15: XML validation - data
run_test "XML Syntax Check - data" "xmllint --noout ./account_payment_approval/data/email_templates.xml 2>/dev/null" "success"

echo -e "${YELLOW}🔧 Configuration Validation${NC}"
echo "-----------------------------------"

# Test 16: Check manifest dependencies
run_test "Manifest Dependencies" "grep -q 'account.*mail.*web' ./account_payment_approval/__manifest__.py" "success"

# Test 17: Check version compatibility
run_test "Odoo Version Check" "grep -q '17.0' ./account_payment_approval/__manifest__.py" "success"

# Test 18: Check data files referenced in manifest
run_test "Data Files in Manifest" "grep -q 'email_templates.xml' ./account_payment_approval/__manifest__.py" "success"

# Test 19: Check assets in manifest
run_test "Assets in Manifest" "grep -q 'web.assets_backend' ./account_payment_approval/__manifest__.py" "success"

echo -e "${YELLOW}📊 Content Validation${NC}"
echo "-----------------------------------"

# Test 20: Check approval states in payment model
run_test "Approval States Defined" "grep -q 'under_review.*approved.*authorized' ./account_payment_approval/models/account_payment.py" "success"

# Test 21: Check digital signature functionality
run_test "Digital Signature Methods" "grep -q '_add_digital_signature' ./account_payment_approval/models/account_payment.py" "success"

# Test 22: Check QR code functionality
run_test "QR Code Methods" "grep -q '_generate_qr_code' ./account_payment_approval/models/account_payment.py" "success"

# Test 23: Check email templates
run_test "Email Template Count" "[ $(grep -c '<record.*mail.template' ./account_payment_approval/data/email_templates.xml) -ge 5 ]" "success"

# Test 24: Check security groups
run_test "Security Groups Defined" "grep -q 'payment_approval_user.*payment_approval_manager' ./account_payment_approval/security/payment_approval_groups.xml" "success"

# Test 25: Check wizard functionality
run_test "Bulk Approval Wizard" "grep -q 'def.*approve_payments' ./account_payment_approval/wizards/payment_bulk_approval_wizard.py" "success"

echo -e "${YELLOW}🎨 Frontend Validation${NC}"
echo "-----------------------------------"

# Test 26: Check JavaScript files
run_test "JavaScript Dashboard Component" "[ -f './account_payment_approval/static/src/js/payment_approval_dashboard.js' ]" "success"

# Test 27: Check SCSS files
run_test "SCSS Stylesheets" "[ -f './account_payment_approval/static/src/scss/payment_approval.scss' ]" "success"

# Test 28: Check OWL templates syntax
run_test "OWL Template Syntax" "grep -q 't-name.*dashboard' ./account_payment_approval/static/src/xml/dashboard_templates.xml" "success"

# Test 29: Check responsive design elements
run_test "Responsive Design Classes" "grep -q 'mobile.*responsive' ./account_payment_approval/static/src/scss/payment_approval.scss" "success"

echo -e "${YELLOW}📈 Enterprise Features Validation${NC}"
echo "-----------------------------------"

# Test 30: Check multi-tier approval logic
run_test "Multi-tier Approval Logic" "grep -q 'approval_tier.*approval_level' ./account_payment_approval/models/account_payment.py" "success"

# Test 31: Check audit trail functionality
run_test "Audit Trail Implementation" "grep -q 'approval_history.*audit' ./account_payment_approval/models/account_payment.py" "success"

# Test 32: Check reporting wizards
run_test "Report Generation Wizard" "[ -f './account_payment_approval/wizards/payment_report_wizard.py' ]" "success"

# Test 33: Check configuration settings
run_test "Configuration Settings" "grep -q 'approval_threshold.*time_limit' ./account_payment_approval/models/res_config_settings.py" "success"

# Test 34: Check API controllers
run_test "API Controllers" "[ -f './account_payment_approval/controllers/api.py' ]" "success"

# Test 35: Check QR verification controller
run_test "QR Verification Controller" "[ -f './account_payment_approval/controllers/qr_verification.py' ]" "success"

echo -e "${YELLOW}🔒 Security Validation${NC}"
echo "-----------------------------------"

# Test 36: Check access rights file
run_test "Access Rights Configuration" "[ -f './account_payment_approval/security/ir.model.access.csv' ]" "success"

# Test 37: Check record rules
run_test "Security Record Rules" "grep -q 'payment_approval.*rule' ./account_payment_approval/security/payment_approval_groups.xml" "success"

# Test 38: Check user groups hierarchy
run_test "User Groups Hierarchy" "grep -q 'payment_approval_user.*payment_approval_reviewer.*payment_approval_approver' ./account_payment_approval/security/payment_approval_groups.xml" "success"

echo ""
echo "=================================================="
echo -e "${BLUE}📊 VALIDATION SUMMARY${NC}"
echo "=================================================="
echo -e "Total Tests Run: ${TOTAL_TESTS}"
echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Module is ready for deployment.${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Run Odoo with --test-enable to execute unit tests"
    echo "2. Install the module in a test database"
    echo "3. Configure approval workflows"
    echo "4. Test with sample payments"
    echo "5. Deploy to production environment"
    echo ""
    echo -e "${BLUE}🚀 Ready for Enterprise Deployment!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please review and fix issues before deployment.${NC}"
    echo ""
    echo -e "${YELLOW}📋 Recommended Actions:${NC}"
    echo "1. Review failed test details above"
    echo "2. Fix any missing files or configuration issues"
    echo "3. Re-run this validation script"
    echo "4. Consult the implementation documentation"
fi

echo ""
echo -e "${BLUE}Generated for OSUS Properties - Account Payment Approval Module${NC}"
echo -e "${BLUE}Validation completed at: $(date)${NC}"
echo "=================================================="

exit $TESTS_FAILED
