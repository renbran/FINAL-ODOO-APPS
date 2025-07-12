# Calendar Extended - Database Update & XML Fix

## 🚨 **Issues Fixed:**

1. **XML Validation Error**: Fixed duplicate content in `calendar_extended_menus.xml`
2. **Model Conflicts**: Removed old problematic model files that were causing selection field errors
3. **File Cleanup**: Removed all old view files, wizard files, and data files not needed in the rebuilt module

## ✅ **Files Cleaned:**

### **Removed Model Files:**
- `models/calendar_recurrence.py` (was causing selection field errors)
- `models/calendar_event.py`
- `models/calendar_event_type.py`
- `models/calendar_resource.py`
- `models/calendar_template.py`
- `models/calendar_reminder.py`
- `models/res_partner.py`
- `models/calendar_internal_meeting.py`
- `models/calendar_meeting_attendee.py`

### **Removed View Files:**
- `views/calendar_department_group_views.xml`
- `views/calendar_event_type_views.xml`
- `views/calendar_resource_views.xml`
- `views/calendar_template_views.xml`
- `views/calendar_meeting_wizard_views.xml`
- `views/calendar_internal_meeting_views.xml`

### **Removed Data Files:**
- `data/calendar_data.xml`
- `data/email_templates.xml`
- `security/calendar_extended_security.xml`
- Entire `wizards/` directory

## 🎯 **Current Clean Module Structure:**

```
calendar_extended/
├── __manifest__.py                 # Clean, focused dependencies
├── models/
│   ├── __init__.py                # Only imports calendar_announcement
│   └── calendar_announcement.py   # Main model with approval workflow
├── wizard/
│   ├── __init__.py
│   ├── calendar_department_select_wizard.py
│   └── calendar_send_invitation_wizard.py
├── views/
│   ├── calendar_announcement_views.xml
│   ├── calendar_extended_menus.xml (FIXED)
│   └── wizard views...
├── security/
│   ├── calendar_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── mail_templates.xml
│   └── cron_jobs.xml
└── static/
    ├── src/css/calendar_extended.css
    └── src/js/calendar_extended.js
```

## 🚀 **Deployment Commands:**

### **For your server (/var/odoo/osuspro):**

```bash
# 1. Stop Odoo service
sudo systemctl stop odoo

# 2. Copy the cleaned module to server
# (Upload your cleaned local module to the server first)

# 3. Clean server cache and uninstall old module
sudo find /var/odoo/osuspro -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
sudo find /var/odoo/osuspro -name "*.pyc" -delete 2>/dev/null || true

# 4. Uninstall the problematic module
sudo -u odoo /var/odoo/osuspro/venv/bin/python3 /var/odoo/osuspro/src/odoo-bin \
    -c /var/odoo/osuspro/odoo.conf \
    --no-http \
    --stop-after-init \
    --uninstall calendar_extended

# 5. Start Odoo (needed for module operations)
sudo systemctl start odoo

# 6. Wait and install the clean module
sleep 10
sudo -u odoo /var/odoo/osuspro/venv/bin/python3 /var/odoo/osuspro/src/odoo-bin \
    -c /var/odoo/osuspro/odoo.conf \
    --no-http \
    --stop-after-init \
    --install calendar_extended

# 7. Check status
sudo systemctl status odoo
```

### **Alternative: Use the automated script:**

```bash
# Make script executable and run
sudo chmod +x /var/odoo/osuspro/src/addons/calendar_extended/cleanup_and_update.sh
sudo bash /var/odoo/osuspro/src/addons/calendar_extended/cleanup_and_update.sh
```

## ✅ **Expected Result:**

- ✅ **No more XML validation errors**
- ✅ **No more selection field errors** 
- ✅ **Clean module installation**
- ✅ **Meeting Announcements functionality working**
- ✅ **Approval workflow operational**
- ✅ **Department selection working**

## 📍 **Access Location:**

After successful installation, find the module at:
**Calendar → Meeting Announcements → Announcements**

---

**Status: 🟢 Ready for clean deployment - All XML and model conflicts resolved!**
