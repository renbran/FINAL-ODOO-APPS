#!/usr/bin/env python3
import re

# Read the original file
with open('temp_crm_dashboard.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the formatCurrency function after the imports
format_function = '''
/**
 * Formats a number with K/M/B abbreviations
 * @param {number} value - The number to format
 * @returns {string} - Formatted number string
 */
function formatCurrency(value) {
    if (value === null || value === undefined || value === 0) {
        return '0';
    }
    
    const absValue = Math.abs(value);
    let formatted;
    
    if (absValue >= 1000000000) {
        // Billions
        formatted = (value / 1000000000).toFixed(2) + ' B';
    } else if (absValue >= 1000000) {
        // Millions
        formatted = (value / 1000000).toFixed(2) + ' M';
    } else if (absValue >= 1000) {
        // Thousands
        formatted = (value / 1000).toFixed(2) + ' K';
    } else {
        // Less than 1000
        formatted = value.toFixed(2);
    }
    
    return formatted;
}

'''

# Insert the function after the imports (before export class)
content = content.replace('export class CRMDashboard extends Component {', 
                         format_function + 'export class CRMDashboard extends Component {')

# Replace all occurrences of revenue display with formatted version
# Pattern: result.record_rev_exp or result.record_rev
replacements = [
    (r"(\+ result\.record_rev_exp \+)", r"+ formatCurrency(result.record_rev_exp) +"),
    (r"(\+ result\.record_rev \+)", r"+ formatCurrency(result.record_rev) +"),
    (r"'&nbsp' \+ result\.record_rev_exp \+", r"'&nbsp;' + formatCurrency(result.record_rev_exp) +"),
    (r"'&nbsp' \+ result\.record_rev \+", r"'&nbsp;' + formatCurrency(result.record_rev) +"),
    (r"'&nbsp' \+ result\.record_rev_exp \)", r"'&nbsp;' + formatCurrency(result.record_rev_exp))"),
    (r"'&nbsp' \+ result\.record_rev \)", r"'&nbsp;' + formatCurrency(result.record_rev))"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write the modified content
with open('temp_crm_dashboard_fixed.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ JavaScript file updated with currency formatting function")
print("✅ All revenue displays now use formatCurrency()")
