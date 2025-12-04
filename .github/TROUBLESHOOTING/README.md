# Troubleshooting Guides Index

This directory contains detailed troubleshooting documentation for common production issues encountered with the FINAL-ODOO-APPS project on CloudPepper hosting.

## Available Guides

### 🚨 Critical Production Issues

#### [CSS Error: "A css error occurred, using an old style to render this page"](./CSS_ERROR_OLD_STYLE_FIX.md)
**Severity**: Critical  
**Impact**: Breaks entire Odoo UI, falls back to basic CSS rendering  
**Time to Fix**: 5 minutes (with guide) vs 5-6 hours (without)  
**Root Cause**: JavaScript syntax errors in sgc_tech_ai_theme module  

**Quick Fix**:
```bash
# Disable SGC theme, clear cache, restart service, clear browser cache
# See full guide for step-by-step instructions
```

**Key Lessons**:
- Error message is misleading (says "CSS" but is JavaScript)
- Don't disable individual files (reveals 22+ more errors)
- Always test server-side first (curl) before trusting browser
- Clear browser cache is CRITICAL step

---

### 🎨 Website Configuration

#### [Website Theme Cleanup - Reset to Default](./WEBSITE_THEME_CLEANUP.md)
**Severity**: Maintenance  
**Impact**: Cleans up frontend website, removes broken themes  
**Time to Fix**: 5 minutes  
**Purpose**: Reset website to clean default Odoo theme  

**Quick Fix**:
```bash
# Uninstall broken theme, clear assets, restart service
# Backend OSUS branding preserved
```

**Key Actions**:
- Uninstalled sgc_tech_ai_theme (22+ JavaScript errors)
- Cleared 110 cached asset records
- Reset to default Odoo frontend theme
- Preserved muk_web_theme backend (OSUS branding)

---

### 📊 Dashboard Enhancements

#### [CRM Dashboard Currency Formatting](./CRM_DASHBOARD_CURRENCY_FORMAT.md)
**Severity**: Enhancement  
**Impact**: Improves readability of large currency values  
**Time to Fix**: 10 minutes  
**Purpose**: Format revenue numbers with K/M/B abbreviations  

**Quick Fix**:
```bash
# Add formatCurrency() function to JavaScript
# Clear assets, restart scholarixv2 service
```

**Key Features**:
- Thousands: 1.50 K (instead of 1,500)
- Millions: 13.38 M (instead of 13,376,708.91)
- Billions: 1.25 B (instead of 1,250,000,000)
- Applied to all dashboard revenue tiles

---

## How to Use These Guides

1. **Quick Reference Card**: Each guide starts with a command block for immediate fix
2. **Root Cause Analysis**: Understand WHY the issue occurred
3. **Step-by-Step Fix**: Detailed instructions with commands
4. **Time Breakdown**: Learn what NOT to do (time-wasters documented)
5. **Lessons Learned**: Prevent future occurrences

## Contributing

When encountering new production issues:

1. Document the complete timeline (what was tried, what failed, what worked)
2. Include ACTUAL time taken vs estimated time
3. Document all dead-ends and time-wasters
4. Create quick reference card at top of document
5. Save in this directory with descriptive filename

**Format**: `ISSUE_DESCRIPTION_FIX.md`

## Emergency Contacts

- **Production Server**: root@139.84.163.11 (CloudPepper)
- **Database**: osusproperties (PostgreSQL 18.1)
- **Service**: odona-osusproperties.service
- **Ports**: 3000 (HTTP), 3001 (gevent)
- **Logs**: `/var/odoo/osusproperties/logs/odoo-server.log`

---

**Last Updated**: November 28, 2025
