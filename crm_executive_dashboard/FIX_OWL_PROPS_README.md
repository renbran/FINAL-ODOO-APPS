# CRM Executive Dashboard - OWL Props Error Fix

## Problem
```
OwlError: Invalid props for component 'CRMExecutiveDashboard': 
unknown key 'action', unknown key 'actionId', unknown key 'className'
```

## Root Cause
The component had `static props = {}` which means it accepts NO props. However, Odoo's action system automatically passes these props to all action components:
- `action`: The action object
- `actionId`: The action's database ID  
- `className`: CSS class for styling

## Solution Applied

### File 1: `crm_executive_dashboard.js`
**Before:**
```javascript
export class CRMExecutiveDashboard extends Component {
    static template = "crm_executive_dashboard.Dashboard";
    static props = {};
```

**After:**
```javascript
export class CRMExecutiveDashboard extends Component {
    static template = "crm_executive_dashboard.Dashboard";
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
    };
```

### File 2: `crm_strategic_dashboard.js`
**Before:**
```javascript
export class CRMStrategicDashboard extends Component {
    static template = "crm_strategic_dashboard.Dashboard";
    static props = {};
```

**After:**
```javascript
export class CRMStrategicDashboard extends Component {
    static template = "crm_strategic_dashboard.Dashboard";
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
    };
```

## Deployment Steps

### Option 1: Manual Upload (Current Server)
```powershell
# Upload to scholarixglobal.com or your server
scp crm_executive_dashboard/static/src/js/crm_executive_dashboard.js user@server:/path/to/addons/crm_executive_dashboard/static/src/js/
scp crm_executive_dashboard/static/src/js/crm_strategic_dashboard.js user@server:/path/to/addons/crm_executive_dashboard/static/src/js/
```

### Option 2: Module Upgrade (Recommended)
```bash
# SSH into server
ssh user@scholarixglobal.com

# Navigate to Odoo directory
cd /path/to/odoo

# Restart Odoo
sudo systemctl restart odoo

# Or upgrade module via Odoo UI:
# Settings → Apps → CRM Executive Dashboard → Upgrade
```

### Option 3: Git Push (If using version control)
```bash
git add crm_executive_dashboard/static/src/js/
git commit -m "fix: Add missing OWL props to CRM dashboards"
git push origin main
# Then pull on server and restart
```

## Testing
1. Navigate to CRM → Dashboard
2. Open browser console (F12)
3. No OWL errors should appear
4. Dashboard should load normally

## Why These Props Are Optional
All three props are marked `optional: true` because:
- **action**: May not be passed in all contexts
- **actionId**: Only present when opened from action menu
- **className**: Only added when custom styling is needed

Making them optional ensures backward compatibility and allows the component to work in various contexts.

## Odoo 17 Best Practice
Always declare props that might be passed by Odoo's framework:
```javascript
static props = {
    // Standard Odoo action props
    action: { type: Object, optional: true },
    actionId: { type: Number, optional: true },
    className: { type: String, optional: true },
    
    // Add any custom props your component needs
    // myCustomProp: { type: String },
};
```

## Status
✅ **Fixed locally** - Files updated in repository
⏳ **Pending deployment** - Upload to scholarixglobal.com server
🔄 **Requires**: Odoo restart + browser cache clear after deployment
