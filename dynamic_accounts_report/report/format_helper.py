# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################


def format_number(value):
    """
    Format a number with thousands separator and 2 decimal places.
    
    Args:
        value: The number to format (int, float, or string representation of a number)
        
    Returns:
        str: Formatted number string
    """
    try:
        if value is None or value == '':
            return '0.00'
        
        # Convert to float if it's a string
        if isinstance(value, str):
            value = float(value)
        
        # Format with 2 decimal places and thousands separator
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return '0.00'
