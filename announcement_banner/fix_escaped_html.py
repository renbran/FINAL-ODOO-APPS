#!/usr/bin/env python3
"""
Clean up HTML-escaped announcement messages
============================================
This script fixes announcements that have HTML code showing instead of formatted content.

Run this from Odoo shell:
    docker-compose exec odoo odoo shell -d osusproperties
    
Then paste this script
"""

import html
import re

def clean_announcement_messages():
    """Clean up HTML-escaped messages in announcements"""
    
    # Get all announcements
    announcements = env['announcement.banner'].search([])
    
    print(f"\n{'='*60}")
    print(f"Found {len(announcements)} announcement(s) to check")
    print(f"{'='*60}\n")
    
    fixed_count = 0
    
    for announcement in announcements:
        original_message = announcement.message
        
        # Check if message contains escaped HTML
        if original_message and ('&lt;' in original_message or '&gt;' in original_message):
            print(f"Fixing: {announcement.name}")
            print(f"  Before: {original_message[:100]}...")
            
            # Unescape HTML entities
            cleaned_message = html.unescape(original_message)
            
            # Update the announcement
            announcement.write({'message': cleaned_message})
            
            print(f"  After: {cleaned_message[:100]}...")
            print(f"  ✓ Fixed!\n")
            
            fixed_count += 1
        else:
            print(f"✓ OK: {announcement.name}")
    
    print(f"\n{'='*60}")
    print(f"Summary: Fixed {fixed_count} announcement(s)")
    print(f"{'='*60}\n")
    
    return fixed_count

# Run the cleanup
if __name__ == '__main__':
    fixed = clean_announcement_messages()
    print(f"\nTotal announcements fixed: {fixed}")
