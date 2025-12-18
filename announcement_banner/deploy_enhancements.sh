#!/bin/bash
# Announcement Banner Enhancement Deployment Script

set -e

echo "🎨 Deploying Announcement Banner Enhancements..."
echo "=================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Changes being deployed:${NC}"
echo "  1. Enhanced title contrast and readability"
echo "  2. Fixed HTML content sanitization"
echo "  3. Improved WYSIWYG editor configuration"
echo ""

# Step 1: Check if Odoo container is running
echo -e "${YELLOW}🔍 Checking Odoo container status...${NC}"
if ! docker-compose ps | grep -q "odoo.*Up"; then
    echo -e "${RED}❌ Odoo container is not running. Starting services...${NC}"
    docker-compose up -d
    sleep 10
else
    echo -e "${GREEN}✅ Odoo container is running${NC}"
fi
echo ""

# Step 2: Update the module
echo -e "${YELLOW}📦 Updating announcement_banner module...${NC}"
docker-compose exec -T odoo odoo --update=announcement_banner --stop-after-init -d odoo

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Module updated successfully${NC}"
else
    echo -e "${RED}❌ Module update failed. Check logs for details.${NC}"
    echo ""
    echo "View logs with: docker-compose logs -f odoo"
    exit 1
fi
echo ""

# Step 3: Restart Odoo
echo -e "${YELLOW}🔄 Restarting Odoo service...${NC}"
docker-compose restart odoo

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Odoo restarted successfully${NC}"
else
    echo -e "${RED}❌ Failed to restart Odoo${NC}"
    exit 1
fi
echo ""

# Step 4: Wait for Odoo to start
echo -e "${YELLOW}⏳ Waiting for Odoo to start (30 seconds)...${NC}"
sleep 30

# Step 5: Check logs for errors
echo -e "${YELLOW}🔍 Checking logs for errors...${NC}"
if docker-compose logs --tail=50 odoo | grep -i "ERROR\|CRITICAL" | grep -i "announcement"; then
    echo -e "${RED}⚠️  Errors detected in logs. Please review.${NC}"
    echo ""
    echo "View full logs with: docker-compose logs -f odoo"
else
    echo -e "${GREEN}✅ No errors detected in recent logs${NC}"
fi
echo ""

# Step 6: Summary
echo "=================================================="
echo -e "${GREEN}✨ Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "📝 Next Steps:"
echo "  1. Clear your browser cache (Ctrl+Shift+Delete)"
echo "  2. Force refresh the page (Ctrl+F5)"
echo "  3. Test announcement creation with formatted content"
echo "  4. Verify title readability and HTML rendering"
echo ""
echo "📊 Module Information:"
echo "  • Module: announcement_banner"
echo "  • Version: 17.0.1.0.2"
echo "  • Status: Updated"
echo ""
echo "🔗 Useful Commands:"
echo "  • View logs: docker-compose logs -f odoo"
echo "  • Restart: docker-compose restart odoo"
echo "  • Stop: docker-compose down"
echo ""
echo -e "${GREEN}🎉 Enhancements deployed successfully!${NC}"
echo ""
