# 🔧 ASSET LOADING ERROR FIX - rental_management + announcement_banner

**Date**: November 30, 2025  
**Issue**: Missing JavaScript/CSS assets causing browser errors  
**Priority**: MEDIUM (Non-blocking but creates console noise)

---

## Error Analysis

### Browser Console Errors

```javascript
Could not get content for rental_management/static/src/js/rental.js
Could not get content for announcement_banner/static/src/js/announcement_banner.js
Could not get content for announcement_banner/static/src/css/announcement_banner.css
```

**Root Cause**: Module manifests reference asset files that don't exist on server

---

## Diagnosis Commands

```bash
# SSH to CloudPepper server
ssh user@scholarixglobal.com

# Navigate to Odoo installation
cd /var/odoo/scholarixv2

# Check if rental_management assets exist
ls -la extra-addons/*/rental_management/static/src/js/rental.js

# Check if announcement_banner module exists
ls -la extra-addons/*/announcement_banner/

# Check which modules are installed
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOF'
env['ir.module.module'].search([
    ('name', 'in', ['rental_management', 'announcement_banner']),
    ('state', '=', 'installed')
]).mapped(lambda m: f"{m.name}: {m.state}")
EOF
```

---

## Solution Options

### Option 1: Remove Asset References (Recommended)

If the JS/CSS files don't exist and aren't needed:

**For rental_management**:

```bash
# Check manifest
cat extra-addons/*/rental_management/__manifest__.py | grep -A 20 "'assets'"

# If rental.js is referenced but doesn't exist, remove from manifest
```

**For announcement_banner**:

```bash
# Check if module is installed but not installable
# Server logs show: "module announcement_banner: not installable, skipped"

# Uninstall if orphaned
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --uninstall announcement_banner --stop-after-init
```

---

### Option 2: Create Missing Files (If Features Needed)

If the assets should exist but are missing:

**Create rental.js**:

```bash
# Check if directory exists
mkdir -p extra-addons/cybroaddons.git-*/rental_management/static/src/js/

# Create placeholder file
cat > extra-addons/cybroaddons.git-*/rental_management/static/src/js/rental.js << 'EOF'
/** @odoo-module **/
// rental_management JavaScript module
// Placeholder - no functionality currently needed
console.log('[rental_management] JS module loaded');
EOF
```

**For announcement_banner**: Module is marked "not installable" so should be removed entirely.

---

### Option 3: Clear Assets Cache (Try First)

Sometimes Odoo caches reference old asset paths:

```bash
# Clear Odoo assets cache
rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/*

# Update web module to regenerate assets
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --update web --stop-after-init

# Restart Odoo
sudo systemctl restart odoo
```

---

## Automated Fix Script

Save this as `fix_missing_assets.sh`:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "FIXING MISSING ASSETS - rental_management + announcement_banner"
echo "=========================================="

# Navigate to Odoo directory
cd /var/odoo/scholarixv2

# Step 1: Check which modules are installed
echo "Step 1: Checking installed modules..."
RENTAL_INSTALLED=$(sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOF'
result = env['ir.module.module'].search([('name', '=', 'rental_management'), ('state', '=', 'installed')])
print('YES' if result else 'NO')
EOF
)

BANNER_INSTALLED=$(sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOF'
result = env['ir.module.module'].search([('name', '=', 'announcement_banner'), ('state', '=', 'installed')])
print('YES' if result else 'NO')
EOF
)

echo "rental_management installed: $RENTAL_INSTALLED"
echo "announcement_banner installed: $BANNER_INSTALLED"

# Step 2: Check if rental.js exists
echo ""
echo "Step 2: Checking rental_management assets..."
RENTAL_JS_PATH=$(find extra-addons -path "*/rental_management/static/src/js/rental.js" 2>/dev/null | head -1)

if [ -z "$RENTAL_JS_PATH" ]; then
    echo "⚠️  rental.js not found"
    
    # Find rental_management directory
    RENTAL_DIR=$(find extra-addons -type d -name "rental_management" 2>/dev/null | head -1)
    
    if [ -n "$RENTAL_DIR" ]; then
        echo "Creating placeholder rental.js..."
        mkdir -p "$RENTAL_DIR/static/src/js"
        cat > "$RENTAL_DIR/static/src/js/rental.js" << 'EOF'
/** @odoo-module **/
// rental_management JavaScript module
// Placeholder - no functionality currently needed
console.log('[rental_management] JS module loaded');
EOF
        echo "✅ Created: $RENTAL_DIR/static/src/js/rental.js"
    else
        echo "❌ rental_management directory not found!"
    fi
else
    echo "✅ rental.js exists: $RENTAL_JS_PATH"
fi

# Step 3: Handle announcement_banner
echo ""
echo "Step 3: Handling announcement_banner..."

if [ "$BANNER_INSTALLED" = "YES" ]; then
    echo "announcement_banner is installed but marked as not installable"
    echo "Uninstalling..."
    
    sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
      --uninstall announcement_banner --stop-after-init
    
    echo "✅ announcement_banner uninstalled"
else
    echo "✅ announcement_banner not installed (good)"
fi

# Step 4: Clear assets cache
echo ""
echo "Step 4: Clearing assets cache..."
rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/*
echo "✅ Assets cache cleared"

# Step 5: Regenerate assets
echo ""
echo "Step 5: Regenerating assets..."
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --update web --stop-after-init

echo "✅ Assets regenerated"

# Step 6: Restart Odoo
echo ""
echo "Step 6: Restarting Odoo..."
sudo systemctl restart odoo
sleep 3

echo ""
echo "=========================================="
echo "✅ FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Verification:"
echo "1. Open browser and hard refresh (Ctrl+Shift+R)"
echo "2. Open DevTools Console (F12)"
echo "3. Check for asset loading errors"
echo ""
echo "If errors persist, check:"
echo "tail -f /var/odoo/scholarixv2/logs/odoo.log | grep -i 'asset\|error'"
```

---

## Manual Fix Steps (Step-by-Step)

### Step 1: SSH Connect

```bash
ssh user@scholarixglobal.com
```

### Step 2: Check Asset Paths

```bash
cd /var/odoo/scholarixv2

# Find rental_management directory
find extra-addons -type d -name "rental_management" 2>/dev/null

# Check if rental.js exists
find extra-addons -path "*/rental_management/static/src/js/rental.js" 2>/dev/null

# Check manifest assets section
cat extra-addons/*/rental_management/__manifest__.py | grep -A 30 "'assets'"
```

### Step 3: Fix rental_management

**Option A: Remove asset reference from manifest** (if file not needed)

```bash
# Edit manifest
nano extra-addons/cybroaddons.git-*/rental_management/__manifest__.py

# Find 'assets' section and remove rental.js reference
# OR comment it out with #
```

**Option B: Create placeholder file** (if reference must stay)

```bash
RENTAL_DIR=$(find extra-addons -type d -name "rental_management" | head -1)
mkdir -p "$RENTAL_DIR/static/src/js"

cat > "$RENTAL_DIR/static/src/js/rental.js" << 'EOF'
/** @odoo-module **/
console.log('[rental_management] JS module loaded');
EOF
```

### Step 4: Fix announcement_banner

```bash
# Uninstall orphaned module
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --uninstall announcement_banner --stop-after-init
```

### Step 5: Clear Cache & Regenerate

```bash
# Clear assets
rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/*

# Regenerate
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --update web --stop-after-init

# Restart
sudo systemctl restart odoo
```

### Step 6: Verify in Browser

1. Open Odoo in browser
2. Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
3. Open DevTools Console (F12)
4. Check for errors

---

## Quick Diagnosis Commands

```bash
# Check Odoo logs in real-time
tail -f /var/odoo/scholarixv2/logs/odoo.log | grep -i "rental\|banner\|asset"

# List all asset bundles
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOF'
bundles = env['ir.asset'].search([])
for bundle in bundles:
    print(f"{bundle.name}: {bundle.path}")
EOF

# Check which files are in web.assets_backend
grep -r "rental.js" extra-addons/*/rental_management/__manifest__.py
```

---

## Root Cause Analysis

### Why This Happens

1. **Missing Physical Files**: Asset files referenced in manifest don't exist on disk
2. **Orphaned Modules**: `announcement_banner` is marked "not installable" but still referenced
3. **Stale Cache**: Odoo's asset cache still references old file paths

### Prevention

1. ✅ Always verify asset files exist before adding to manifest
2. ✅ Remove unused asset references from manifests
3. ✅ Properly uninstall modules instead of just marking not installable
4. ✅ Clear assets cache after module changes

---

## Impact Assessment

**Current Impact**: 🟡 **MEDIUM**
- ✅ Functional features still work (rental_management operational)
- ⚠️ Browser console shows errors (confusing for developers)
- ⚠️ Slight performance impact (failed asset requests)
- ⚠️ Clutters error logs

**After Fix**: 🟢 **CLEAN**
- ✅ No console errors
- ✅ Faster page loads (no failed requests)
- ✅ Clean error logs

---

## Testing Checklist

After applying fix:

- [ ] No console errors for rental.js
- [ ] No console errors for announcement_banner assets
- [ ] rental_management features work (property form, payment schedules)
- [ ] Page loads without delays
- [ ] Odoo logs show no asset errors

---

## Alternative: PowerShell Remote Execution

If you prefer to run commands from Windows PowerShell:

```powershell
# Define SSH connection
$SSH_HOST = "scholarixglobal.com"
$SSH_USER = "your_username"

# Run diagnostic
ssh "${SSH_USER}@${SSH_HOST}" "cd /var/odoo/scholarixv2 && find extra-addons -path '*/rental_management/static/src/js/rental.js'"

# Clear cache remotely
ssh "${SSH_USER}@${SSH_HOST}" "sudo rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/*"

# Restart Odoo
ssh "${SSH_USER}@${SSH_HOST}" "sudo systemctl restart odoo"
```

---

## Next Steps

1. **Choose your approach**:
   - Automated: Run `fix_missing_assets.sh` script
   - Manual: Follow step-by-step commands above
   - PowerShell: Use remote execution from Windows

2. **After fix**: Hard refresh browser (Ctrl+Shift+R)

3. **Verify**: Check console for clean load

4. **Monitor**: Watch logs for 10 minutes to ensure stability

---

**Status**: 📋 **READY TO FIX**  
**Estimated Time**: 5-10 minutes  
**Risk Level**: LOW (non-breaking changes)

---

*Need help with SSH commands? Let me know which option you prefer!*
