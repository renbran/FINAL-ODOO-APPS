@echo off
echo Emergency Database Fix for Payment Account Enhanced Module
echo ===========================================================

echo Step 1: Applying database schema fix...
docker-compose exec -T db psql -U odoo -d odoo -c "
-- Add voucher_footer_message column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_footer_message'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_footer_message TEXT DEFAULT 'Thank you for your business';
        RAISE NOTICE 'Added voucher_footer_message column to res_company';
    END IF;
END $$;

-- Add voucher_terms column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_terms'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_terms TEXT DEFAULT 'Computer-generated document';
        RAISE NOTICE 'Added voucher_terms column to res_company';
    END IF;
END $$;

-- Add use_osus_branding column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'use_osus_branding'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN use_osus_branding BOOLEAN DEFAULT TRUE;
        RAISE NOTICE 'Added use_osus_branding column to res_company';
    END IF;
END $$;
"

if %errorlevel% neq 0 (
    echo ERROR: Database fix failed
    pause
    exit /b 1
)

echo Step 2: Updating Odoo module...
docker-compose exec -T odoo odoo --update=payment_account_enhanced --stop-after-init --no-http

echo Step 3: Restarting Odoo...
docker-compose restart odoo

echo.
echo ✓ Emergency fix completed successfully!
echo   The websocket error should now be resolved.
echo   Check Odoo logs to confirm the fix.
echo.
pause
