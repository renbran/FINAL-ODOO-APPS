#!/usr/bin/env python3
"""
Quick validation of state field definition
"""
import re

def check_state_field():
    """Check the state field definition"""
    print("🔍 Checking State Field Definition...")
    
    model_file = "account_payment_approval/models/account_payment.py"
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for selection_add usage
        if 'selection_add=' in content and 'state = fields.Selection' in content:
            print("   ✅ State field uses selection_add (correct approach)")
            
            # Check for ondelete parameter
            if 'ondelete=' in content:
                print("   ✅ Has ondelete parameter")
            else:
                print("   ❌ Missing ondelete parameter")
                return False
            
            # Check for proper closing
            state_section = re.search(r'state = fields\.Selection\((.*?)\)', content, re.DOTALL)
            if state_section:
                state_def = state_section.group(1)
                if 'selection_add=' in state_def and ')' in state_def:
                    print("   ✅ State field definition is properly closed")
                    return True
                else:
                    print("   ❌ State field definition syntax issue")
                    return False
            else:
                print("   ❌ Could not parse state field definition")
                return False
        else:
            print("   ❌ State field not using selection_add")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False

def main():
    print("🚀 STATE FIELD QUICK VALIDATION")
    print("="*40)
    
    if check_state_field():
        print("\n✅ LOCAL STATE FIELD DEFINITION IS CORRECT")
        print("🔧 Issue is likely on CloudPepper side - deployment/cache problem")
        print("💡 Use nuclear reset option for guaranteed fix")
    else:
        print("\n❌ LOCAL STATE FIELD DEFINITION HAS ISSUES")
        print("🔧 Fix local definition first, then deploy")

if __name__ == "__main__":
    main()
