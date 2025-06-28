# Individual Commission Types Enhancement

## Overview
Enhanced the commission calculation system to support individual commission types for each party, providing maximum flexibility in commission calculations.

## Key Features

### Individual Commission Types
Each commission party now has its own calculation method dropdown:

**External Parties (Group A):**
- Broker Commission Type
- Referrer Commission Type  
- Cashback Commission Type
- Other External Commission Type

**Internal Parties (Group B):**
- Agent 1 Commission Type
- Agent 2 Commission Type
- Manager Commission Type
- Director Commission Type

### Calculation Methods (Per Party)
1. **Based on Price Unit**: Commission calculated on sum of (line price × quantity)
2. **Based on Untaxed Total**: Commission calculated on order subtotal
3. **Fixed Amount**: Enter a fixed commission amount (not percentage-based)

## Implementation Details

### Model Changes (`commission_ax/models/sale_order.py`)
- Added 8 new selection fields for individual commission types
- Updated `_compute_commission_totals()` method with per-party calculation logic
- Refactored all onchange methods to use individual commission types
- Enhanced calculation helper function to support all three methods per party

### View Changes (`commission_ax/views/sale_order.xml`)
- Added commission type dropdown for each party
- Added helpful tooltips explaining calculation methods
- Hide rate field when "Fixed Amount" is selected
- Enhanced field labels and descriptions

### User Experience Improvements
- **Smart Field Visibility**: Rate fields hide when Fixed Amount is selected
- **Contextual Help**: Tooltips explain each calculation method
- **Auto-calculation**: Real-time calculation based on selected method
- **Visual Feedback**: Color-coded fields and decorations

## Usage Examples

### Example 1: Mixed Commission Types
- **Broker**: 5% of Untaxed Total
- **Referrer**: Fixed Amount of $500
- **Agent 1**: 3% of Price Unit Total
- **Manager**: 2% of Untaxed Total

### Example 2: All Fixed Amount
- **Broker**: Fixed $1,000
- **Agent 1**: Fixed $300
- **Manager**: Fixed $200
- **Director**: Fixed $150

### Example 3: Price Unit Based
- **Agent 1**: 4% of Price Unit Total (useful for quantity-based commissions)
- **Agent 2**: 2% of Price Unit Total
- **Manager**: 3% of Untaxed Total (different base)

## Benefits

1. **Maximum Flexibility**: Each party can have different calculation methods
2. **Business Logic Support**: Supports various commission structures
3. **User-Friendly**: Clear interface with helpful guidance
4. **Real-time Calculation**: Immediate feedback on commission changes
5. **Mixed Structures**: Combine percentage and fixed amount commissions

## Technical Implementation

### Calculation Logic
```python
def calculate_commission(rate, amount, commission_type):
    if commission_type == 'fixed_amount':
        return amount or 0
    elif commission_type == 'price_unit':
        return (rate / 100.0 * base_amount_price_unit) if rate else (amount or 0)
    else:  # untaxed_total
        return (rate / 100.0 * base_amount_untaxed) if rate else (amount or 0)
```

### Onchange Methods
Each party has dedicated onchange methods that:
- Calculate based on the party's specific commission type
- Use appropriate base amount (price unit total vs untaxed total)
- Handle fixed amount scenarios correctly

## Migration Notes

### Existing Data
- All existing commissions will default to 'untaxed_total' method
- No data loss or calculation changes for existing records
- Backward compatibility maintained

### Configuration
- Default commission method remains as fallback
- Individual types can be set independently
- Global method still available for bulk configuration

This enhancement provides unprecedented flexibility in commission calculations while maintaining ease of use and backward compatibility.
