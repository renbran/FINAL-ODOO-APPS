# OSUS Global PDF Template

This module applies the official OSUS Properties template design to all PDF reports globally.

## Features
- Automatic template application to all reports
- No per-report configuration needed
- Clean, modern implementation
- Compatible with all Odoo 17 report types
- Minimal CSS for proper content positioning

## Installation
1. Copy module to addons directory
2. Copy OSUS TEMPLATE.pdf to static/template/osus_template.pdf
3. Update app list
4. Install module

## Configuration
- Template is applied to all reports by default
- Can be disabled per report via "Apply OSUS Template" checkbox

## Technical Details
- Uses universal PyPDF2/pypdf compatibility layer
- Proper error handling and graceful degradation
- Returns original PDF if template fails
- Minimal overhead (0.5-1 second per report)
