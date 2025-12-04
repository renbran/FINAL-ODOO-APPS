# CRM Dashboard Accuracy Issues - Analysis & Fixes

## 🔍 Issues Identified

### 1. **Hardcoded Stage ID for "Won" Leads**
**Problem**: Multiple queries use `stage_id=4` assuming stage 4 is always "Won"
```python
# Lines 128, 148, 588, 622, etc.
self._cr.execute('''select sum(expected_revenue) from crm_lead 
where stage_id=4 and team_id=%s ...''')
```
**Impact**: If CRM stages are customized or reordered, "Won" stage might not be ID 4, causing incorrect revenue calculations.

**Fix**: Use `probability=100` OR lookup stage by name instead of hardcoded ID.

### 2. **Inconsistent Date Field Usage**
**Problem**: Mixing `date_deadline`, `date_closed`, `date_open`, and `date_conversion`
```python
# Lines 135 - using date_closed for Won
Extract(Year FROM date_closed)=Extract(Year FROM DATE(NOW()))

# Lines 642 - using date_open for ratio calculation  
Extract(Year FROM crm_lead.date_open) = Extract(Year FROM DATE(NOW()))
```
**Impact**: Inconsistent timeframe filtering - some use close date, others deadline, causing mismatched counts.

**Fix**: Standardize on appropriate date field per metric type.

### 3. **Incorrect Active/Probability Logic**
**Problem**: Revenue calculations filter incorrectly:
```python
# Line 226 - Expected Revenue includes Won (should exclude)
WHERE user_id=%s and type='opportunity' and active='true'

# Line 234 - Won revenue query
WHERE user_id=%s and type='opportunity' and active='true' and stage_id=4
```
**Impact**: "Expected Revenue" includes already-won opportunities, inflating numbers.

**Fix**: Expected revenue should exclude won/lost (probability NOT IN (0,100)).

### 4. **Ratio Calculations Without NULL Checks**
**Problem**: Division by zero not properly handled in multiple places
```python
# Line 645
round(data[1] / data[2], 2) if data[2] != 0 else 0
```
**Impact**: May show 0 or cause errors when no lost opportunities exist.

**Fix**: More robust NULL/zero handling.

### 5. **User vs Team Filtering Confusion**
**Problem**: Manager queries use `team_id` but salesperson uses `user_id`
```python
# Line 135 - Manager sees team
where stage_id=4 and team_id=%s

# Line 150 - Salesperson sees own
where stage_id=4 and user_id=%s
```
**Impact**: Managers might see inflated team numbers vs personal targets.

**Fix**: Clarify if dashboard should show personal or team metrics.

### 6. **Average Time Calculation Bug**
**Problem**: Uses `.seconds` instead of total time difference
```python
# Line 706
avg = (date_close - date_create).seconds  # Only counts seconds portion!
```
**Impact**: Average conversion time will be wildly inaccurate (max 86400).

**Fix**: Use `.total_seconds()` or `.days`.

### 7. **Monthly Goal Logic Issues**
**Problem**: Compares deadline month with closed month inconsistently
```python
# Line 300 - Uses deadline for total
t.date_deadline.month == fields.date.today().month

# Line 302 - Uses closed for achievement  
a.date_closed.month == fields.date.today().month
```
**Impact**: Comparing opportunities expected this month vs actually closed this month (apples to oranges).

**Fix**: Use consistent date field based on metric intent.

## 🛠️ Recommended Fixes

### Fix 1: Create Proper Stage Lookup
```python
@api.model
def _get_won_stage_ids(self):
    """Get IDs of Won stages (probability=100)"""
    return self.env['crm.stage'].search([('is_won', '=', True)]).ids

@api.model  
def _get_lost_stage_ids(self):
    """Get IDs of Lost stages"""
    return self.env['crm.stage'].search([]).filtered(
        lambda s: s.fold and s.probability == 0).ids
```

### Fix 2: Standardize Expected Revenue Query
```python
# Expected Revenue = Open opportunities (not won/lost)
SELECT SUM(expected_revenue) 
FROM crm_lead 
WHERE user_id=%s 
  AND type='opportunity' 
  AND active=true
  AND probability NOT IN (0, 100)  -- Exclude won/lost
  AND EXTRACT(MONTH FROM date_deadline) = EXTRACT(MONTH FROM CURRENT_DATE)
  AND EXTRACT(YEAR FROM date_deadline) = EXTRACT(YEAR FROM CURRENT_DATE)
```

### Fix 3: Fix Average Conversion Time
```python
# Use total_seconds() and convert to days/hours
delta = date_close - date_create
avg_seconds += delta.total_seconds()

# Then calculate average
avg_time_days = avg_seconds / crm_lead_count / 86400
```

### Fix 4: Add Proper NULL Handling
```python
# Before division
won_count = record_opportunity.get(True, 0) or 0
lost_count = record_opportunity.get(False, 0) or 0

if lost_count > 0:
    opportunity_ratio_value = round(won_count / lost_count, 2)
else:
    opportunity_ratio_value = 0.0
```

### Fix 5: Clarify Monthly Goal Logic
```python
# Option A: Expected to close this month (use deadline)
total = sum(rec.expected_revenue for rec in leads.filtered(
    lambda t: t.date_deadline and 
              t.date_deadline.month == today.month and
              t.date_deadline.year == today.year and
              t.probability not in (0, 100)  # Exclude won/lost
))

# Option B: Actually closed this month (use date_closed)
achievement = sum(won.expected_revenue for won in leads_won.filtered(
    lambda a: a.date_closed and
              a.date_closed.month == today.month and
              a.date_closed.year == today.year
))
```

## 📊 Testing Checklist

1. [ ] Verify lead counts match CRM > Leads list view filters
2. [ ] Verify opportunity counts match CRM > Pipeline
3. [ ] Verify revenue totals match Sales Analysis report
4. [ ] Test with custom stage IDs (not default 1-4)
5. [ ] Test with user who has zero leads/opportunities
6. [ ] Test manager view vs salesperson view
7. [ ] Verify date filters work across year boundaries
8. [ ] Test won/lost ratios with edge cases (0 lost, 0 won)

## 🚀 Implementation Priority

**HIGH PRIORITY (Data Accuracy)**:
1. Fix hardcoded stage_id=4 → use probability=100 or lookup
2. Fix expected revenue to exclude won/lost
3. Fix average time calculation bug

**MEDIUM PRIORITY (Consistency)**:
4. Standardize date field usage per metric
5. Improve NULL/zero handling in ratios
6. Clarify user vs team metric logic

**LOW PRIORITY (Enhancement)**:
7. Add data validation/sanity checks
8. Add caching for expensive queries
9. Add user-facing error messages

## 📝 Deployment Steps

1. Backup current crm_dashboard module
2. Apply fixes incrementally (test each)
3. Run `cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u crm_dashboard`
4. Clear browser cache
5. Test all dashboard tiles/charts
6. Monitor logs for SQL errors
7. Rollback if issues detected

## 💡 Long-term Recommendations

1. **Add Unit Tests**: Create test cases for each calculation method
2. **Add Logging**: Log SQL query results for debugging
3. **Performance**: Consider computed fields instead of real-time queries
4. **Documentation**: Add docstrings explaining each metric's calculation
5. **User Guide**: Document what each tile/chart represents

---

**Created**: November 27, 2025
**Status**: Analysis Complete - Ready for Implementation
**Module**: crm_dashboard (Cybrosys)
**Database**: scholarixv2
