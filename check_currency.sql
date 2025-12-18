-- Check active currencies in the system
SELECT 
    id,
    name,
    symbol,
    active,
    position
FROM res_currency
WHERE active = true
ORDER BY name;

-- Check company currency
SELECT 
    c.name as company_name,
    curr.name as currency_name,
    curr.symbol as currency_symbol
FROM res_company c
JOIN res_currency curr ON c.currency_id = curr.id;

-- Check if AED currency exists
SELECT 
    id,
    name,
    symbol,
    active,
    rounding
FROM res_currency
WHERE name = 'AED' OR name LIKE '%Dirham%';
