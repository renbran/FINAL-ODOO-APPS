#!/bin/bash

# Sales Dashboard Module Validation Script
# Run this script to validate the module structure and dependencies

echo "=========================================="
echo "OSUS Executive Sales Dashboard Validation"
echo "=========================================="

MODULE_PATH="."
ERRORS=0

# Check required files
echo "Checking required module files..."

required_files=(
    "__manifest__.py"
    "__init__.py"
    "models/__init__.py"
    "models/sale_dashboard.py"
    "views/dashboard_views.xml"
    "views/dashboard_menu.xml"
    "security/ir.model.access.csv"
    "static/src/js/dashboard.js"
    "static/src/xml/dashboard_template.xml"
)

for file in "${required_files[@]}"; do
    if [ -f "$MODULE_PATH/$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Python syntax
echo ""
echo "Validating Python syntax..."
for py_file in $(find $MODULE_PATH -name "*.py" -not -path "*/tests/*"); do
    if python3 -m py_compile "$py_file" 2>/dev/null; then
        echo "✓ $py_file syntax OK"
    else
        echo "✗ $py_file syntax error"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check XML syntax
echo ""
echo "Validating XML syntax..."
for xml_file in $(find $MODULE_PATH -name "*.xml"); do
    if xmllint --noout "$xml_file" 2>/dev/null; then
        echo "✓ $xml_file syntax OK"
    else
        echo "✗ $xml_file syntax error"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check manifest structure
echo ""
echo "Validating manifest structure..."
if grep -q "'name':" "$MODULE_PATH/__manifest__.py" && \
   grep -q "'version':" "$MODULE_PATH/__manifest__.py" && \
   grep -q "'depends':" "$MODULE_PATH/__manifest__.py"; then
    echo "✓ Manifest structure OK"
else
    echo "✗ Manifest missing required fields"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED - Module is ready for deployment"
    echo "=========================================="
    exit 0
else
    echo "✗ $ERRORS ERRORS FOUND - Please fix before deployment"
    echo "=========================================="
    exit 1
fi
