#!/usr/bin/env python3
"""
Script to remove duplicate methods from sale_order.py
"""

import re

def remove_duplicate_methods():
    """Remove duplicate method definitions"""
    
    file_path = 'order_status_override/models/sale_order.py'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns to identify duplicate methods that need removal
    duplicate_removals = [
        # Remove second action_reject_order (around line 772)
        {
            'start_pattern': r'def action_reject_order\(self\):\s*"""Reject order - move back to draft with enhanced logic"""',
            'end_pattern': r'return True\s*def _create_workflow_activity',
            'replacement': 'def _create_workflow_activity'
        },
        # Remove third action_reject_order (around line 950)
        {
            'start_pattern': r'def action_reject_order\(self\):\s*"""Reject order and move to draft"""',
            'end_pattern': r'return True\s*def',
            'replacement': 'def'
        }
    ]
    
    # Apply removals
    for removal in duplicate_removals:
        pattern = removal['start_pattern'] + r'.*?' + removal['end_pattern']
        content = re.sub(pattern, removal['replacement'], content, flags=re.DOTALL)
    
    # Write back the cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Duplicate methods removed")

if __name__ == "__main__":
    remove_duplicate_methods()
