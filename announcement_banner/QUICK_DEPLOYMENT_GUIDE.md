# 🚀 Quick Deployment Guide - Announcement Banner

**Status**: ✅ Production Ready  
**Version**: 17.0.1.1.0  
**Time Required**: 5-10 minutes

---

## 📋 Pre-Deployment Checklist

- [ ] Docker is running (check with `docker-compose ps`)
- [ ] Database backup completed
- [ ] Module files are in correct location
- [ ] You have System Administrator access

---

## 🎯 Deployment Steps

### Step 1: Verify Module Location
```bash
# Check module is in addons directory
ls -la "d:\RUNNING APPS\ready production\latest\OSUSAPPS\announcement_banner"
```

Expected output: Should see `__manifest__.py`, `models/`, `views/`, etc.

### Step 2: Update Odoo Apps List
```bash
# Start Docker (if not running)
docker-compose up -d

# Wait for Odoo to be ready (check logs)
docker-compose logs -f odoo
# Press Ctrl+C when you see "HTTP service (werkzeug) running"
```

### Step 3: Install/Update Module

**Option A: Via Odoo UI (Recommended)**
1. Open Odoo in browser
2. Navigate to: **Settings** → **Apps** → **Update Apps List**
3. Search for "Announcement Banner"
4. Click **Install** (or **Upgrade** if already installed)
5. Wait for installation to complete

**Option B: Via Command Line**
```bash
# For Docker environment
docker-compose exec odoo odoo -u announcement_banner -d osusproperties --stop-after-init
docker-compose restart odoo

# For production server
sudo -u odoo odoo -u announcement_banner -d properties --stop-after-init
sudo systemctl restart odoo
```

### Step 4: Verify Installation
1. Go to: **Settings** → **Announcements** (should see new menu)
2. Click **Announcements** → **Create** (should open form)
3. Try creating a test announcement

---

## 🧪 Quick Test

### Create Test Announcement
1. **Navigate**: Settings → Announcements → Announcements
2. **Click**: Create
3. **Enter**:
   - **Title**: "Welcome to OSUSAPPS"
   - **Message**: Type some text, format it bold, add a bullet list
   - **Priority**: 10 (default)
   - Leave dates empty for immediate display
4. **Save**
5. **Test**: Open new browser tab (or incognito) and log in
   - You should see the announcement popup
   - Click "Got it" to close

### Expected Result
✅ Popup appears with:
- Professional header with announcement icon
- Your formatted message (no HTML code visible)
- "Got it" button at bottom
- OSUSAPPS branding in footer

---

## 🔧 Troubleshooting

### Module Not Showing in Apps List
```bash
# Update apps list
docker-compose exec odoo odoo --update=list -d osusproperties --stop-after-init
docker-compose restart odoo
```

### Installation Error
```bash
# Check Odoo logs for errors
docker-compose logs --tail=100 odoo

# Common issues:
# 1. Missing dependencies - check __manifest__.py
# 2. Syntax errors - run validation script
python announcement_banner/validate_module.py
```

### Announcement Not Showing
1. **Check announcement is active**: Edit announcement, verify "Active" is checked
2. **Check dates**: Ensure current date is within start/end date range (or dates are empty)
3. **Check user targeting**: Ensure your user is included (or field is empty)
4. **Check browser cache**: Hard refresh (Ctrl+Shift+R)
5. **Check logs**: Settings → Announcements → Announcement Logs

### HTML Code Visible Instead of Formatted Text
This issue has been **FIXED** in version 1.1.0:
- Template uses `t-raw` instead of `t-out`
- CSS has `word-break: normal`

If you still see HTML code:
1. **Delete old announcement** (it has escaped HTML in database)
2. **Create new announcement** using the HTML editor
3. **Do NOT paste HTML code** - use the toolbar buttons instead

---

## ✅ Post-Deployment Verification

Run this checklist after deployment:

### Functional Tests
- [ ] Module appears in Apps list
- [ ] Module installs without errors
- [ ] Menu "Announcements" appears under Settings
- [ ] Can create new announcement
- [ ] HTML editor toolbar works
- [ ] Can add formatting (bold, italic, bullets)
- [ ] Can insert images
- [ ] Announcement saves successfully
- [ ] Popup appears on next login
- [ ] Formatted text displays correctly (no HTML code)
- [ ] Images display properly
- [ ] Close button works
- [ ] Navigation works (if multiple announcements)
- [ ] Logs record views correctly

### UI/UX Tests
- [ ] Popup is centered on screen
- [ ] Header has OSUSAPPS branding colors (teal/navy)
- [ ] Footer shows "Powered by OSUSAPPS"
- [ ] Text is readable (proper word breaks)
- [ ] Images have rounded corners and shadows
- [ ] Works on mobile (test on phone)

---

## 📱 Mobile Testing

```bash
# Test on mobile devices:
1. iPhone (Safari)
2. Android (Chrome)
3. Tablet (iPad/Android)

Expected:
- Popup fills most of screen
- Text is readable
- Close button is accessible
- Scrolls if content is long
```

---

## 🎨 Creating Your First Announcement

### Example: System Maintenance Notice

**Title**: "Scheduled Maintenance - Sunday 3 AM"

**Message** (use the HTML editor):
```
Dear Users,

Our system will undergo scheduled maintenance on:

📅 Sunday, November 10, 2025
🕐 3:00 AM - 6:00 AM GMT

During this time:
• System will be temporarily unavailable
• All data will be safely backed up
• No action required from users

Thank you for your patience!

- OSUSAPPS Team
```

**Settings**:
- Priority: 20 (high priority)
- Start Date: Nov 7, 2025 (today)
- End Date: Nov 10, 2025 (after maintenance)
- Show Once: ❌ (unchecked - show every time)
- Target Users: (empty - show to all)

---

## 🎯 Configuration Tips

### Priority System
- **30-50**: Critical/Urgent (red alerts, security)
- **20-29**: Important (maintenance, updates)
- **10-19**: Normal (features, announcements)
- **1-9**: Low priority (tips, suggestions)

### Date Strategy
- **No dates**: Permanent announcement (until archived)
- **Start date only**: Begins showing from date, no end
- **End date only**: Shows until date, then auto-hides
- **Both dates**: Shows only within date range

### Show Once Option
- ✅ **Checked**: User sees once (onboarding, new features)
- ❌ **Unchecked**: User sees every login (critical updates)

---

## 📞 Need Help?

### Quick Support
1. **Check logs**: `docker-compose logs -f odoo`
2. **Run validation**: `python validate_module.py`
3. **Review docs**: See `FINAL_DEPLOYMENT_STATUS.md`

### Contact Support
- 📧 Email: support@osusapps.com
- 🌐 Website: https://www.osusapps.com

---

## ✅ Deployment Complete!

If you've completed all steps above, your module is now:
- ✅ Installed and configured
- ✅ Tested and verified
- ✅ Ready for use

**Next Steps**:
1. Create real announcements for your users
2. Train administrators on module usage
3. Monitor announcement logs for engagement
4. Archive old announcements regularly

---

**Happy Announcing! 📢**

*OSUSAPPS - Enterprise Odoo Solutions*
