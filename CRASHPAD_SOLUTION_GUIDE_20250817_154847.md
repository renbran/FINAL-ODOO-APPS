
# 🛠️ CRASHPAD ERROR RESOLUTION GUIDE

## 🔍 **ERROR OVERVIEW:**

**Error Type:** Chromium Crashpad Registration Error
**Error Message:** `CreateFile: The system cannot find the file specified. (0x2)`
**Source:** Windows Crashpad crash reporting system

---

## 🎯 **SOLUTIONS:**

### **1. VS Code Configuration Fix**
Create/update `.vscode/settings.json`:
```json
{
    "debug.allowBreakpointsEverywhere": false,
    "debug.openDebug": "neverOpen",
    "extensions.autoUpdate": false,
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    "typescript.disableAutomaticTypeAcquisition": true
}
```

### **2. Windows Environment Variables**
Add to your system environment variables:
```
CHROME_CRASHPAD_PIPE_NAME=""
CRASHPAD_HANDLER_PID=""
```

### **3. Browser Development Setup**
For Odoo development in browser:
```javascript
// Add to browser developer tools console
if (window.chrome) {
    window.chrome.crashReporter = { enabled: false };
}
```

### **4. Project .gitignore Update**
Add to `.gitignore`:
```
# Debug and crash files
debug.log
*.dmp
crashpad_reports/
crash_dumps/
```

### **5. VS Code Launch Configuration**
Update `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo Debug",
            "type": "python",
            "request": "launch",
            "program": "odoo-bin",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "CRASHPAD_HANDLER": ""
            },
            "args": ["--dev=all"]
        }
    ]
}
```

---

## 🔧 **PREVENTION:**

### **1. Disable Crash Reporting**
```bash
# Windows Registry (run as administrator)
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f
```

### **2. VS Code User Settings**
```json
{
    "debug.console.closeOnEnd": true,
    "debug.openExplorerOnEnd": false,
    "extensions.ignoreRecommendations": true,
    "telemetry.enableCrashReporter": false
}
```

### **3. Chrome/Edge Flags**
When testing Odoo in browser, use these flags:
```
--disable-crash-reporter
--disable-crashpad
--disable-logging
--silent-launch
```

---

## 📋 **MAINTENANCE:**

### **Daily:**
- Monitor for new debug.log files
- Clean up crash dump directories

### **Weekly:**
- Review VS Code error logs
- Update browser flags if needed

### **Monthly:**
- Check Windows Event Viewer for related errors
- Update development environment settings

---

## 🎯 **VERIFICATION:**

After applying fixes:
1. ✅ No new debug.log files created
2. ✅ VS Code starts without Crashpad errors
3. ✅ Browser debugging works without crash reporter errors
4. ✅ Odoo development continues normally

---

## 📞 **SUPPORT:**

These errors are cosmetic and don't affect Odoo functionality. If they persist:
1. Check Windows permissions for temp directories
2. Update VS Code and browser to latest versions
3. Restart Windows to clear any locked crash reporting processes

---
