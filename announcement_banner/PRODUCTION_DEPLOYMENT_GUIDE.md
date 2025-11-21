# 🚀 Production Deployment Guide
## Announcement Banner - OSUSAPPS

**Version**: 1.1.0
**Odoo Version**: 17.0
**Status**: ✅ Production Ready
**Date**: November 7, 2025

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Testing](#testing)
5. [Deployment to Production](#deployment-to-production)
6. [Post-Deployment](#post-deployment)
7. [Rollback Plan](#rollback-plan)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Environment Requirements
- [ ] Odoo 17.0 installed (Community or Enterprise)
- [ ] Python 3.10 or higher
- [ ] PostgreSQL database with sufficient storage
- [ ] Modern web browsers for end users
- [ ] Backup system in place

### Access Requirements
- [ ] System Administrator access to Odoo
- [ ] SSH/Server access for file deployment
- [ ] Database admin credentials for backup
- [ ] Web server restart permissions

### Module Verification
- [ ] All files present in module directory
- [ ] `__manifest__.py` has correct version (17.0.1.1.0)
- [ ] All dependencies (web, base) available
- [ ] Security CSV file present
- [ ] Assets (JS, CSS, XML) properly structured

---

## Installation Steps

### Step 1: Backup Current System

**CRITICAL: Always backup before installing new modules**

```bash
# Backup database
pg_dump -U odoo -d production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup filestore (attachments)
tar -czf filestore_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/filestore

# Backup addons (if modifying)
tar -czf addons_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/addons
```

### Step 2: Deploy Module Files

**Option A: Manual Deployment**
```bash
# Copy module to Odoo addons directory
cp -r announcement_banner /opt/odoo/custom/addons/

# Set correct permissions
chown -R odoo:odoo /opt/odoo/custom/addons/announcement_banner
chmod -R 755 /opt/odoo/custom/addons/announcement_banner
```

**Option B: Git Deployment**
```bash
# Clone or pull from repository
cd /opt/odoo/custom/addons
git clone https://github.com/osusapps/announcement_banner.git
# OR
cd announcement_banner && git pull origin main
```

### Step 3: Update Odoo Apps List

**Via Command Line:**
```bash
# Restart Odoo with update apps list
odoo -u all -d production_db --stop-after-init

# Or restart Odoo service
systemctl restart odoo
# OR
service odoo restart
```

**Via Web Interface:**
1. Log in as System Administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Confirm the action

### Step 4: Install the Module

**Via Web Interface:**
1. Go to **Apps** menu
2. Remove "Apps" filter to see all modules
3. Search for "Announcement Banner"
4. Click **Install**
5. Wait for installation to complete

**Via Command Line:**
```bash
odoo -i announcement_banner -d production_db --stop-after-init
systemctl restart odoo
```

---

## Configuration

### Step 1: Verify Installation

1. Check that menu item appears: **Announcements** → **Announcements**
2. Verify access rights: Only System Administrators can see the menu
3. Check assets loaded: Open browser console, no JavaScript errors

### Step 2: Configure First Announcement

**Test Announcement Creation:**

1. Navigate to **Announcements** → **Announcements**
2. Click **Create**
3. Fill in:
   - **Title**: "System Announcement Test"
   - **Message**: Add formatted text and an image
   - **Priority**: 10
   - **Active**: ☑
   - **Show Once**: ☐ (for testing)
   - Leave dates empty (shows immediately)
   - Leave users empty (shows to all)
4. Click **Save**

### Step 3: Verify Security Access

**Check User Permissions:**
```python
# In Odoo shell
env['ir.model.access'].search([
    ('model_id.model', 'in', ['announcement.banner', 'announcement.banner.log'])
])
```

**Expected Groups:**
- `announcement.banner`: System Administrator (create, read, write, delete)
- `announcement.banner.log`: System Administrator (create, read), Users (read)

---

## Testing

### Test 1: Display Test

1. Open Odoo in **incognito/private window**
2. Log in as a test user
3. **Expected**: Announcement popup appears
4. **Verify**:
   - Title displays correctly
   - Message shows formatted (no HTML code)
   - Images display properly
   - "Got it" button works
   - Close button (X) works
   - Popup closes on background click

### Test 2: Formatting Test

Create announcement with:
```html
<h2>Formatted Test</h2>
<p>This is <strong>bold</strong> and <em>italic</em> text.</p>
<ul>
  <li>Bullet point 1</li>
  <li>Bullet point 2</li>
</ul>
<p>Image below:</p>
<img src="https://via.placeholder.com/400x200" alt="Test">
```

**Expected**: All formatting displays correctly, no HTML tags visible

### Test 3: Multiple Announcements

1. Create 3 announcements with different priorities
2. Log in as new user
3. **Expected**:
   - Highest priority shows first
   - Navigation buttons appear (1/3)
   - Can navigate between announcements
   - All announcements tracked in logs

### Test 4: Scheduling Test

1. Create announcement with:
   - Start Date: Tomorrow
   - End Date: +7 days
2. **Expected**: Announcement doesn't show today
3. Modify start date to yesterday
4. **Expected**: Announcement shows

### Test 5: User Targeting

1. Create announcement targeting specific user
2. Log in as that user
3. **Expected**: Announcement shows
4. Log in as different user
5. **Expected**: Announcement doesn't show

### Test 6: Show Once Option

1. Create announcement with "Show Once" checked
2. Log in, view announcement, close
3. Log out and log in again
4. **Expected**: Announcement doesn't show
5. Check logs: Entry exists for user

### Test 7: Mobile Responsive

1. Open on mobile device or resize browser
2. **Expected**:
   - Modal adjusts to screen size
   - Content readable
   - Buttons accessible
   - Navigation works

### Test 8: Performance Test

1. Create 10+ announcements
2. Log in
3. **Expected**:
   - Page loads normally
   - No significant delay
   - Browser console shows no errors

---

## Deployment to Production

### Pre-Deployment

1. **Notify Users**
   ```
   Subject: System Update - Announcement Feature

   We will be deploying a new announcement system today at [TIME].
   Expected downtime: 5 minutes

   New Feature: You will see important announcements when logging in.
   ```

2. **Schedule Maintenance Window**
   - Off-peak hours recommended
   - Allocate 30-60 minutes
   - Have rollback plan ready

### Deployment

**1. Enable Maintenance Mode**
```bash
# Add to config file or use Odoo CLI
odoo --stop-after-init --config=/etc/odoo.conf
```

**2. Deploy Module**
```bash
# Deploy files
cp -r announcement_banner /opt/odoo/production/addons/

# Install module
odoo -i announcement_banner -d production_db --stop-after-init
```

**3. Restart Services**
```bash
systemctl restart odoo
systemctl restart nginx  # if using nginx
```

**4. Verify Deployment**
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log

# Check for errors
grep -i error /var/log/odoo/odoo.log
```

**5. Disable Maintenance Mode**
```bash
# Remove maintenance flag and restart
systemctl restart odoo
```

---

## Post-Deployment

### Verification Steps

1. **Smoke Test**
   - [ ] Can access Odoo
   - [ ] Can log in successfully
   - [ ] Announcement menu visible to admins
   - [ ] Can create announcement
   - [ ] Announcement displays to users

2. **Monitor Logs**
```bash
# Watch for errors
tail -f /var/log/odoo/odoo.log | grep announcement

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log
```

3. **User Feedback**
   - Monitor support channels
   - Check for reported issues
   - Gather user feedback

### Initial Announcements

**Recommended First Announcement:**
```
Title: Welcome to Our New Announcement System!

Message:
We've introduced a new way to keep you informed about important updates.

What's New:
• You'll see announcements like this when you log in
• Important updates will be highlighted
• You can navigate through multiple announcements

Click "Got it" when you've read the message.

Questions? Contact IT Support.
```

---

## Rollback Plan

### If Issues Occur

**Option 1: Uninstall Module**
```bash
# Via Odoo CLI
odoo -u announcement_banner -d production_db --stop-after-init

# Then manually uninstall via web interface
```

**Option 2: Restore from Backup**
```bash
# Stop Odoo
systemctl stop odoo

# Restore database
psql -U odoo production_db < backup_YYYYMMDD_HHMMSS.sql

# Restore filestore
tar -xzf filestore_backup_YYYYMMDD_HHMMSS.tar.gz -C /path/to/odoo/

# Start Odoo
systemctl start odoo
```

**Option 3: Disable Module**
```python
# In Odoo shell
module = env['ir.module.module'].search([('name', '=', 'announcement_banner')])
module.button_immediate_uninstall()
```

---

## Troubleshooting

### Issue 1: Announcements Not Showing

**Symptoms**: Users don't see announcements after logging in

**Solutions**:
1. Check announcement is Active
2. Verify start/end dates
3. Check user targeting
4. Clear browser cache
5. Check browser console for JS errors

```bash
# Check for JavaScript errors in logs
grep -i "announcement" /var/log/odoo/odoo.log
```

### Issue 2: HTML Code Visible

**Symptoms**: Raw HTML tags showing instead of formatted content

**Solutions**:
1. Verify module version is 1.1.0
2. Check `t-raw` is used in XML template (not `t-esc`)
3. Clear browser cache
4. Check sanitization settings in model

### Issue 3: Images Not Displaying

**Symptoms**: Image links shown instead of actual images

**Solutions**:
1. Verify image URL is accessible
2. Check CORS settings if external images
3. Use Odoo's image upload feature
4. Check CSS for image styling

### Issue 4: Performance Issues

**Symptoms**: Slow page load when announcements active

**Solutions**:
1. Limit number of active announcements
2. Optimize images (compress, resize)
3. Check database indexes
4. Monitor server resources

```sql
-- Check announcement counts
SELECT COUNT(*) FROM announcement_banner WHERE active = true;

-- Check log size
SELECT COUNT(*) FROM announcement_banner_log;
```

### Issue 5: Permission Errors

**Symptoms**: Users can't see menu or get access denied

**Solutions**:
1. Verify security groups
2. Update access rights CSV
3. Clear Odoo cache

```bash
# Restart Odoo to reload security
systemctl restart odoo
```

---

## Monitoring & Maintenance

### Key Metrics to Monitor

1. **Usage Statistics**
```sql
-- Announcements shown per day
SELECT DATE(shown_date), COUNT(*)
FROM announcement_banner_log
GROUP BY DATE(shown_date)
ORDER BY DATE(shown_date) DESC;

-- Most viewed announcements
SELECT a.name, COUNT(l.id) as view_count
FROM announcement_banner a
LEFT JOIN announcement_banner_log l ON l.announcement_id = a.id
GROUP BY a.id, a.name
ORDER BY view_count DESC;
```

2. **Performance Metrics**
   - Page load time with announcements
   - JavaScript console errors
   - Server response time

3. **User Feedback**
   - Support tickets related to announcements
   - User survey on announcement helpfulness

### Regular Maintenance

**Weekly:**
- [ ] Review active announcements
- [ ] Archive expired announcements
- [ ] Check for old logs (cleanup if needed)

**Monthly:**
- [ ] Review announcement analytics
- [ ] Optimize images and content
- [ ] Update announcement strategy

**Quarterly:**
- [ ] Review module updates
- [ ] Test new features
- [ ] User training refresh

---

## Security Considerations

### Access Control
- Only System Administrators can create/edit announcements
- Users can only view their own logs
- No SQL injection vulnerabilities
- XSS protection via Odoo's sanitization

### Content Security
- HTML content sanitized by default
- External images should be vetted
- Links should be verified
- No script execution allowed

### Data Privacy
- Logs contain user IDs (PII)
- GDPR compliance: Users can request log deletion
- Retention policy recommended (e.g., 90 days)

### Audit Trail
```sql
-- View all announcement changes
SELECT * FROM ir_logging
WHERE func LIKE '%announcement%'
ORDER BY create_date DESC;
```

---

## Support & Contact

### Getting Help

**OSUSAPPS Support:**
- 📧 Email: support@osusapps.com
- 🌐 Website: https://www.osusapps.com
- 📞 Enterprise Support: Available for production issues

### Emergency Contact

For critical production issues:
1. Email: support@osusapps.com (Priority: URGENT)
2. Include:
   - Company name
   - Odoo version
   - Module version
   - Error description
   - Screenshots/logs
   - Impact level (Critical/High/Medium/Low)

---

## Success Criteria

Deployment is successful when:

- ✅ Module installed without errors
- ✅ Announcements display correctly
- ✅ Formatting and images work
- ✅ Navigation functions properly
- ✅ Mobile responsive
- ✅ No JavaScript errors
- ✅ Performance acceptable
- ✅ Users can interact successfully
- ✅ Logs recording properly
- ✅ No support tickets about bugs

---

## Additional Resources

- **README.md**: Comprehensive module documentation
- **CHANGELOG.md**: Version history and changes
- **FIX_HTML_DISPLAY_ISSUE.md**: Troubleshooting HTML issues
- **index.html**: Marketing and feature documentation

---

**Deployment Prepared By**: OSUSAPPS
**Last Updated**: November 7, 2025
**Version**: 1.1.0

✅ **This module is PRODUCTION READY and has been tested across multiple environments**

---

*Good luck with your deployment! For any questions, contact OSUSAPPS support.*
