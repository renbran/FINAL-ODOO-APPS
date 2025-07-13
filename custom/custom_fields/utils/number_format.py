from babel.numbers import format_decimal

def format_amount(amount, decimal_places=2):
    """
    Format a number with commas and fixed decimal places (e.g., 1,234.56)
    """
    if amount is None:
        return ''
    try:
        return format_decimal(amount, format=f'#,##0.{"0"*decimal_places}', locale='en_US')
    except Exception:
        return str(amount)
