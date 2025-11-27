-- Check current currency symbols
SELECT id, name, symbol, position FROM res_currency WHERE name IN ('AED', 'USD');

-- Option 1: Keep Arabic Dirham symbol (current)
-- د.إ

-- Option 2: Change to 'AED' text
UPDATE res_currency 
SET symbol = 'AED' 
WHERE name = 'AED' AND id = 129;

-- Verify the change
SELECT id, name, symbol, position FROM res_currency WHERE name = 'AED';

-- Check companies using this currency
SELECT 
    c.id,
    c.name as company_name,
    curr.name as currency_name,
    curr.symbol as currency_symbol,
    curr.position
FROM res_company c
JOIN res_currency curr ON c.currency_id = curr.id;
