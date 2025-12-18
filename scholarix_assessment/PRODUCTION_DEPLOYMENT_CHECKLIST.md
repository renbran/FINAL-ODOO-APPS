# 🚀 SCHOLARIX Assessment - Production Deployment Checklist

**Module Version:** 17.0.2.0.0  
**Deployment Date:** _____________  
**Deployed By:** _____________

---

## ✅ PRE-DEPLOYMENT VERIFICATION (COMPLETED)

### 1. Code Quality ✓
- [x] All Python files lint-clean (lazy logging, no unused imports)
- [x] All XML files validated (no deprecated `attrs` syntax)
- [x] Odoo 17 compliance verified across all views
- [x] No syntax errors in models, controllers, views
- [x] Exception handling uses specific exception types
- [x] All logging uses lazy % formatting

### 2. Models & Data ✓
- [x] 7 models defined with proper inheritance:
  - `assessment.candidate` (portal, mail.thread, mail.activity.mixin)
  - `assessment.response` (mail.thread)
  - `assessment.ai.score` (with AI integration)
  - `assessment.human.review` (mail.thread, mail.activity.mixin)
  - `assessment.ranking` (computed leaderboard)
  - `assessment.question` (10 questions configured)
  - `assessment.audit.log` (audit trail)
- [x] All required fields defined with proper constraints
- [x] State machines validated (draft → submitted → ai_scored → reviewed)
- [x] Computed fields tested (_compute methods working)
- [x] Access tokens implemented for portal access

### 3. Security ✓
- [x] Security groups defined (Viewer, Reviewer, Manager)
- [x] Access rights CSV complete (27 entries)
- [x] Record rules implemented for all models
- [x] Public/portal access configured correctly
- [x] Multi-tier permissions hierarchy working

### 4. Views ✓
- [x] 12 view files validated:
  - Candidate views (tree, form, kanban, search, dashboard)
  - Response views (form, tree with responses)
  - AI Score views (form with analysis)
  - Human Review views (form with chatter)
  - Ranking views (leaderboard)
  - Question views (configuration)
  - **Audit Log views (NEW - complete)**
- [x] All views use modern Odoo 17 syntax (invisible, required, readonly)
- [x] Status badges display correctly
- [x] Smart buttons functional
- [x] Chatter integration working

### 5. Portal & Public Access ✓
- [x] Assessment landing page (`/assessment`)
- [x] Assessment form (`/assessment/start`)
- [x] View results page (`/assessment/view/<token>`)
- [x] Thank you page (`/assessment/thank-you`)
- [x] Portal templates responsive and styled
- [x] Access token system functional

### 6. Reports ✓
- [x] PDF report action defined (`action_report_assessment_candidate`)
- [x] QWeb report template created
- [x] Report generates successfully
- [x] Branding consistent (Deep Ocean theme)

### 7. Integrations ✓
- [x] AI scoring with Anthropic Claude 3.5 Sonnet
- [x] OpenAI GPT-4 fallback configured
- [x] Email notifications (confirmation, status changes)
- [x] Mail templates defined
- [x] Cron jobs configured for automated tasks

### 8. Data Migration ✓
- [x] **Post-installation hook created** (`hooks.py`)
- [x] Candidate status migration logic implemented
- [x] Access token generation for existing records
- [x] Hook registered in `__manifest__.py`
- [x] Migration tested in development

---

## 📋 DEPLOYMENT STEPS

### Step 1: Backup (CRITICAL - DO FIRST!)
```bash
# SSH to production server
ssh renbran@147.79.119.151

# Backup database
pg_dump -U odoo scholarixv2 > ~/backups/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup created
ls -lh ~/backups/scholarixv2_backup_*.sql

# Backup Odoo custom addons (optional)
tar -czf ~/backups/scholarix_assessment_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/odoo/scholarixv2/scholarix_assessment/
```
**Status:** [ ] Completed - Backup file: _____________

---

### Step 2: Pull Latest Code
```bash
# Navigate to module directory
cd /var/odoo/scholarixv2/scholarix_assessment

# Pull from GitHub
git pull origin main

# Verify latest commit
git log -1 --oneline
# Should show: 9bb4b43c9 🔧 Code quality improvements for production deployment
```
**Status:** [ ] Completed - Commit: _____________

---

### Step 3: Verify Dependencies
```bash
# Activate virtual environment
source /var/odoo/scholarixv2/venv/bin/activate

# Check Python packages
pip list | grep -E "openai|anthropic|tiktoken|numpy|pandas"

# Install if missing
pip install openai anthropic tiktoken numpy pandas
```
**Status:** [ ] Completed

---

### Step 4: Upgrade Module (This runs migration hook!)
```bash
# Stop Odoo service
sudo systemctl stop odoo

# Run module upgrade (this executes post_init_hook)
/var/odoo/scholarixv2/venv/bin/python3 /var/odoo/scholarixv2/odoo-bin \
  -c /etc/odoo.conf \
  -d scholarixv2 \
  -u scholarix_assessment \
  --stop-after-init

# Check for errors
echo $?  # Should be 0
```
**Status:** [ ] Completed - Exit code: _____________

---

### Step 5: Check Migration Logs
```bash
# View upgrade logs
tail -200 /var/log/odoo/odoo.log | grep -A 10 "Migration"

# Should see:
# - "Running post-installation hook for scholarix_assessment..."
# - "Migrating candidate status..."
# - "Migrated status for X candidates"
# - "Ensuring access tokens..."
# - "Post-installation hook completed successfully"
```
**Status:** [ ] Completed - Records migrated: _____________

---

### Step 6: Restart Odoo
```bash
# Start Odoo service
sudo systemctl start odoo

# Check service status
sudo systemctl status odoo

# Monitor logs in real-time
tail -f /var/log/odoo/odoo.log
```
**Status:** [ ] Completed

---

### Step 7: Verify Database State
```bash
# Connect to database
sudo -u postgres psql scholarixv2

# Check module installed correctly
SELECT state, latest_version FROM ir_module_module 
WHERE name = 'scholarix_assessment';
-- Should show: installed | 17.0.2.0.0

# Check candidate status migration
SELECT status, COUNT(*) FROM assessment_candidate 
GROUP BY status;

# Check access tokens generated
SELECT COUNT(*) FROM assessment_candidate WHERE access_token IS NULL;
-- Should be 0

# Check report action registered
SELECT id, name FROM ir_actions_report 
WHERE model = 'assessment.candidate';
-- Should show: action_report_assessment_candidate

# Exit psql
\q
```
**Status:** [ ] Completed

---

## 🧪 POST-DEPLOYMENT TESTING

### Test 1: Backend Access
- [ ] Login to Odoo backend: https://scholarixglobal.com
- [ ] Navigate to Assessment menu
- [ ] Verify all menu items visible:
  - [ ] Candidates
  - [ ] Responses
  - [ ] AI Scores
  - [ ] Human Reviews
  - [ ] Rankings
  - [ ] Questions
  - [ ] **Audit Logs (NEW)**
  - [ ] Dashboard

### Test 2: View Existing Data
- [ ] Open Candidates list view
- [ ] Verify status badges display correctly
- [ ] Check old candidates have proper status (not draft/empty)
- [ ] Open a candidate form
- [ ] Verify all fields display correctly
- [ ] Check smart buttons work (Responses, AI Scores, Reviews)

### Test 3: Human Review Workflow
- [ ] Open a Human Review record
- [ ] Verify chatter is visible at bottom
- [ ] Test "Submit Review" button
- [ ] Test "View Candidate" button
- [ ] Check mail logging works

### Test 4: Audit Log
- [ ] Navigate to Assessment → Audit Logs
- [ ] Verify audit records display
- [ ] Test filters (action type, date ranges)
- [ ] Open an audit log entry
- [ ] Verify all fields show correctly

### Test 5: PDF Report Generation
- [ ] Open a candidate record
- [ ] Click "Print" → "Assessment Report"
- [ ] Verify PDF generates without errors
- [ ] Check PDF content is correct
- [ ] Verify branding appears correctly

### Test 6: Portal Access (Public)
- [ ] Open incognito browser
- [ ] Navigate to: https://scholarixglobal.com/assessment
- [ ] Verify landing page loads
- [ ] Click "Start Assessment"
- [ ] Verify assessment form loads with 10 questions
- [ ] Submit a test assessment
- [ ] Verify thank you page displays
- [ ] Check access token sent via email

### Test 7: AI Scoring
- [ ] After test submission, check backend
- [ ] Verify candidate status changed to "AI Scored"
- [ ] Open AI Score record
- [ ] Verify all scoring categories populated
- [ ] Check overall score calculated
- [ ] Verify AI recommendations present

### Test 8: Email Notifications
- [ ] Check email sent to test candidate
- [ ] Verify access token link works
- [ ] Click link to view results
- [ ] Verify results page displays correctly

### Test 9: Dashboard & Analytics
- [ ] Navigate to Assessment Dashboard
- [ ] Verify statistics display
- [ ] Check charts render correctly
- [ ] Test filters and date ranges

### Test 10: Permissions
- [ ] Test as Viewer user (read-only)
- [ ] Test as Reviewer user (can review)
- [ ] Test as Manager user (full access)
- [ ] Verify record rules enforced

---

## 🔍 TROUBLESHOOTING GUIDE

### Issue: Module won't upgrade
**Symptoms:** Upgrade command fails
**Solution:**
```bash
# Check Odoo logs
tail -100 /var/log/odoo/odoo.log

# Common causes:
# - Syntax errors in Python/XML
# - Missing dependencies
# - Database constraint violations

# Try with verbose logging
/var/odoo/scholarixv2/venv/bin/python3 /var/odoo/scholarixv2/odoo-bin \
  -c /etc/odoo.conf -d scholarixv2 -u scholarix_assessment \
  --log-level=debug --stop-after-init 2>&1 | tee upgrade.log
```

### Issue: PDF report not found
**Symptoms:** "action_report_assessment_candidate not found"
**Solution:**
```sql
-- Check if report action exists
SELECT * FROM ir_actions_report WHERE model = 'assessment.candidate';

-- If missing, module needs upgrade
-- Or manually load report XML:
-- Update module via UI: Apps → SCHOLARIX Assessment System → Upgrade
```

### Issue: Old candidates have no status
**Symptoms:** Candidates show blank status
**Solution:**
```sql
-- Check migration ran
SELECT * FROM ir_logging WHERE name LIKE '%Migration%' 
ORDER BY create_date DESC LIMIT 10;

-- If migration didn't run, trigger manually:
-- In Odoo: Settings → Technical → Automation → Python Code
-- Run: env['assessment.candidate'].search([])._migrate_status()
```

### Issue: Access tokens missing
**Symptoms:** Portal links don't work for old submissions
**Solution:**
```sql
-- Count candidates without tokens
SELECT COUNT(*) FROM assessment_candidate WHERE access_token IS NULL;

-- Generate tokens manually if needed (in Odoo shell):
-- candidates = env['assessment.candidate'].search([('access_token', '=', False)])
-- for c in candidates: c._generate_access_token()
```

### Issue: Audit logs not appearing
**Symptoms:** Audit Logs menu item missing or empty
**Solution:**
```bash
# Verify views loaded
grep -r "action_assessment_audit_log" /var/odoo/scholarixv2/scholarix_assessment/

# Upgrade module to load views
odoo-bin -c /etc/odoo.conf -d scholarixv2 -u scholarix_assessment --stop-after-init

# Clear browser cache and refresh
```

---

## 📊 ROLLBACK PROCEDURE (IF NEEDED)

### If deployment fails critically:

**1. Stop Odoo:**
```bash
sudo systemctl stop odoo
```

**2. Restore Database:**
```bash
# Drop current database (CAUTION!)
sudo -u postgres dropdb scholarixv2

# Restore from backup
sudo -u postgres createdb scholarixv2
sudo -u postgres psql scholarixv2 < ~/backups/scholarixv2_backup_YYYYMMDD_HHMMSS.sql
```

**3. Revert Code:**
```bash
cd /var/odoo/scholarixv2/scholarix_assessment
git log -5 --oneline  # Find previous commit
git reset --hard <previous-commit-hash>
```

**4. Restart Odoo:**
```bash
sudo systemctl start odoo
```

**5. Notify Team:**
- Document what went wrong
- Create incident report
- Plan fixes before retry

---

## ✅ FINAL SIGN-OFF

### Deployment Successful
- [ ] All tests passed
- [ ] No critical errors in logs
- [ ] Users can access system
- [ ] Core workflows functional
- [ ] Performance acceptable

### Production Verification
- [ ] Monitor for 1 hour post-deployment
- [ ] Check error logs: `tail -f /var/log/odoo/odoo.log`
- [ ] Verify no spike in error rate
- [ ] Test user feedback collected

### Documentation
- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Update module documentation if needed
- [ ] Notify stakeholders of successful deployment

---

## 📞 SUPPORT CONTACTS

**Technical Lead:** Brandon Moreno  
**Email:** recruitment@scholarixglobal.com  
**Emergency:** [Contact Number]

**GitHub Repository:** https://github.com/renbran/OSUSAPPS  
**Latest Commit:** 9bb4b43c9

---

## 🎯 SUCCESS CRITERIA

✅ **Module upgraded successfully** (Version 17.0.2.0.0)  
✅ **All 7 models accessible** (Candidate, Response, AI Score, Human Review, Ranking, Question, Audit Log)  
✅ **All 12 view sets functional** (including new Audit Log views)  
✅ **Security working** (3 groups, 27 access rights, record rules)  
✅ **Portal accessible** (Public assessment form, results viewing)  
✅ **Reports generating** (PDF candidate assessment reports)  
✅ **AI integration active** (Claude/GPT scoring)  
✅ **Email notifications sent** (Confirmation, status changes)  
✅ **Data migration completed** (Old candidates have proper status & tokens)  
✅ **Audit logging functional** (All changes tracked)  
✅ **Zero critical errors** (Clean logs)

---

**Deployment Completed:** [ ] YES [ ] NO  
**Signed By:** ________________________  
**Date:** _____________  
**Time:** _____________

---

*This checklist ensures a safe, verified production deployment with rollback capability.*
