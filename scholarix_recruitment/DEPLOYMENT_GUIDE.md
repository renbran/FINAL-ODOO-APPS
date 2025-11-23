# 🚀 DEPLOYMENT GUIDE - Scholarix Recruitment Extension
**Module:** scholarix_recruitment  
**Version:** 17.0.1.0.0  
**Status:** ✅ PRODUCTION-READY  
**Date:** November 14, 2025

---

## ⚡ QUICK DEPLOYMENT (5 Minutes)

### For Docker Environment (OSUSAPPS Standard)

```bash
# 1. Copy module to extra-addons
cp -r scholarix_recruitment /path/to/odoo/extra-addons/

# 2. Restart Odoo container
docker-compose restart odoo

# 3. Watch logs
docker-compose logs -f odoo

# 4. Install via UI
# Settings > Apps > Update Apps List
# Search "Scholarix" > Install
```

### For Production Server (Vultr)

```bash
# 1. Backup database FIRST (CRITICAL!)
pg_dump properties > /var/backups/properties_$(date +%Y%m%d_%H%M%S).sql

# 2. Copy module
sudo cp -r scholarix_recruitment /var/odoo/properties/extra-addons/

# 3. Set permissions
sudo chown -R odoo:odoo /var/odoo/properties/extra-addons/scholarix_recruitment

# 4. Clear Python cache (IMPORTANT!)
find /var/odoo/properties/extra-addons/scholarix_recruitment -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find /var/odoo/properties/extra-addons/scholarix_recruitment -name "*.pyc" -delete

# 5. Update apps list
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d properties -u base --stop-after-init

# 6. Install module (via UI is safer)
# OR via CLI:
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d properties -i scholarix_recruitment --stop-after-init

# 7. Monitor logs
tail -f /var/log/odoo/odoo.log
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Environment Verification
- [ ] Odoo 17 installed and running
- [ ] Database backup completed (CRITICAL!)
- [ ] `hr_recruitment` module already installed
- [ ] Disk space available (min 50MB)
- [ ] Python environment is correct
- [ ] Docker/Odoo service has write permissions

### Configuration Ready
- [ ] Company logo prepared (PNG, 300x80px recommended)
- [ ] Email server configured (SMTP settings)
- [ ] Company details updated (name, address, phone)
- [ ] Test email address ready for verification

### Team Preparation
- [ ] HR team notified of new features
- [ ] Training session scheduled
- [ ] Support contact information shared
- [ ] Quick reference guide distributed

---

## 🔧 DETAILED INSTALLATION STEPS

### Step 1: Backup Database (CRITICAL!)

```bash
# Docker environment
docker-compose exec db pg_dump -U odoo odoo > backup_$(date +%Y%m%d_%H%M%S).sql

# Production server
pg_dump properties > /var/backups/properties_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup size
ls -lh backup_*.sql

# IMPORTANT: Keep this backup until deployment is confirmed successful
```

### Step 2: Copy Module Files

```bash
# Ensure you're in the correct directory
pwd
# Should show: /path/to/OSUSAPPS

# Copy module
cp -r scholarix_recruitment /path/to/odoo/extra-addons/

# Verify files copied
ls -la /path/to/odoo/extra-addons/scholarix_recruitment/

# Expected output:
# __init__.py
# __manifest__.py
# models/
# views/
# reports/
# data/
# security/
# static/
# README.md
# etc.
```

### Step 3: Set Permissions (Production Only)

```bash
# Set owner
sudo chown -R odoo:odoo /var/odoo/properties/extra-addons/scholarix_recruitment

# Set permissions
sudo chmod -R 755 /var/odoo/properties/extra-addons/scholarix_recruitment

# Verify
ls -la /var/odoo/properties/extra-addons/ | grep scholarix
```

### Step 4: Clear Python Cache

```bash
# Navigate to module directory
cd /path/to/odoo/extra-addons/scholarix_recruitment

# Clear all Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Verify cache cleared
find . -name "*.pyc" -o -name __pycache__
# Should return nothing
```

### Step 5: Restart Odoo Service

```bash
# Docker environment
docker-compose restart odoo

# Production systemd service
sudo systemctl restart odoo

# Verify service is running
docker-compose ps odoo
# OR
sudo systemctl status odoo
```

### Step 6: Update Apps List

**Via Odoo UI (Recommended):**
1. Log in as Administrator
2. Navigate to: **Settings > Apps**
3. Click: **Update Apps List** button (top menu)
4. Confirm the action
5. Wait for completion message

**Via Command Line (Alternative):**
```bash
# Docker
docker-compose exec odoo odoo -u base --stop-after-init

# Production
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d properties -u base --stop-after-init
```

### Step 7: Install Module

**Via Odoo UI (Recommended):**
1. Navigate to: **Apps**
2. Remove "Apps" filter (click X on filter chip)
3. Search: **"Scholarix"**
4. Click: **Install** button
5. Wait for installation to complete
6. Verify success message

**Via Command Line (Advanced):**
```bash
# Docker
docker-compose exec odoo odoo -i scholarix_recruitment --stop-after-init

# Production
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d properties -i scholarix_recruitment --stop-after-init
```

### Step 8: Verify Installation

1. **Check Module Status:**
   - Apps > Search "Scholarix"
   - Status should show: **Installed** (green)

2. **Check Recruitment Menu:**
   - Navigate to: **Recruitment > Applications**
   - Open any applicant (or create test)
   - Verify new tabs appear:
     - Personal Information
     - Employment Details
     - Compensation & Benefits
     - Offer Letter

3. **Check Buttons:**
   - Header should have:
     - "Generate Offer Letter" button
     - "Send Offer Letter" button

4. **Check Logs:**
```bash
# Docker
docker-compose logs -f odoo | grep scholarix

# Production
tail -f /var/log/odoo/odoo.log | grep scholarix

# Should see:
# INFO database odoo.modules.loading: loading scholarix_recruitment/security/ir.model.access.csv
# INFO database odoo.modules.loading: loading scholarix_recruitment/views/hr_applicant_views.xml
# etc.
```

---

## 🎨 POST-INSTALLATION CONFIGURATION

### 1. Upload Company Logo

1. Navigate to: **Settings > General Settings > Companies**
2. Click on your company name
3. Click: **Edit**
4. Upload logo in **Company Logo** field
   - Format: PNG (recommended)
   - Size: 300x80px optimal
   - Max size: 5MB
5. Click: **Save**

### 2. Configure Email Server

1. Navigate to: **Settings > Technical > Email > Outgoing Mail Servers**
2. Create/Edit server:
   - **Description:** Scholarix Careers
   - **SMTP Server:** smtp.gmail.com (or your provider)
   - **SMTP Port:** 587
   - **Connection Security:** TLS (STARTTLS)
   - **Username:** careers@scholarixglobal.com
   - **Password:** [your password]
3. Click: **Test Connection**
4. Verify success message
5. Click: **Save**

### 3. Update Company Details

1. Navigate to: **Settings > General Settings > Companies**
2. Update:
   - **Company Name:** Scholarix Global
   - **Address:** Dubai, UAE
   - **Phone:** +971 XX XXX XXXX
   - **Email:** careers@scholarixglobal.com
   - **Website:** www.scholarixglobal.com
3. Click: **Save**

### 4. Test Email Template

1. Navigate to: **Settings > Technical > Email > Email Templates**
2. Search: **"Offer Letter - Scholarix Global"**
3. Click to open
4. Click: **Preview** (if available)
5. Verify branding and layout

---

## 🧪 TESTING PROCEDURES

### Test 1: Create Test Applicant

1. Navigate to: **Recruitment > Applications**
2. Click: **Create**
3. Fill basic fields:
   - **Subject / Application:** Test Applicant - John Doe
   - **Email:** test@example.com
   - **Job Position:** Select any
4. Click: **Save**

### Test 2: Fill Personal Information

1. Open test applicant
2. Navigate to: **Personal Information** tab
3. Fill fields:
   - Full Name (Arabic): محمد أحمد
   - Nationality: Select country
   - Emirates ID: 784-1234-1234567-1
   - Passport: A12345678
   - Date of Birth: 1990-01-01
   - UAE Mobile: +971-50-123-4567
   - Personal Email: test@example.com
   - Current Address: Dubai Marina, Dubai, UAE
4. Click: **Save**

### Test 3: Fill Employment Details

1. Navigate to: **Employment Details** tab
2. Fill fields:
   - Position Title: Senior Odoo Consultant
   - Department: Select or create
   - Employment Type: Unlimited Contract
   - Probation Period: 180 days
   - Proposed Start Date: [Future date]
   - Work Location: Dubai, United Arab Emirates
   - Notice Period: 30 days
3. Click: **Save**

### Test 4: Fill Compensation

1. Navigate to: **Compensation & Benefits** tab
2. Fill salary fields:
   - Basic Salary: 15,000 AED
   - Housing Allowance: 5,000 AED
   - Transport Allowance: 2,000 AED
3. Verify auto-calculations:
   - Total Monthly: Should show 22,000 AED ✅
   - Annual Salary: Should show 264,000 AED ✅
4. Fill benefits:
   - Annual Leave Days: 30
   - Health Insurance: Basic Plan
   - Visa Provided: ✓ (checked)
   - Flight Tickets: Annual Return Ticket
5. Click: **Save**

### Test 5: Generate Offer Letter

1. Navigate to: **Offer Letter** tab
2. Verify:
   - Offer Letter Reference: Auto-generated (SGO-YYYYMMDD-XXXX)
   - Offer Letter Date: Today's date
   - Offer Valid Until: Date + 14 days
3. Click: **Generate Offer Letter** button
4. Verify PDF opens
5. Check PDF contents:
   - [ ] Letterhead displays correctly
   - [ ] Company logo visible
   - [ ] All data populated
   - [ ] Salary table formatted
   - [ ] Benefits listed
   - [ ] Signature boxes present
   - [ ] No errors or missing data

### Test 6: Send Email

1. Update **Email** field to your test email
2. Click: **Send Offer Letter** button
3. Verify success notification
4. Check email inbox:
   - [ ] Email received
   - [ ] Subject correct
   - [ ] Branding displays
   - [ ] PDF attached
   - [ ] All links work

---

## 🚨 TROUBLESHOOTING

### Issue: Module Not Appearing in Apps List

**Solution:**
```bash
# Clear Odoo assets cache
docker-compose exec odoo odoo --dev=all -u base --stop-after-init

# Or delete assets manually
rm -rf ~/.local/share/Odoo/filestore/[database]/assets/*

# Update apps list again via UI
```

### Issue: PDF Not Generating

**Symptoms:** Error when clicking "Generate Offer Letter"

**Solution:**
```bash
# Check wkhtmltopdf installation
which wkhtmltopdf

# If not installed (Docker):
docker-compose exec odoo apt-get update
docker-compose exec odoo apt-get install -y wkhtmltopdf

# If not installed (Production):
sudo apt-get install -y wkhtmltopdf

# Restart Odoo
docker-compose restart odoo
```

### Issue: Email Not Sending

**Symptoms:** No error but email not received

**Solution:**
1. Check outgoing mail server configuration
2. Test SMTP connection
3. Check Odoo logs:
```bash
docker-compose logs -f odoo | grep -i mail
```
4. Verify email address is valid
5. Check spam folder

### Issue: Fields Not Visible

**Symptoms:** New tabs don't appear in applicant form

**Solution:**
```bash
# Clear browser cache (Ctrl + Shift + Delete)

# Clear Odoo cache
docker-compose exec odoo odoo --dev=all --stop-after-init

# Upgrade module
docker-compose exec odoo odoo -u scholarix_recruitment --stop-after-init

# Hard refresh browser (Ctrl + F5)
```

### Issue: Logo Not Appearing

**Symptoms:** PDF shows "SCHOLARIX GLOBAL" text instead of logo

**Solution:**
1. Upload company logo (Settings > Companies)
2. Verify logo file is PNG format
3. Check file size (should be < 5MB)
4. Regenerate offer letter

### Issue: Calculation Errors

**Symptoms:** Total salary incorrect

**Solution:**
1. Check currency is set correctly
2. Re-save record to trigger recomputation
3. Check logs for Python errors:
```bash
docker-compose logs -f odoo | grep -i error
```

---

## 📊 MONITORING & MAINTENANCE

### Daily Checks (First Week)

```bash
# Check for errors
docker-compose logs --tail=100 odoo | grep -i error

# Check module usage
docker-compose exec db psql -U odoo -d odoo -c "SELECT COUNT(*) FROM hr_applicant WHERE offer_letter_reference IS NOT NULL;"

# Check email queue
docker-compose exec db psql -U odoo -d odoo -c "SELECT COUNT(*) FROM mail_mail WHERE state = 'exception';"
```

### Weekly Maintenance

1. Review error logs
2. Check user feedback
3. Monitor PDF generation performance
4. Verify email delivery rates
5. Check disk space usage

### Monthly Review

1. Review usage statistics
2. Gather user feedback
3. Plan improvements
4. Update documentation
5. Check for Odoo updates

---

## 🔄 ROLLBACK PROCEDURE (If Needed)

### Emergency Rollback

```bash
# 1. Stop Odoo
docker-compose stop odoo

# 2. Restore database backup
docker-compose exec db psql -U odoo -d odoo < backup_YYYYMMDD.sql

# 3. Remove module directory
rm -rf /path/to/odoo/extra-addons/scholarix_recruitment

# 4. Start Odoo
docker-compose start odoo

# 5. Uninstall via UI (if needed)
# Apps > Scholarix Recruitment > Uninstall
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

### Immediately After Installation
- [ ] Module installed successfully
- [ ] No errors in logs
- [ ] New tabs visible in applicant form
- [ ] Test applicant created
- [ ] PDF generation works
- [ ] Email sending works

### Within 24 Hours
- [ ] Company logo uploaded
- [ ] Email server configured
- [ ] Company details updated
- [ ] HR team notified
- [ ] Test cases completed
- [ ] Backup verified and stored safely

### Within 1 Week
- [ ] HR team training completed
- [ ] Real applicant data entered
- [ ] Offer letters generated for real candidates
- [ ] Feedback collected from users
- [ ] Performance monitored
- [ ] No critical issues reported

---

## 📞 SUPPORT CONTACTS

### Technical Support
- **Email:** support@scholarixglobal.com
- **Response Time:** 24 hours
- **Scope:** Installation, configuration, bugs

### Development Team
- **Email:** dev@scholarixglobal.com
- **Scope:** Customizations, enhancements

### Emergency Hotline
- **Available:** 9 AM - 6 PM GST (Sun-Thu)
- **For:** Critical production issues

---

## 📚 ADDITIONAL RESOURCES

- **Module README:** `/scholarix_recruitment/README.md`
- **Installation Guide:** `/scholarix_recruitment/INSTALL.md`
- **Production Review:** `/scholarix_recruitment/PRODUCTION_REVIEW.md`
- **Changelog:** `/scholarix_recruitment/CHANGELOG.md`

---

## 🎉 SUCCESS!

If you've reached this point and all tests pass, congratulations! 🎊

The Scholarix Recruitment Extension is now successfully deployed and ready for production use.

**Navigate. Innovate. Transform.** 🚀

---

**Deployment Guide Version:** 1.0  
**Last Updated:** November 14, 2025  
**Next Review:** After 30 days of production use
