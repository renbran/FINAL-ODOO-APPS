#!/bin/bash

# Fix Duplicate Partners Shell Script
# This script connects to the Odoo container and runs the duplicate partner fix

echo "🔧 Starting duplicate partner fix..."
echo "========================================"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found"
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Odoo containers not running. Start with: docker-compose up -d"
    exit 1
fi

echo "📦 Connecting to Odoo container..."

# Run the fix in Odoo shell
docker-compose exec odoo python3 odoo-bin shell -d osuspro << 'EOF'
# Fix duplicate partners
try:
    print("🔍 Searching for duplicate partner names...")
    hr_employee = env['hr.employee']
    result = hr_employee.fix_existing_duplicate_partners()
    
    print("\n" + "="*60)
    print("DUPLICATE PARTNER FIX RESULTS")
    print("="*60)
    print(f"Duplicates found: {result['duplicates_found']}")
    print(f"Records fixed: {result['fixed_count']}")
    print(f"Message: {result['message']}")
    print("="*60)
    
    if result['fixed_count'] > 0:
        env.cr.commit()
        print("✅ Changes committed to database")
    else:
        print("ℹ️  No duplicates found or no changes needed")
    
    print("\n🎉 Duplicate partner fix completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    env.cr.rollback()
    print("🔄 Transaction rolled back")

EOF

echo "========================================"
echo "✅ Duplicate partner fix process completed"
echo ""
echo "💡 You can now proceed with employee imports"
echo "   The system will handle any new duplicates automatically"
