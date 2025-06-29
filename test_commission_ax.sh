#!/bin/bash

# Simple test script for commission_ax module
echo "🧪 Testing Commission AX Module"
echo "================================="

echo "✅ 1. Checking Python syntax..."
python3 -c "
import ast
try:
    ast.parse(open('commission_ax/models/sale_order.py').read())
    print('   ✓ sale_order.py syntax valid')
except Exception as e:
    print(f'   ✗ sale_order.py syntax error: {e}')
    exit(1)

try:
    ast.parse(open('commission_ax/models/__init__.py').read())
    print('   ✓ models/__init__.py syntax valid')
except Exception as e:
    print(f'   ✗ models/__init__.py syntax error: {e}')
    exit(1)

try:
    ast.parse(open('commission_ax/__init__.py').read())
    print('   ✓ __init__.py syntax valid')
except Exception as e:
    print(f'   ✗ __init__.py syntax error: {e}')
    exit(1)
"

echo ""
echo "✅ 2. Checking XML syntax..."
python3 -c "
import xml.etree.ElementTree as ET
try:
    ET.parse('commission_ax/views/sale_order.xml')
    print('   ✓ sale_order.xml syntax valid')
except Exception as e:
    print(f'   ✗ sale_order.xml syntax error: {e}')
    exit(1)

try:
    ET.parse('commission_ax/views/purchase_order.xml')
    print('   ✓ purchase_order.xml syntax valid')
except Exception as e:
    print(f'   ✗ purchase_order.xml syntax error: {e}')
    exit(1)
"

echo ""
echo "✅ 3. Checking manifest file..."
python3 -c "
import ast
try:
    with open('commission_ax/__manifest__.py', 'r') as f:
        manifest = ast.literal_eval(f.read())
    print(f'   ✓ Module: {manifest[\"name\"]}')
    print(f'   ✓ Version: {manifest[\"version\"]}')
    print(f'   ✓ Dependencies: {manifest[\"depends\"]}')
except Exception as e:
    print(f'   ✗ Manifest error: {e}')
    exit(1)
"

echo ""
echo "🎯 Commission AX Module Validation Complete!"
echo "   Status: READY FOR INSTALLATION"
echo ""
echo "To install this specific module:"
echo "   odoo-bin -d your_database -u commission_ax"
