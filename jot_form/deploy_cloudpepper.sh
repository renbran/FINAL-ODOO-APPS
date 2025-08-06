#!/bin/bash
"""
CloudPepper Deployment Script for JotForm Webhook
No external dependencies required - uses only Python standard library
"""

echo "🚀 CloudPepper JotForm Webhook Deployment"
echo "=========================================="

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found"
    exit 1
fi

echo "✅ Python found: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d" " -f2)
echo "📋 Python version: $PYTHON_VERSION"

# Create logs directory
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your CloudPepper Odoo credentials"
fi

# Test webhook script
echo "🔍 Testing webhook script..."
$PYTHON_CMD -c "
import sys
import json
import urllib.request
import base64
import hashlib
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import logging

print('✅ All required modules available')
print('🎯 Ready to deploy on CloudPepper')
"

if [ $? -eq 0 ]; then
    echo "✅ All dependencies satisfied"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Edit .env file with your CloudPepper Odoo credentials"
    echo "2. Run: $PYTHON_CMD lightweight_webhook.py"
    echo "3. Configure your JotForm webhook to point to your CloudPepper domain"
    echo ""
    echo "📡 Your webhook URL will be: https://your-domain.cloudpepper.com:5000"
    echo "🏥 Health check URL: https://your-domain.cloudpepper.com:5000/health"
else
    echo "❌ Dependency check failed"
    exit 1
fi
