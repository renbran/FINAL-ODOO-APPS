#!/usr/bin/env python3
"""
Test script to verify dashboard number formatting
"""

def format_dashboard_value(value, precision=1):
    """Format numbers in compact notation (K, M, B)"""
    try:
        value = float(value)
        
        if value == 0:
            return "0"
            
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = f"{value / 1_000_000_000:.1f}"
            return f"{formatted} B"
        elif abs_value >= 1_000_000:
            formatted = f"{value / 1_000_000:.1f}"
            return f"{formatted} M"
        elif abs_value >= 1_000:
            formatted = f"{value / 1_000:.0f}"
            return f"{formatted} K"
        else:
            return f"{round(value)}"
    except (ValueError, TypeError):
        return str(value)

# Test cases based on user's example
test_values = [
    1251412,     # Should be 1.3 M
    48098047.1,  # Should be 48.1 M
    1106173.43,  # Should be 1.1 M
    92181.12,    # Should be 92 K
    999,         # Should be 999
    1000,        # Should be 1 K
    1234567890,  # Should be 1.2 B
    0,           # Should be 0
    -1500000,    # Should be -1.5 M
]

print("Dashboard Number Formatting Test")
print("=" * 40)

for value in test_values:
    formatted = format_dashboard_value(value)
    print(f"{value:>12} -> {formatted}")

print("\n✅ Compact formatting test completed")
