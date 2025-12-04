# ===============================================================================
# EMERGENCY FIX: ai_enrichment_report Field Undefined OwlError
# ===============================================================================
# Date: November 29, 2025
# Error: "crm.lead"."ai_enrichment_report" field is undefined
# Severity: CRITICAL - Prevents CRM lead forms from loading
# ===============================================================================

## ROOT CAUSE ANALYSIS

**Error Type**: OwlError in lifecycle
**Error Location**: scholarixglobal.com production server
**Affected Module**: llm_lead_scoring
**Missing Field**: crm.lead.ai_enrichment_report

**Why This Happened**:
1. The `llm_lead_scoring` module added the `ai_enrichment_report` field to `crm.lead`
2. Views reference this field in `llm_lead_scoring/views/crm_lead_views.xml`
3. On production, the field doesn't exist, causing:
   - Module not installed
   - Module not upgraded after deployment
   - Database schema not synchronized
   - Field definition not migrated

## IMMEDIATE SOLUTIONS (Choose One)

### ✅ SOLUTION 1: Install Compatibility Module (RECOMMENDED - FASTEST)

**Time to Fix**: 2-5 minutes
**Risk Level**: LOW
**Rollback**: Easy

This creates a safety layer that provides the missing field without requiring full module upgrade.

**Steps**:
```bash
# 1. Upload compatibility module to server
scp -r crm_ai_field_compatibility/ user@scholarixglobal.com:/opt/odoo/addons/

# 2. SSH to server
ssh user@scholarixglobal.com

# 3. Install compatibility module (Odoo CLI)
cd /opt/odoo
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -i crm_ai_field_compatibility --stop-after-init

# 4. Restart Odoo
sudo systemctl restart odoo

# 5. Clear asset cache
rm -rf /var/lib/odoo/.local/share/Odoo/filestore/scholarix_db/assets/*

# 6. Verify - Check logs
tail -f /var/log/odoo/odoo.log | grep -i "ai_enrichment"
```

**What This Does**:
- ✅ Adds `ai_enrichment_report` field as computed field
- ✅ Prevents OwlError on CRM lead forms
- ✅ Coexists with `llm_lead_scoring` if later installed
- ✅ No database migration required
- ✅ CloudPepper-safe implementation

---

### ✅ SOLUTION 2: Upgrade llm_lead_scoring Module (PROPER FIX)

**Time to Fix**: 5-10 minutes
**Risk Level**: MEDIUM
**Rollback**: Module downgrade required

This ensures the module is properly installed with all fields.

**Steps**:
```bash
# 1. SSH to server
ssh user@scholarixglobal.com

# 2. Verify module exists
ls -la /opt/odoo/addons/llm_lead_scoring/

# 3. Upgrade module
cd /opt/odoo
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -u llm_lead_scoring --stop-after-init

# 4. If not installed, install it
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -i llm_lead_scoring --stop-after-init

# 5. Restart Odoo
sudo systemctl restart odoo

# 6. Clear browser cache
# Tell users: Ctrl + Shift + R (hard refresh)

# 7. Verify installation via Odoo UI
# Go to: Apps → Search "LLM Lead Scoring" → Should show "Installed"
```

**What This Does**:
- ✅ Properly installs/upgrades `llm_lead_scoring` module
- ✅ Creates database schema for all AI fields
- ✅ Enables full AI lead scoring features
- ✅ Ensures field definitions match view references

---

### ✅ SOLUTION 3: Remove Field from View (TEMPORARY WORKAROUND)

**Time to Fix**: 2 minutes
**Risk Level**: LOW
**Rollback**: Restore XML file

This hides the field from the view temporarily.

**Steps**:
```bash
# 1. SSH to server
ssh user@scholarixglobal.com

# 2. Backup view file
cp /opt/odoo/addons/llm_lead_scoring/views/crm_lead_views.xml \
   /opt/odoo/addons/llm_lead_scoring/views/crm_lead_views.xml.backup

# 3. Edit view to comment out field
nano /opt/odoo/addons/llm_lead_scoring/views/crm_lead_views.xml

# 4. Comment out line 37:
# <!-- TEMPORARY FIX: Commented until module upgrade -->
# <!-- <field name="ai_enrichment_report" ... /> -->

# 5. Upgrade view
cd /opt/odoo
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -u llm_lead_scoring --stop-after-init

# 6. Restart Odoo
sudo systemctl restart odoo
```

**What This Does**:
- ✅ Removes field reference from view
- ✅ Prevents OwlError immediately
- ⚠️ Hides AI enrichment report from users
- ⚠️ Temporary solution only

---

## VERIFICATION CHECKLIST

After applying any solution, verify:

### 1. Error Resolution
```bash
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo.log | grep -E "ERROR|OwlError|ai_enrichment"

# Should see NO errors related to ai_enrichment_report
```

### 2. CRM Lead Form Loading
```
1. Navigate to: CRM → Leads → Any Lead
2. Open lead form
3. Verify form loads WITHOUT OwlError
4. Check browser console (F12) for JavaScript errors
5. Confirm all fields visible and functional
```

### 3. Field Visibility
```
If using Solution 1 (Compatibility Module):
- Field will show placeholder text: "AI Enrichment not available"

If using Solution 2 (Module Upgrade):
- Field should be functional with "Run AI enrichment" button

If using Solution 3 (Remove Field):
- Field will not be visible (expected)
```

### 4. Performance Check
```bash
# Monitor server resources
top -u odoo

# Check database connections
sudo -u postgres psql -d scholarix_db -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Verify no memory leaks
free -h
```

---

## POST-FIX ACTIONS

### Immediate (Within 1 hour)
- [ ] Monitor error logs continuously
- [ ] Test CRM lead creation/editing
- [ ] Verify user reports of issue resolution
- [ ] Document which solution was applied

### Short-term (Within 24 hours)
- [ ] Plan permanent fix if using temporary workaround
- [ ] Install `llm_lead_scoring` properly if using compatibility module
- [ ] Update deployment documentation
- [ ] Brief support team on fix status

### Long-term (Within 1 week)
- [ ] Review why module wasn't installed/upgraded
- [ ] Implement module dependency checks in deployment pipeline
- [ ] Add field existence validation to CI/CD
- [ ] Create monitoring alerts for similar errors

---

## ROLLBACK PROCEDURES

### If Solution 1 Causes Issues:
```bash
# Uninstall compatibility module
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -u crm_ai_field_compatibility --stop-after-init

# Or remove from filesystem
rm -rf /opt/odoo/addons/crm_ai_field_compatibility/
```

### If Solution 2 Causes Issues:
```bash
# Downgrade/uninstall llm_lead_scoring
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -u llm_lead_scoring --stop-after-init

# Restore database backup (if you made one)
sudo -u postgres pg_restore -d scholarix_db /path/to/backup.sql
```

### If Solution 3 Causes Issues:
```bash
# Restore original view file
cp /opt/odoo/addons/llm_lead_scoring/views/crm_lead_views.xml.backup \
   /opt/odoo/addons/llm_lead_scoring/views/crm_lead_views.xml

# Upgrade module
./odoo-bin -c /etc/odoo/odoo.conf -d scholarix_db -u llm_lead_scoring --stop-after-init
```

---

## PREVENTION FOR FUTURE

### 1. Pre-Deployment Validation
Add to deployment checklist:
```bash
# Validate all view field references exist in models
python validate_module.py llm_lead_scoring/
python validate_production_ready.py
```

### 2. Module Dependency Check
```python
# In deployment script, verify dependencies
def check_module_dependencies(module_name):
    manifest = read_manifest(module_name)
    for dep in manifest['depends']:
        if not is_module_installed(dep):
            raise Exception(f"Dependency {dep} not installed!")
```

### 3. Field Existence Validation
```sql
-- Add to database validation script
SELECT 
    c.relname AS table_name,
    a.attname AS column_name
FROM pg_class c
JOIN pg_attribute a ON a.attrelid = c.oid
WHERE c.relname = 'crm_lead'
AND a.attname = 'ai_enrichment_report';

-- Should return 1 row if field exists
```

---

## RECOMMENDED SOLUTION

**For Immediate Production Fix**: Use **Solution 1** (Compatibility Module)
- Fastest to deploy (2-5 minutes)
- Lowest risk
- Easy rollback
- Doesn't affect existing data
- Allows proper fix to be planned

**For Proper Long-term Fix**: Use **Solution 2** (Module Upgrade)
- Enables full AI features
- Proper database schema
- Maintains module integrity
- Should be done after emergency fix

---

## CONTACT INFORMATION

**Escalation Path**:
1. Check error logs first
2. Apply Solution 1 (Compatibility Module)
3. If issues persist, contact development team
4. If critical, engage emergency response team

**Log Locations**:
- Odoo Server: `/var/log/odoo/odoo.log`
- Nginx: `/var/log/nginx/error.log`
- PostgreSQL: `/var/log/postgresql/postgresql-*.log`

---

## SUMMARY

✅ **Compatibility module created**: `crm_ai_field_compatibility/`
✅ **Emergency fix available**: Deploy immediately to production
✅ **Multiple solutions provided**: Choose based on urgency and risk tolerance
✅ **Verification steps documented**: Ensure fix works correctly
✅ **Rollback procedures ready**: Safety net if issues arise
✅ **Prevention measures identified**: Avoid similar issues in future

**Recommended Action**: Deploy Solution 1 NOW, then plan Solution 2 for next maintenance window.

---

*Last Updated: November 29, 2025*
*Emergency Response: Odoo 17 Agent*
