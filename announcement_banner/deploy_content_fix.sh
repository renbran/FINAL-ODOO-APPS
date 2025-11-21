#!/bin/bash

# Message Content Display Fix - Deployment Script
# Version: 1.2.0
# Date: November 13, 2025

echo "================================================"
echo "Announcement Banner - Message Content Fix"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Cleaning Python cache...${NC}"
bash clean_cache.sh
echo -e "${GREEN}✓ Cache cleaned${NC}"
echo ""

echo -e "${YELLOW}Step 2: Restarting Odoo container...${NC}"
docker-compose restart odoo
echo -e "${GREEN}✓ Container restarted${NC}"
echo ""

echo -e "${YELLOW}Step 3: Waiting for Odoo to start (30 seconds)...${NC}"
sleep 30
echo -e "${GREEN}✓ Wait complete${NC}"
echo ""

echo -e "${YELLOW}Step 4: Updating announcement_banner module...${NC}"
docker-compose exec odoo odoo --update=announcement_banner --stop-after-init --no-http
echo -e "${GREEN}✓ Module updated${NC}"
echo ""

echo -e "${YELLOW}Step 5: Starting Odoo service...${NC}"
docker-compose up -d odoo
echo -e "${GREEN}✓ Service started${NC}"
echo ""

echo -e "${YELLOW}Step 6: Waiting for service to be ready (20 seconds)...${NC}"
sleep 20
echo -e "${GREEN}✓ Service ready${NC}"
echo ""

echo "================================================"
echo -e "${GREEN}Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Clear your browser cache (Ctrl+Shift+R)"
echo "2. Log in to Odoo"
echo "3. Create a test announcement with:"
echo "   - Text content (paragraphs, headings)"
echo "   - Images (upload via HTML editor)"
echo "   - Tables (use editor table tool)"
echo "   - Mixed content"
echo "4. Verify content displays correctly"
echo "5. Test on mobile device"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f odoo"
echo ""
echo "To check module status:"
echo "  Navigate to Apps > Announcement Banner"
echo ""
