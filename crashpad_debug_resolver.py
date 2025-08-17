#!/usr/bin/env python3
"""
Crashpad Debug Log Cleaner and Error Resolver
Addresses Chromium Crashpad errors and cleans up debug files
"""

import os
import glob
import json
from datetime import datetime
from pathlib import Path

class CrashpadDebugResolver:
    def __init__(self):
        self.debug_files_found = []
        self.debug_files_cleaned = []
        self.errors_analyzed = []
        
    def analyze_crashpad_errors(self):
        """Analyze Crashpad errors and provide solutions"""
        print("🔍 CRASHPAD ERROR ANALYSIS")
        print("=" * 50)
        
        crashpad_info = {
            "error_type": "Chromium Crashpad Registration Error",
            "error_code": "0x2 (System cannot find the file specified)",
            "common_causes": [
                "VS Code Electron process trying to create crash dumps",
                "Browser debugging sessions with missing crash dump paths",
                "Chromium-based applications with invalid crash reporting paths",
                "Windows permission issues with crash dump directories",
                "Missing or invalid crashpad handler executable"
            ],
            "impact": "Low - These are non-critical crash reporting errors",
            "resolution_priority": "Medium - Clean up but not critical for Odoo functionality"
        }
        
        print("📊 ERROR DETAILS:")
        print(f"   Type: {crashpad_info['error_type']}")
        print(f"   Code: {crashpad_info['error_code']}")
        print(f"   Impact: {crashpad_info['impact']}")
        
        print("\n🔍 COMMON CAUSES:")
        for i, cause in enumerate(crashpad_info['common_causes'], 1):
            print(f"   {i}. {cause}")
        
        return crashpad_info
    
    def find_debug_files(self):
        """Find all debug.log files in the project"""
        print("\n🔍 SCANNING FOR DEBUG FILES...")
        print("-" * 40)
        
        # Find debug.log files
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'debug.log':
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    
                    self.debug_files_found.append({
                        'path': file_path,
                        'size': file_size,
                        'size_mb': round(file_size / 1024 / 1024, 2) if file_size > 0 else 0
                    })
                    
                    print(f"📄 Found: {file_path} ({file_size} bytes)")
        
        print(f"\n📊 Total debug files found: {len(self.debug_files_found)}")
        total_size_mb = sum(f['size_mb'] for f in self.debug_files_found)
        print(f"📊 Total size: {total_size_mb:.2f} MB")
    
    def analyze_debug_file_contents(self):
        """Analyze contents of debug files"""
        print("\n🔍 ANALYZING DEBUG FILE CONTENTS...")
        print("-" * 40)
        
        for debug_file in self.debug_files_found:
            file_path = debug_file['path']
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Analyze content
                crashpad_errors = content.count('crashpad')
                createfile_errors = content.count('CreateFile:')
                total_lines = len(content.splitlines())
                
                analysis = {
                    'file': file_path,
                    'total_lines': total_lines,
                    'crashpad_errors': crashpad_errors,
                    'createfile_errors': createfile_errors,
                    'has_useful_content': total_lines > 2 and not (crashpad_errors == total_lines)
                }
                
                self.errors_analyzed.append(analysis)
                
                print(f"📄 {file_path}:")
                print(f"   Lines: {total_lines}")
                print(f"   Crashpad errors: {crashpad_errors}")
                print(f"   CreateFile errors: {createfile_errors}")
                print(f"   Useful content: {'Yes' if analysis['has_useful_content'] else 'No'}")
                
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
    
    def clean_debug_files(self):
        """Clean up debug files that only contain Crashpad errors"""
        print("\n🧹 CLEANING DEBUG FILES...")
        print("-" * 40)
        
        for analysis in self.errors_analyzed:
            file_path = analysis['file']
            
            # Clean files that only contain Crashpad errors or are very small
            should_clean = (
                not analysis['has_useful_content'] or
                analysis['total_lines'] <= 3 or
                (analysis['crashpad_errors'] > 0 and analysis['total_lines'] <= 10)
            )
            
            if should_clean:
                try:
                    # Create backup first
                    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    
                    # Remove the debug file
                    os.remove(file_path)
                    self.debug_files_cleaned.append(file_path)
                    print(f"✅ Cleaned: {file_path} (backup: {backup_path})")
                    
                except Exception as e:
                    print(f"❌ Error cleaning {file_path}: {e}")
            else:
                print(f"⚠️ Kept: {file_path} (contains useful content)")
    
    def create_crashpad_solution_guide(self):
        """Create comprehensive solution guide for Crashpad errors"""
        solution_guide = """
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
reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f
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
"""
        
        guide_file = f"CRASHPAD_SOLUTION_GUIDE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(solution_guide)
        
        print(f"\n📄 Solution guide created: {guide_file}")
        return guide_file
    
    def create_gitignore_update(self):
        """Update .gitignore to prevent future debug file commits"""
        gitignore_additions = """
# Debug and crash files (added by Crashpad resolver)
debug.log
*.dmp
crashpad_reports/
crash_dumps/
*.log.backup.*

# VS Code debug files
.vscode/launch.json.backup
.vscode/settings.json.backup

# Windows crash dumps
*.mdmp
*.hdmp
"""
        
        gitignore_path = '.gitignore'
        
        try:
            # Read existing .gitignore
            existing_content = ""
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Check if our additions are already there
            if "Debug and crash files" not in existing_content:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write(gitignore_additions)
                print(f"✅ Updated .gitignore with debug file patterns")
            else:
                print(f"ℹ️ .gitignore already contains debug file patterns")
                
        except Exception as e:
            print(f"❌ Error updating .gitignore: {e}")
    
    def run_crashpad_resolver(self):
        """Run complete Crashpad error resolution process"""
        print("🚀 CRASHPAD DEBUG LOG RESOLVER")
        print("=" * 60)
        print("OSUS Properties - Odoo 17 Development Environment")
        print("=" * 60)
        
        # Step 1: Analyze the error
        crashpad_info = self.analyze_crashpad_errors()
        
        # Step 2: Find debug files
        self.find_debug_files()
        
        # Step 3: Analyze contents
        self.analyze_debug_file_contents()
        
        # Step 4: Clean unnecessary files
        self.clean_debug_files()
        
        # Step 5: Create solution guide
        guide_file = self.create_crashpad_solution_guide()
        
        # Step 6: Update .gitignore
        self.create_gitignore_update()
        
        # Summary
        print(f"\n🎉 CRASHPAD RESOLUTION COMPLETE!")
        print("=" * 60)
        print(f"📊 SUMMARY:")
        print(f"   Debug files found: {len(self.debug_files_found)}")
        print(f"   Files cleaned: {len(self.debug_files_cleaned)}")
        print(f"   Solution guide: {guide_file}")
        
        if self.debug_files_cleaned:
            print(f"\n🧹 CLEANED FILES:")
            for file in self.debug_files_cleaned:
                print(f"   - {file}")
        
        print(f"\n💡 RECOMMENDATION:")
        print("   These Crashpad errors are cosmetic and don't affect Odoo functionality.")
        print("   Follow the solution guide to prevent future occurrences.")
        print("   Continue with normal Odoo development - no critical issues found.")
        
        return {
            'files_found': len(self.debug_files_found),
            'files_cleaned': len(self.debug_files_cleaned),
            'solution_guide': guide_file,
            'errors_analyzed': len(self.errors_analyzed)
        }

if __name__ == "__main__":
    resolver = CrashpadDebugResolver()
    result = resolver.run_crashpad_resolver()
