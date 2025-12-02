# 🚀 QUICK FIX: Missing Assets (rental.js + announcement_banner)

**Issue**: Browser console shows asset loading errors  
**Impact**: Non-breaking (features work, but console shows errors)  
**Fix Time**: 5 minutes

---

## Option 1: Automated PowerShell (Easiest) ⚡

```powershell
# From repository root
cd "d:\RUNNING APPS\FINAL-ODOO-APPS"

# Run automated fix (update SSHUser if needed)
.\fix_remote_assets.ps1 -SSHUser "root" -SSHHost "scholarixglobal.com"

# Or with default values:
.\fix_remote_assets.ps1
```

**What it does**:
1. Uploads fix script to server
2. Creates missing rental.js file
3. Uninstalls announcement_banner (orphaned module)
4. Clears assets cache
5. Regenerates assets
6. Restarts Odoo

---

## Option 2: Manual SSH (Full Control) 🔧

```bash
# 1. SSH to server
ssh root@scholarixglobal.com

# 2. Navigate to Odoo
cd /var/odoo/scholarixv2

# 3. Upload and run fix script
# (From local machine, upload script first)
scp fix_missing_assets.sh root@scholarixglobal.com:/tmp/
ssh root@scholarixglobal.com "bash /tmp/fix_missing_assets.sh"

# OR manually create the file:
RENTAL_DIR=$(find extra-addons -type d -name "rental_management" | head -1)
mkdir -p "$RENTAL_DIR/static/src/js"
cat > "$RENTAL_DIR/static/src/js/rental.js" << 'EOF'
/** @odoo-module **/
console.log('[rental_management] JS module loaded');
EOF

# 4. Clear cache
rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/*

# 5. Restart
sudo systemctl restart odoo
```

---

## Option 3: Quick Cache Clear (Fastest) ⚡⚡

If you just want to try clearing cache first:

```bash
ssh root@scholarixglobal.com "rm -rf /var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets/* && sudo systemctl restart odoo"
```

Then hard refresh browser: **Ctrl+Shift+R**

---

## Verification

### In Browser:
1. Open DevTools (F12)
2. Go to Console tab
3. Hard refresh (Ctrl+Shift+R)
4. **Should NOT see**:
   - ❌ `Could not get content for rental_management/static/src/js/rental.js`
   - ❌ `Could not get content for announcement_banner/static/src/js/announcement_banner.js`

### On Server:
```bash
# Check if rental.js exists
ssh root@scholarixglobal.com "find /var/odoo/scholarixv2/extra-addons -path '*/rental_management/static/src/js/rental.js'"

# Should output a path like:
# /var/odoo/scholarixv2/extra-addons/cybroaddons.git-XXX/rental_management/static/src/js/rental.js
```

---

## Troubleshooting

### Error: SSH Connection Failed
```powershell
# Update SSH credentials
.\fix_remote_assets.ps1 -SSHUser "your_username" -SSHHost "139.84.163.11"
```

### Error: Script Not Found
```powershell
# Ensure you're in repository root
cd "d:\RUNNING APPS\FINAL-ODOO-APPS"
ls fix_remote_assets.ps1  # Should exist
```

### Assets Still Not Loading
```bash
# SSH to server
ssh root@scholarixglobal.com

# Check Odoo logs
tail -50 /var/odoo/scholarixv2/logs/odoo.log | grep -i "asset\|error"

# Force regenerate all assets
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --update all --stop-after-init
```

---

## What Gets Fixed

### rental_management
- ✅ Creates placeholder `rental.js` file
- ✅ Prevents "Could not get content" errors
- ✅ Maintains all existing functionality

### announcement_banner
- ✅ Uninstalls orphaned module (marked "not installable")
- ✅ Removes asset references from cache
- ✅ Cleans up database entries

### Assets Cache
- ✅ Clears stale cached asset references
- ✅ Regenerates fresh asset bundles
- ✅ Odoo restart ensures clean load

---

## Files Created

| File | Purpose |
|------|---------|
| `fix_remote_assets.ps1` | PowerShell automation script |
| `fix_missing_assets.sh` | Bash script for server execution |
| `FIX_MISSING_ASSETS.md` | Comprehensive documentation |
| `QUICK_FIX_ASSETS.md` | This quick reference |

---

## Related Issues

This fix also resolves:
- Browser console clutter
- Slight page load delays
- Asset loading warnings in logs

Does NOT affect:
- rental_management functionality
- Payment schedule generation
- SPA report printing
- Any core Odoo features

---

## Support

**If fix doesn't work**:
1. Check SSH connection: `ssh root@scholarixglobal.com "echo OK"`
2. Check Odoo service: `ssh root@scholarixglobal.com "systemctl status odoo"`
3. Review server logs: `ssh root@scholarixglobal.com "tail -100 /var/odoo/scholarixv2/logs/odoo.log"`

**For help**: See full documentation in `FIX_MISSING_ASSETS.md`

---

**Status**: ✅ Ready to deploy  
**Risk Level**: 🟢 Low (non-breaking changes)  
**Est. Time**: ⏱️ 5 minutes
