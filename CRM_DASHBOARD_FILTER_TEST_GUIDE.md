# CRM Dashboard Filter Testing Guide

## 🎯 Quick Access
**URL:** https://stagingtry.cloudpepper.site/  
**Path:** CRM → Dashboard  
**Login:** salescompliance@osusproperties.com

---

## ✅ Pre-Flight Check

Before testing filters, verify these dashboard elements are visible:

### Tiles (Top Row)
- [ ] **Leads Count:** Should show **1,145**
- [ ] **Opportunities Count:** Should show **3,823**
- [ ] **Expected Revenue:** Should show **~$356.6M**
- [ ] **Won Revenue:** Should show **~$6.8M**
- [ ] **Won/Lost Ratio:** Should show **50:34** or **1.47**

### Charts (Middle Section)
- [ ] **Annual Target vs YTD Bar Chart** - Shows comparison
- [ ] **Revenue Pie Chart** - Three segments (Expected/Won/Lost)
- [ ] **Monthly Goal Gauge** - Shows percentage progress
- [ ] **Lead Stage Funnel** - 12 stages with opportunity counts

### Tables (Bottom Section)
- [ ] **Top 10 Deals** - Sorted by revenue
- [ ] **Upcoming Activities** - Shows activities (38 due today)
- [ ] **Lead Details by User** - Shows 9+ users with counts

---

## 🔧 Filter Testing Scenarios

### Scenario 1: Date Range Filter
**Purpose:** Verify dashboard updates based on date selections

1. **Test: Current Month Filter**
   - Select: "This Month" from date filter
   - Expected: All widgets update to show only current month data
   - Verify: Opportunity count decreases, revenue adjusts

2. **Test: Custom Date Range**
   - Select: Custom date range (e.g., Last 90 Days)
   - Expected: Dashboard shows only opportunities in that range
   - Verify: Charts redraw, tables refresh

3. **Test: Year-to-Date**
   - Select: "Year to Date" option
   - Expected: Annual Target chart should be most relevant
   - Verify: YTD comparison matches expectations

**Expected Behavior:**
- ✅ All tiles update simultaneously
- ✅ Charts animate to new values
- ✅ Tables show filtered records only
- ✅ No console errors

---

### Scenario 2: User Filter
**Purpose:** Verify user-specific data filtering

1. **Test: Single User Selection**
   - Select: "info@scholarixglobal.com" (highest pipeline)
   - Expected Results:
     - Opportunities: ~967
     - Revenue: ~$118M
     - Only this user's opportunities shown

2. **Test: Multiple User Selection**
   - Select: 2-3 users (e.g., info@scholarixglobal.com + abhishek.b@scholarixit.com)
   - Expected: Combined data for selected users
   - Verify: Sum matches individual totals

3. **Test: Current User Only**
   - Select: "My Opportunities" or current user
   - Expected: Shows only opportunities assigned to logged-in user
   - Verify: Other users' data hidden

**Expected Behavior:**
- ✅ User dropdown populates with all sales users
- ✅ Multi-select works correctly
- ✅ "All Users" option resets filter
- ✅ User count matches database (9+ users with targets)

---

### Scenario 3: Team Filter
**Purpose:** Verify team-based filtering

1. **Test: Single Team Selection**
   - Select: A sales team from dropdown
   - Expected: Shows only opportunities for that team
   - Verify: Team members' data aggregated

2. **Test: No Team Filter**
   - Select: "All Teams"
   - Expected: Shows all opportunities regardless of team
   - Verify: Counts match overall totals

3. **Test: Team + User Combination**
   - Select: A team + specific user in that team
   - Expected: Intersection of both filters
   - Verify: Data consistent with both conditions

**Expected Behavior:**
- ✅ Team dropdown shows all active sales teams
- ✅ Team filter works independently
- ✅ Combines correctly with other filters
- ✅ "Unassigned" option shows teamless opportunities

---

### Scenario 4: Stage Filter
**Purpose:** Verify stage-based filtering

1. **Test: Early Stage Filter**
   - Select: "New" stage (largest stage with 2,841 opportunities)
   - Expected Results:
     - Opportunities: 2,841
     - Revenue: ~$304M
     - Other stages hidden

2. **Test: Won Stage Filter**
   - Select: "Closed Implementation" (won stage)
   - Expected Results:
     - Opportunities: 51
     - Revenue: ~$6.8M
     - Funnel shows only won stage

3. **Test: Multiple Stages**
   - Select: Multiple stages (e.g., New + Contacted + Follow up)
   - Expected: Combined data from selected stages
   - Verify: Sum equals individual stage totals

4. **Test: Lost Stage**
   - Select: "Not Interested" or lost stages
   - Expected: Shows 69 opportunities, ~$4.1M
   - Verify: Probability = 0 or active = false

**Expected Behavior:**
- ✅ Stage dropdown shows all 12 CRM stages in sequence order
- ✅ Funnel chart highlights selected stages
- ✅ Won/Lost filters affect probability calculations
- ✅ Stage colors consistent with CRM configuration

---

### Scenario 5: Probability Filter
**Purpose:** Verify probability-based filtering

1. **Test: Won Opportunities (100%)**
   - Select: Probability = 100%
   - Expected Results:
     - Count: 50 opportunities
     - Revenue: $6.84M
     - All in "Closed Implementation" stage

2. **Test: Lost Opportunities (0%)**
   - Select: Probability = 0%
   - Expected Results:
     - Count: 34 opportunities
     - Revenue: $0 (or archived)
     - Mostly archived records

3. **Test: Pipeline Opportunities (1-99%)**
   - Select: Probability 1-99%
   - Expected Results:
     - Count: 3,739 opportunities
     - Revenue: $356.6M
     - Active pipeline only

4. **Test: High Probability Range**
   - Select: Probability > 50%
   - Expected: Shows opportunities more likely to close
   - Verify: Higher average revenue per opportunity

**Expected Behavior:**
- ✅ Probability slider or dropdown works smoothly
- ✅ Range selections update dynamically
- ✅ Won/Lost tiles update based on probability
- ✅ Expected revenue excludes won/lost (probability 0% and 100%)

---

### Scenario 6: Active/Archived Toggle
**Purpose:** Verify archived records handling

1. **Test: Active Only (Default)**
   - Ensure: "Active" toggle is ON
   - Expected: Shows 3,739 active opportunities
   - Verify: No archived records visible

2. **Test: Include Archived**
   - Toggle: Show archived records
   - Expected: Count increases to 3,823 total
   - Verify: 84 archived opportunities now visible

3. **Test: Archived Only**
   - Select: "Archived Only" if available
   - Expected: Shows only 84 archived opportunities
   - Verify: All have active = false

**Expected Behavior:**
- ✅ Toggle switch clearly labeled
- ✅ Default state is "Active Only"
- ✅ Archived records visually distinguished
- ✅ Lost opportunities may be archived

---

### Scenario 7: Combined Filters
**Purpose:** Verify multiple filters work together

1. **Test: Date + User + Stage**
   - Select: "This Month" + "info@scholarixglobal.com" + "New" stage
   - Expected: Intersection of all three conditions
   - Verify: Count is subset of each individual filter

2. **Test: User + Team + Probability**
   - Select: Specific user + their team + probability > 50%
   - Expected: High-probability opportunities for user in team
   - Verify: Data consistency across widgets

3. **Test: Date + Stage + Active**
   - Select: Last 90 Days + Won stage + Active only
   - Expected: Recently won opportunities
   - Verify: Date_closed within last 90 days

4. **Test: All Filters Combined**
   - Apply: Date + User + Team + Stage + Probability + Active
   - Expected: Highly specific filtered view
   - Verify: All widgets reflect combined filter logic

**Expected Behavior:**
- ✅ Filters combine with AND logic (intersection)
- ✅ No conflicts between filter types
- ✅ "Reset All Filters" button clears everything
- ✅ URL parameters reflect active filters (for bookmarking)

---

## 🔍 Data Drill-Down Testing

### Test: Click Tiles
1. Click **Opportunities Count** tile
   - Expected: Opens CRM opportunity list view
   - Verify: Filter applied from dashboard
   - Action: Click back/breadcrumb to return

2. Click **Won Revenue** tile
   - Expected: Opens list of won opportunities (probability = 100%)
   - Verify: 50 records, $6.84M total
   - Action: Return to dashboard

### Test: Click Chart Segments
1. Click **Revenue Pie Chart** - "Won" segment
   - Expected: Opens list of won opportunities
   - Verify: Same as clicking Won Revenue tile

2. Click **Stage Funnel** - "New" stage
   - Expected: Opens opportunities in "New" stage
   - Verify: 2,841 records, $304M revenue

### Test: Click Table Rows
1. Click row in **Top 10 Deals** table
   - Expected: Opens opportunity form view
   - Verify: Shows full opportunity details
   - Action: Close or click back

2. Click row in **Lead Details by User** table
   - Expected: Opens filtered list for that user
   - Verify: Shows only selected user's opportunities

---

## ⚡ Performance Testing

### Load Time Benchmarks
- [ ] **Initial Dashboard Load:** < 3 seconds
- [ ] **Filter Application:** < 1 second
- [ ] **Chart Redraw:** < 500ms
- [ ] **Table Refresh:** < 500ms

### Browser Console Check
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Verify:
   - [ ] No JavaScript errors
   - [ ] No 404 resource errors
   - [ ] No CORS errors
   - [ ] No deprecation warnings

### Network Performance
1. Open Network tab in Developer Tools
2. Reload dashboard
3. Verify:
   - [ ] Total load time < 5 seconds
   - [ ] RPC calls complete successfully
   - [ ] No failed requests
   - [ ] Asset files cached on subsequent loads

---

## 🐛 Edge Case Testing

### Test: Empty Filter Results
1. Apply: Combination that yields 0 results
   - Example: Date range in future + Won stage
   - Expected: "No data available" message
   - Verify: Dashboard doesn't break, shows empty state

### Test: Large Dataset Filter
1. Select: "All Users" + "All Teams" + "This Year"
   - Expected: Full dataset (4,968 records)
   - Verify: Dashboard handles large data without timeout
   - Performance: Should still load < 5 seconds

### Test: Rapid Filter Changes
1. Quickly change filters multiple times
   - Example: Toggle between different users rapidly
   - Expected: Dashboard updates smoothly
   - Verify: No race conditions, latest filter wins

### Test: Browser Refresh with Filters
1. Apply: Multiple filters
2. Refresh: Press F5 to reload page
3. Expected: Filters persist (if using URL parameters)
4. Verify: Dashboard shows same filtered view

---

## 📊 Data Accuracy Verification

### Revenue Calculations
- [ ] **Expected Revenue** = Sum of opportunities with 1-99% probability
  - Should equal: $356,586,832.69
  - Excludes: Won (100%) and Lost (0%) opportunities

- [ ] **Won Revenue** = Sum of opportunities with 100% probability
  - Should equal: $6,841,727.08
  - Includes: Only "Closed Implementation" stage

- [ ] **Total Pipeline** = Expected + Won
  - Should equal: $363,428,559.77

### Count Accuracy
- [ ] **Lead Count** = Records with type='lead'
  - Should equal: 1,145

- [ ] **Opportunity Count** = Records with type='opportunity'
  - Should equal: 3,823

- [ ] **Won Count** = Opportunities with probability=100
  - Should equal: 50

- [ ] **Lost Count** = Opportunities with probability=0 and active=false
  - Should equal: 34

### User Performance
- [ ] **Top User by Pipeline:** info@scholarixglobal.com
  - Opportunities: 967
  - Revenue: $118,116,625.95

- [ ] **Top User by Won Deals:** (verify in dashboard)
  - Should show user with most won opportunities

---

## ✅ Final Validation Checklist

### Visual Elements
- [ ] All tiles render correctly
- [ ] Charts display without errors
- [ ] Tables populate with data
- [ ] Colors consistent with branding
- [ ] Icons and labels visible
- [ ] Responsive layout on different screen sizes

### Functionality
- [ ] All filters work independently
- [ ] Combined filters work correctly
- [ ] Reset filters button works
- [ ] Drill-down navigation works
- [ ] Breadcrumb navigation works
- [ ] Export functionality (if available)

### Data Integrity
- [ ] Numbers match database queries
- [ ] Revenue calculations accurate
- [ ] Date filters respect timezone
- [ ] User permissions respected
- [ ] Team visibility rules applied

### Performance
- [ ] Load time acceptable
- [ ] No console errors
- [ ] Smooth animations
- [ ] Responsive interactions
- [ ] No memory leaks (check after extended use)

### User Experience
- [ ] Filter controls intuitive
- [ ] Loading indicators present
- [ ] Error messages helpful
- [ ] Tooltips informative
- [ ] Help documentation accessible

---

## 🚨 Known Issues to Watch For

### Issue 1: Hardcoded Stage ID
- **Symptom:** Won revenue doesn't match expected
- **Cause:** Code uses stage_id=4 instead of is_won=true
- **Current State:** Works correctly because code filters probability=100
- **Action:** If discrepancy found, apply fix from `crm_dashboard_fixes.py`

### Issue 2: Sales Target Field Not Editable
- **Symptom:** Cannot edit sales target in user form
- **Cause:** res_users_views.xml disabled due to compatibility issue
- **Workaround:** Edit via Settings → Users → Sales Target field
- **Impact:** Minor usability issue, no data loss

### Issue 3: Average Conversion Time Bug
- **Symptom:** Average time shows max 86,400 seconds (1 day)
- **Cause:** Code uses `.seconds` instead of `.total_seconds()`
- **Current Impact:** May affect if displayed in dashboard
- **Fix:** Available in `crm_dashboard_fixes.py`

---

## 📞 Support Information

### If Dashboard Doesn't Load
1. Check Odoo service status: `systemctl status odoo-scholarixv2`
2. Check logs: `tail -f /var/odoo/scholarixv2/logs/odoo-server.log`
3. Verify module installed: Check Apps → CRM Dashboard → Installed
4. Clear browser cache and retry

### If Data Looks Wrong
1. Review: `CRM_DASHBOARD_TEST_RESULTS.md` for expected values
2. Run: Database query from `comprehensive_dashboard_test.sql`
3. Compare: Dashboard numbers vs. query results
4. Document: Any discrepancies for investigation

### If Filters Don't Work
1. Check: Browser console for JavaScript errors
2. Verify: User has proper access rights (Sales User or Manager)
3. Test: With admin user to rule out permission issues
4. Clear: Browser cache and retry

---

## 📝 Test Results Template

```
=== CRM DASHBOARD MANUAL TEST RESULTS ===

Tester: _______________________
Date: _________________________
Time: _________________________
Browser: ______________________
Odoo Version: 17.0

VISUAL RENDERING:
[ ] Dashboard loads successfully
[ ] All tiles visible
[ ] Charts render correctly
[ ] Tables display data
[ ] Layout is responsive

DATA ACCURACY:
[ ] Leads Count: _____ (expected: 1,145)
[ ] Opportunities Count: _____ (expected: 3,823)
[ ] Expected Revenue: $_____ (expected: $356.6M)
[ ] Won Revenue: $_____ (expected: $6.8M)
[ ] Won/Lost Ratio: _____ (expected: 50:34)

FILTER FUNCTIONALITY:
[ ] Date range filter: PASS / FAIL
[ ] User filter: PASS / FAIL
[ ] Team filter: PASS / FAIL
[ ] Stage filter: PASS / FAIL
[ ] Probability filter: PASS / FAIL
[ ] Active/Archived toggle: PASS / FAIL
[ ] Combined filters: PASS / FAIL
[ ] Reset filters: PASS / FAIL

PERFORMANCE:
[ ] Initial load time: _____ seconds (target: < 3s)
[ ] Filter apply time: _____ seconds (target: < 1s)
[ ] Console errors: YES / NO
[ ] Memory issues: YES / NO

DRILL-DOWN:
[ ] Tile clicks: PASS / FAIL
[ ] Chart clicks: PASS / FAIL
[ ] Table clicks: PASS / FAIL
[ ] Navigation: PASS / FAIL

ISSUES FOUND:
1. _________________________________
2. _________________________________
3. _________________________________

OVERALL RESULT: PASS / FAIL

NOTES:
_______________________________________
_______________________________________
_______________________________________

Signature: ____________________________
```

---

**Test Guide Created:** November 27, 2025  
**Version:** 1.0  
**Database:** scholarixv2  
**Module:** crm_dashboard v17.0.1.0.1  

✅ **DASHBOARD READY FOR TESTING**
