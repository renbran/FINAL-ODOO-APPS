-- CloudPepper PostgreSQL Fix - Run these commands individually
-- Copy and paste each command separately into your CloudPepper database console

-- Command 1: Add voucher_footer_message column
ALTER TABLE res_company ADD voucher_footer_message TEXT;

-- Command 2: Add voucher_terms column  
ALTER TABLE res_company ADD voucher_terms TEXT;

-- Command 3: Add use_osus_branding column
ALTER TABLE res_company ADD use_osus_branding BOOLEAN;

-- Command 4: Set default values for voucher_footer_message
UPDATE res_company SET voucher_footer_message = 'Thank you for your business' WHERE voucher_footer_message IS NULL;

-- Command 5: Set default values for voucher_terms
UPDATE res_company SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' WHERE voucher_terms IS NULL;

-- Command 6: Set default values for use_osus_branding
UPDATE res_company SET use_osus_branding = TRUE WHERE use_osus_branding IS NULL;

-- Command 7: Verify the fix worked
SELECT COUNT(*) as total_companies, COUNT(voucher_footer_message) as with_footer, COUNT(voucher_terms) as with_terms, COUNT(use_osus_branding) as with_branding FROM res_company;
