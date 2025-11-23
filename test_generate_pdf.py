#!/usr/bin/env python3
"""
Generate a test invoice PDF to verify OSUS template application
"""

import base64

# Find a sample invoice or create test data
invoice = env['account.move'].search([('move_type', '=', 'out_invoice'), ('state', '=', 'posted')], limit=1)

if not invoice:
    print("⚠️ No posted invoices found. Searching for any invoice...")
    invoice = env['account.move'].search([('move_type', '=', 'out_invoice')], limit=1)

if invoice:
    print(f"📄 Found invoice: {invoice.name}")
    print(f"   Partner: {invoice.partner_id.name}")
    print(f"   Amount: {invoice.amount_total} {invoice.currency_id.name}")
    print(f"   State: {invoice.state}")
    
    # Find invoice report
    report = env.ref('account.account_invoices', raise_if_not_found=False)
    
    if not report:
        print("\n⚠️ Standard invoice report not found, searching for any invoice report...")
        report = env['ir.actions.report'].search([
            ('model', '=', 'account.move'),
            ('report_type', '=', 'qweb-pdf')
        ], limit=1)
    
    if report:
        print(f"\n📋 Using report: {report.name}")
        print(f"   Apply OSUS template: {report.apply_osus_template}")
        
        try:
            print("\n🎨 Generating PDF with OSUS template...")
            pdf_content, content_type = report._render_qweb_pdf(report.report_name, invoice.ids)
            pdf_size = len(pdf_content)
            
            print(f"\n✅ PDF generated successfully!")
            print(f"   Size: {pdf_size:,} bytes")
            print(f"   Content type: {content_type}")
            
            # Save to temp file for inspection
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
                f.write(pdf_content)
                print(f"   Saved to: {f.name}")
                print(f"\n💡 Download this file to verify the OSUS template is applied:")
                print(f"   scp root@139.84.163.11:{f.name} ./test_invoice_with_template.pdf")
                
        except Exception as e:
            print(f"\n❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ No invoice report found")
else:
    print("❌ No invoices found in database")
    print("\n💡 To test, create an invoice first:")
    print("   - Go to Accounting → Customers → Invoices")
    print("   - Create and post an invoice")
    print("   - Then run this test again")
