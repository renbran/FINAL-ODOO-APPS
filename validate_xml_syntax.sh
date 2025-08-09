#!/bin/bash
# XML Validation Script for Account Payment Final
# This script checks all XML files for syntax errors

echo "🔍 XML Syntax Validation for Account Payment Final"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find all XML files in the module
xml_files=$(find account_payment_final -name "*.xml" -type f)

echo "📁 Found XML files:"
echo "$xml_files"
echo ""

error_count=0
success_count=0

# Validate each XML file
for file in $xml_files; do
    echo -n "Checking $file... "
    
    # Use xmllint to validate XML syntax
    if command -v xmllint &> /dev/null; then
        if xmllint --noout "$file" 2>/dev/null; then
            echo -e "${GREEN}✅ VALID${NC}"
            ((success_count++))
        else
            echo -e "${RED}❌ INVALID${NC}"
            echo -e "${YELLOW}Error details:${NC}"
            xmllint --noout "$file" 2>&1 | head -3
            echo ""
            ((error_count++))
        fi
    else
        # Fallback: basic Python XML validation
        python3 -c "
import xml.etree.ElementTree as ET
try:
    ET.parse('$file')
    print('✅ VALID')
except ET.ParseError as e:
    print('❌ INVALID')
    print(f'Error: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️  Cannot validate: {e}')
" && ((success_count++)) || ((error_count++))
    fi
done

echo ""
echo "📊 Validation Summary:"
echo "========================"
echo -e "✅ Valid files: ${GREEN}$success_count${NC}"
echo -e "❌ Invalid files: ${RED}$error_count${NC}"

if [ $error_count -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All XML files are valid! Module ready for installation.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Found $error_count XML syntax errors. Please fix before installing.${NC}"
    exit 1
fi
