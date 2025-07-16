#!/usr/bin/env python3
"""
Test script to verify dashboard number formatting
"""

def format_dashboard_value(value, precision=1):
    """Format numbers in compact notation (K, M, B)"""
    try:
        value = float(value)
        
        if abs(value) >= 1000000000:
            return f"{value / 1000000000:.{precision}f} B"
        elif abs(value) >= 1000000:
            return f"{value / 1000000:.{precision}f} M"
        elif abs(value) >= 1000:
            return f"{value / 1000:.{precision}f} K"
        else:
            return f"{value:.{precision}f}"
    except (ValueError, TypeError):
        return str(value)

# Test cases based on user's example
test_values = [
    1251412,    # Should be 1.3 M
    48098047.1, # Should be 48.1 M
    999,        # Should be 999.0
    1000,       # Should be 1.0 K
    1234567890, # Should be 1.2 B
    0,          # Should be 0.0
    -1500000,   # Should be -1.5 M
]

print("Dashboard Number Formatting Test")
print("=" * 40)

for value in test_values:
    formatted = format_dashboard_value(value)
    print(f"{value:>12} -> {formatted}")

print("\n✅ Compact formatting test completed")
