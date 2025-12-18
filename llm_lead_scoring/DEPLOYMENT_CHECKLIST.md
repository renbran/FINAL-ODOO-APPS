# 🚀 Quick Deployment Checklist - Google Custom Search Integration

## ✅ Pre-Deployment Verification

- [ ] All files created/modified (see GOOGLE_INTEGRATION_IMPLEMENTATION_SUMMARY.md)
- [ ] No syntax errors in Python files
- [ ] No XML validation errors (except non-critical warnings)
- [ ] Security access rules added
- [ ] README.md updated
- [ ] Documentation complete (GOOGLE_CUSTOM_SEARCH_SETUP.md)

## 📋 Files to Deploy

### New Files (8):
```
llm_lead_scoring/
├── models/web_research_service.py                        [NEW]
├── wizards/google_search_setup_wizard.py                 [NEW]
├── wizards/google_search_setup_wizard_views.xml          [NEW]
├── GOOGLE_CUSTOM_SEARCH_SETUP.md                         [NEW]
├── GOOGLE_INTEGRATION_IMPLEMENTATION_SUMMARY.md          [NEW]
└── DEPLOYMENT_CHECKLIST.md                               [NEW]
```

### Modified Files (8):
```
llm_lead_scoring/
├── models/__init__.py                                    [MODIFIED]
├── models/llm_service.py                                 [MODIFIED]
├── models/res_config_settings.py                         [MODIFIED]
├── views/res_config_settings_views.xml                   [MODIFIED]
├── wizards/__init__.py                                   [MODIFIED]
├── __manifest__.py                                       [MODIFIED]
├── security/ir.model.access.csv                          [MODIFIED]
└── README.md                                             [MODIFIED]
```

## 🔧 Deployment Steps

### 1. Backup (5 minutes)
```bash
# SSH to production server
ssh user@139.84.163.11

# Backup database
pg_dump -U odoo scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup module
tar -czf /tmp/llm_lead_scoring_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/odoo/addons/llm_lead_scoring/
```

### 2. Upload Files (5 minutes)
```bash
# From local machine
cd "d:\RUNNING APPS\FINAL-ODOO-APPS"

# Upload entire module directory
scp -r llm_lead_scoring/ user@139.84.163.11:/opt/odoo/addons/

# OR if using git:
ssh user@139.84.163.11
cd /opt/odoo/addons/FINAL-ODOO-APPS/
git pull origin main
```

### 3. Update Module (10 minutes)
```bash
# On production server
sudo systemctl stop odoo

# Update module
/usr/bin/odoo -u llm_lead_scoring -d scholarixv2 --stop-after-init --log-level=info

# Check output for errors
# Look for: "Module llm_lead_scoring updated successfully"

# If errors, check logs:
# tail -f /var/log/odoo/odoo-server.log
```

### 4. Restart Service (2 minutes)
```bash
# Start Odoo
sudo systemctl start odoo

# Verify service running
sudo systemctl status odoo

# Monitor logs for errors
tail -f /var/log/odoo/odoo-server.log
```

### 5. Post-Deployment Verification (5 minutes)
```bash
# Check new configuration parameters exist
psql -U odoo scholarixv2 -c "SELECT * FROM ir_config_parameter WHERE key LIKE '%google%';"

# Expected output: 3 rows (enable_web_research, google_search_api_key, google_search_engine_id)

# Check module version
psql -U odoo scholarixv2 -c "SELECT name, latest_version, state FROM ir_module_module WHERE name = 'llm_lead_scoring';"

# Check security access
psql -U odoo scholarixv2 -c "SELECT id, name, model_id FROM ir_model_access WHERE model_id IN (SELECT id FROM ir_model WHERE model IN ('web.research.service', 'google.search.setup.wizard'));"
```

### 6. Web Interface Test (10 minutes)

**Test 1: Settings Page**
- [ ] Login to Odoo: https://stagingtry.cloudpepper.site/
- [ ] Go to: Settings → CRM → LLM Lead Scoring
- [ ] Verify "Web Research Configuration" section visible
- [ ] Verify "Setup Guide" button present
- [ ] Verify toggle, API key field, Search Engine ID field visible

**Test 2: Setup Wizard**
- [ ] Click "Setup Guide" button
- [ ] Wizard opens with Step 1 (Introduction)
- [ ] Click "Next" → Step 2 (API Key)
- [ ] Paste test API key: `test_key_123`
- [ ] Click "Next" → Step 3 (Search Engine)
- [ ] Paste test ID: `test_engine_123`
- [ ] Click "Next" → Step 4 (Test)
- [ ] (Test will fail with test credentials - expected)
- [ ] Click "Cancel" to close wizard
- [ ] Configuration NOT saved (as expected with cancel)

**Test 3: Manual Configuration**
- [ ] Go to: Settings → CRM → LLM Lead Scoring
- [ ] Enable "Live Web Research" toggle
- [ ] Paste REAL Google API key
- [ ] Paste REAL Search Engine ID
- [ ] Click "Save"
- [ ] Verify settings saved (page reloads, values retained)

**Test 4: Lead Enrichment**
- [ ] Go to: CRM → Leads
- [ ] Create test lead:
  - Name: "Microsoft Corporation"
  - Email: sales@microsoft.com
  - Website: microsoft.com
  - Description: "Interested in enterprise solutions"
- [ ] Click "AI Enrich" button
- [ ] Wait 10-15 seconds
- [ ] Check internal note/chatter
- [ ] Verify "🌐 Live Web Research Results" section appears
- [ ] Verify recent data from 2024-2025
- [ ] Verify sources listed

**Test 5: Fallback (Disable Web Research)**
- [ ] Go to: Settings → CRM → LLM Lead Scoring
- [ ] Disable "Live Web Research" toggle
- [ ] Save
- [ ] Create another test lead
- [ ] Click "AI Enrich"
- [ ] Verify NO web research section (original LLM research only)
- [ ] Re-enable "Live Web Research" toggle

## 🧪 Production Testing Scenarios

### Test Case 1: Recent Company (Critical)
```
Lead Details:
- Name: "Anthropic AI"
- Email: sales@anthropic.com
- Website: anthropic.com
- Description: "Looking for AI safety solutions"

Expected Results:
✅ Company founded 2021
✅ Recent news about Claude 3 (2024)
✅ Funding information (Series C, 2024)
✅ Product details (Claude AI models)
✅ Sources: anthropic.com, techcrunch.com, etc.

Success Criteria:
- Data from 2024 present
- Multiple sources cited
- Enrichment completes in <20 seconds
```

### Test Case 2: Quota Tracking
```
Steps:
1. Check initial quota: Odoo logs → "Google Custom Search quota: 0/100"
2. Enrich 5 leads (2-3 queries each)
3. Check updated quota: Should show 10-15/100
4. Verify quota increments correctly

Success Criteria:
- Quota tracking accurate
- Quota persists across server restarts
- Quota resets daily (test next day)
```

### Test Case 3: Error Handling
```
Scenario A: Invalid API Key
1. Settings → Paste invalid key → Save
2. Try enriching lead
3. Expected: Error message + fallback to LLM knowledge
4. Success: No crash, enrichment completes

Scenario B: Quota Exceeded
1. Manually set quota to 100 in database
2. Try enriching lead
3. Expected: Warning message + fallback to LLM knowledge
4. Success: No crash, enrichment completes

Scenario C: Network Timeout
(Difficult to test, monitor in production)
Expected: 30-second timeout → fallback to LLM
```

## 🔍 Monitoring (First 24 Hours)

### Log Monitoring Commands:
```bash
# Watch for Google API errors
tail -f /var/log/odoo/odoo-server.log | grep -i "google"

# Check quota usage
grep "quota" /var/log/odoo/odoo-server.log | tail -20

# Monitor enrichment times
grep "AI Enrich" /var/log/odoo/odoo-server.log | tail -50

# Check for errors
grep "ERROR\|WARNING" /var/log/odoo/odoo-server.log | tail -100
```

### Database Monitoring:
```sql
-- Check configuration
SELECT key, value FROM ir_config_parameter WHERE key LIKE '%google%';

-- Check daily quota usage
SELECT value FROM ir_config_parameter WHERE key = 'google_search_daily_quota';

-- Enrichment statistics (last 24 hours)
SELECT 
    COUNT(*) as total_leads,
    COUNT(ai_enrichment_data) as enriched_leads,
    COUNT(CASE WHEN ai_enrichment_data::text LIKE '%Live Web Research%' THEN 1 END) as web_researched_leads,
    AVG(ai_probability_score) as avg_score
FROM crm_lead
WHERE write_date >= CURRENT_TIMESTAMP - INTERVAL '24 hours';
```

### Performance Metrics:
```
Target Metrics:
- Enrichment time: <20 seconds (with web research)
- API success rate: >95%
- Quota usage: <100/day (free tier)
- User satisfaction: Positive feedback on data freshness

Monitor:
- Error rate in logs
- Enrichment completion rate
- User adoption (# of enrichments/day)
- Web research vs LLM fallback ratio
```

## 🚨 Rollback Plan (If Issues Occur)

### Quick Rollback (5 minutes):
```bash
# Stop Odoo
sudo systemctl stop odoo

# Restore database
psql -U odoo scholarixv2 < /tmp/scholarixv2_backup_YYYYMMDD_HHMMSS.sql

# Restore module files
cd /opt/odoo/addons/
rm -rf llm_lead_scoring/
tar -xzf /tmp/llm_lead_scoring_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/odoo/addons/

# Restart Odoo
sudo systemctl start odoo
```

### Partial Rollback (Disable Feature Only):
```bash
# Disable web research via database (no downtime)
psql -U odoo scholarixv2 -c "UPDATE ir_config_parameter SET value='False' WHERE key='llm_lead_scoring.enable_web_research';"

# Users will immediately use LLM fallback (no web research)
# No module update needed
```

## 📊 Success Criteria

### Deployment Successful If:
- ✅ Module updates without errors
- ✅ Odoo service starts and runs normally
- ✅ Settings page shows new "Web Research Configuration" section
- ✅ Setup wizard accessible and functional
- ✅ Manual configuration saves correctly
- ✅ Lead enrichment works with web research enabled
- ✅ Fallback to LLM works when web research disabled
- ✅ No critical errors in logs
- ✅ Security access rules working (salespeople can enrich, managers can configure)

### Production Ready If:
- ✅ Real Google API credentials configured
- ✅ Test enrichments return recent data (2024-2025)
- ✅ Quota tracking accurate
- ✅ Error handling graceful (no crashes)
- ✅ Performance acceptable (<20 seconds)
- ✅ User feedback positive

## 📞 Support Contacts

**If deployment issues occur:**

1. **Check Odoo Logs:**
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

2. **Check Module Status:**
   ```sql
   SELECT name, state, latest_version FROM ir_module_module WHERE name = 'llm_lead_scoring';
   ```

3. **Emergency Disable:**
   ```sql
   UPDATE ir_config_parameter SET value='False' WHERE key='llm_lead_scoring.enable_web_research';
   ```

4. **Rollback:** See "Rollback Plan" section above

## ✅ Final Checklist

**Before Deployment:**
- [ ] All files committed to git (if using version control)
- [ ] Backup created (database + module files)
- [ ] Testing plan prepared
- [ ] Rollback plan ready
- [ ] Stakeholders notified

**During Deployment:**
- [ ] Module updated successfully
- [ ] No errors in Odoo logs
- [ ] Service restarted properly
- [ ] Database verification passed

**After Deployment:**
- [ ] Settings page tested
- [ ] Setup wizard tested
- [ ] Lead enrichment tested
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Users notified of new feature
- [ ] Monitoring in place (24-48 hours)

**Sign-Off:**
- [ ] Technical team approves deployment
- [ ] Sales team trained on new feature
- [ ] Documentation updated
- [ ] Feature announced to users

---

## 🎯 Timeline

**Total Deployment Time: ~45 minutes**

| Phase | Time | Status |
|-------|------|--------|
| Backup | 5 min | ⏳ |
| Upload Files | 5 min | ⏳ |
| Update Module | 10 min | ⏳ |
| Restart Service | 2 min | ⏳ |
| Verification | 5 min | ⏳ |
| Web Testing | 10 min | ⏳ |
| Production Tests | 8 min | ⏳ |

**Monitoring Period: 24-48 hours**

---

## 📝 Post-Deployment Notes

**Record:**
- Deployment date/time: ____________________
- Deployed by: ____________________
- Module version: 17.0.1.0.0 (with Google Custom Search)
- Issues encountered: ____________________
- Resolution: ____________________
- User feedback: ____________________

**Next Steps:**
1. Monitor for 24-48 hours
2. Collect user feedback
3. Optimize based on usage patterns
4. Consider paid tier if quota exceeded regularly
5. Document lessons learned
6. Plan next enhancements (see IMPROVEMENT_ROADMAP.md)

---

**Deployment Status:** ⏳ **READY TO DEPLOY**

**Confidence Level:** ✅ **HIGH** (All files validated, comprehensive testing plan prepared)

**Risk Level:** 🟢 **LOW** (Graceful fallback, easy rollback, non-breaking changes)

---

*Last Updated: November 29, 2025*  
*Ready for Production Deployment*
