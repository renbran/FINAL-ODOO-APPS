#!/usr/bin/env python3
"""
Detailed SCSS brace analyzer - finds exact location of brace mismatches
"""

import os
from pathlib import Path

def analyze_braces(file_path):
    """Analyze braces in a SCSS file and report mismatches with line numbers"""
    print(f"\n🔍 Analyzing braces in: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    open_braces = 0
    brace_stack = []
    
    for line_num, line in enumerate(lines, 1):
        # Remove strings and comments that might contain braces
        cleaned_line = line
        
        # Remove single-line comments
        if '//' in cleaned_line:
            cleaned_line = cleaned_line[:cleaned_line.index('//')]
        
        for char_pos, char in enumerate(cleaned_line):
            if char == '{':
                open_braces += 1
                brace_stack.append((line_num, char_pos, 'open'))
                print(f"  Line {line_num:3d}: Opening brace #{open_braces} - {line.strip()}")
            elif char == '}':
                if open_braces > 0:
                    open_braces -= 1
                    brace_stack.append((line_num, char_pos, 'close'))
                    print(f"  Line {line_num:3d}: Closing brace (now {open_braces} open) - {line.strip()}")
                else:
                    print(f"  ❌ Line {line_num:3d}: EXTRA closing brace! - {line.strip()}")
                    return False
    
    if open_braces > 0:
        print(f"  ❌ {open_braces} unclosed opening braces")
        # Show the last few opening braces
        open_only = [item for item in brace_stack if item[2] == 'open']
        if open_only:
            print("  Last opening braces:")
            for line_num, pos, _ in open_only[-open_braces:]:
                print(f"    Line {line_num}: {lines[line_num-1].strip()}")
        return False
    
    print(f"  ✅ All braces balanced!")
    return True

def main():
    """Main analyzer"""
    base_path = Path(__file__).parent / "account_payment_final" / "static" / "src" / "scss" / "components"
    target_file = base_path / "payment_widget.scss"
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return
    
    print("🔧 SCSS Brace Analyzer")
    print("=" * 50)
    
    success = analyze_braces(target_file)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 File is properly balanced!")
    else:
        print("❌ Brace mismatch detected!")

if __name__ == "__main__":
    main()
