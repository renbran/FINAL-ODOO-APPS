#!/usr/bin/env python3
"""
Script to find and fix cron jobs with invalid interval_type
"""

import sys
import os

def find_cron_issues():
    """Find cron job lines with invalid interval_type"""
    dump_file = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final\custom\dump.sql"
    
    if not os.path.exists(dump_file):
        print("Dump file not found!")
        return
    
    print("Searching for problematic cron jobs...")
    
    try:
        with open(dump_file, 'r', encoding='utf-8') as f:
            in_cron_section = False
            line_num = 0
            
            for line in f:
                line_num += 1
                
                # Start of cron data section
                if "COPY public.ir_cron" in line and "FROM stdin" in line:
                    in_cron_section = True
                    print(f"Found cron section at line {line_num}")
                    continue
                
                # End of cron data section
                if in_cron_section and line.strip() == r"\.":
                    in_cron_section = False
                    print(f"End of cron section at line {line_num}")
                    break
                
                # Process cron data lines
                if in_cron_section and line.strip() and not line.startswith("--"):
                    fields = line.split('\t')
                    if len(fields) >= 10:  # Should have at least 10 fields based on schema
                        interval_type = fields[9]  # interval_type is the 10th field (0-indexed)
                        
                        # Check for invalid interval_type
                        if interval_type in ['\\N', 'NULL', '', 'None']:
                            print(f"FOUND PROBLEMATIC CRON at line {line_num}:")
                            print(f"  ID: {fields[0] if len(fields) > 0 else 'N/A'}")
                            print(f"  Name: {fields[8] if len(fields) > 8 else 'N/A'}")
                            print(f"  Interval Type: {interval_type}")
                            print(f"  Interval Number: {fields[3] if len(fields) > 3 else 'N/A'}")
                            print(f"  Active: {fields[10] if len(fields) > 10 else 'N/A'}")
                            print("---")
                            
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    find_cron_issues()
