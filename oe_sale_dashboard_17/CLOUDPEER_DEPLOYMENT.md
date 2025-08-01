# CloudPeer Deployment Checklist - Odoo 17 Sales Dashboard

## Quick Deployment Steps for CloudPeer

### 1. Pre-Deployment Preparation ✅

**Check Module Dependencies:**
- ✅ commission_ax module (for agent/broker fields)
- ✅ osus_invoice_report module (for sale_value, booking_date fields)
- ✅ le_sale_type module (for sales type categorization)

**Verify Module Files:**
- ✅ __manifest__.py (updated with AED currency support)
- ✅ models/sale_dashboard.py (enhanced with field validation)
- ✅ static/src/js/dashboard.js (fixed OWL syntax errors)
- ✅ static/src/xml/dashboard_template.xml (safe template patterns)
- ✅ static/src/scss/dashboard.scss (responsive design)
- ✅ views/dashboard_views.xml (Odoo 17 compatible)
- ✅ security/ir.model.access.csv (proper permissions)

### 2. CloudPeer Upload Process 📁

1. **Create Module Package:**
   ```powershell
   # Run the deployment script
   .\deploy_cloudpeer.ps1 -CloudPeerHost "your-cloudpeer-url" -DatabaseName "your-db" -TestMode
   ```

2. **Upload to CloudPeer:**
   - Access CloudPeer file manager
   - Navigate to `/odoo/addons/` directory
   - Upload the module folder or ZIP package
   - Extract if uploaded as ZIP

3. **Set Proper Permissions:**
   ```bash
   # If you have SSH access
   chown -R odoo:odoo /odoo/addons/oe_sale_dashboard_17
   chmod -R 755 /odoo/addons/oe_sale_dashboard_17
   ```

### 3. Odoo Module Installation 🔧

1. **Update Apps List:**
   - Go to Settings → Apps
   - Click "Update Apps List"
   - Wait for completion

2. **Install/Upgrade Module:**
   - Search for "OSUS Executive Sales Dashboard"
   - Click Install (new) or Upgrade (existing)
   - Wait for installation to complete

3. **Clear Assets Cache:**
   - Go to Settings → Technical → Database Structure → Sequences
   - Or restart Odoo service if possible

### 4. Verification Tests 🧪

**Dashboard Access:**
- ✅ Navigate to Sales → Dashboard
- ✅ Dashboard loads without errors
- ✅ All sections render properly

**Data Display:**
- ✅ AED currency formatting shows correctly
- ✅ Commission data from agents/brokers displays
- ✅ Sales type categorization works
- ✅ Date filtering functions properly

**Chart Functionality:**
- ✅ Chart.js loads from CDN
- ✅ All charts render without errors
- ✅ Interactive features work (hover, click)
- ✅ Responsive design on mobile/tablet

**JavaScript Console:**
- ✅ No errors in browser developer tools
- ✅ OWL template rendering works correctly
- ✅ State management functions properly

### 5. Post-Deployment Monitoring 📊

**Server Logs:**
```bash
# Monitor for errors
tail -f /var/log/odoo/odoo.log | grep -i "dashboard\|error\|exception"
```

**Performance Checks:**
- ✅ Dashboard loads within acceptable time
- ✅ Database queries are optimized
- ✅ Memory usage is reasonable
- ✅ No browser memory leaks

**User Experience:**
- ✅ All dashboard features work correctly
- ✅ Data refreshes properly on date changes
- ✅ Export functions work (if implemented)
- ✅ Responsive design works on all devices

### 6. Troubleshooting Common Issues 🔧

**Chart.js Not Loading:**
- Check internet connectivity from server
- Verify CDN URLs are accessible
- Check browser console for network errors

**"Field does not exist" Errors:**
- Verify dependent modules are installed
- Check field existence validation in code
- Review database schema for missing fields

**Template Rendering Errors:**
- Clear browser cache completely
- Check OWL template syntax in XML
- Verify JavaScript state initialization

**AED Currency Not Showing:**
- Check format_dashboard_value method
- Verify locale settings in browser
- Test currency formatting functions

### 7. Emergency Rollback Plan 🚨

**If Deployment Fails:**

1. **Immediate Actions:**
   ```bash
   # Stop Odoo service
   sudo systemctl stop odoo
   
   # Remove module
   rm -rf /odoo/addons/oe_sale_dashboard_17
   
   # Start Odoo service
   sudo systemctl start odoo
   ```

2. **Database Cleanup:**
   - Go to Settings → Apps
   - Search for "oe_sale_dashboard_17"
   - Uninstall module if it appears
   - Clear any remaining data

3. **Recovery Steps:**
   - Fix identified issues
   - Test in development environment
   - Retry deployment with corrected version

### 8. Success Confirmation ✅

**Dashboard is successfully deployed when:**
- ✅ No errors in Odoo logs
- ✅ Dashboard menu appears in Sales app
- ✅ All charts render with correct data
- ✅ AED currency formatting displays properly
- ✅ Commission fields show agent/broker data
- ✅ Date filtering works correctly
- ✅ No JavaScript errors in browser console
- ✅ Responsive design works on all devices
- ✅ Performance is acceptable for end users

### 9. CloudPeer Specific Notes 📝

**Important CloudPeer Considerations:**
- CDN access for Chart.js - ensure server has internet connectivity
- File permissions - CloudPeer may have specific requirements
- Service restart - may require CloudPeer support for service control
- Backup - CloudPeer should handle automatic backups
- SSL/HTTPS - ensure CDN resources load over HTTPS if site uses SSL

**Contact CloudPeer Support If:**
- Unable to upload module files
- Service restart needed but no access
- Performance issues after deployment
- Network connectivity issues affecting CDN resources

---

**Deployment Package Location:** `/tmp/oe_sale_dashboard_17_[timestamp].zip`
**Ready for CloudPeer Upload and Installation!**
