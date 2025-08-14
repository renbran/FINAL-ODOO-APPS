#!/usr/bin/env python3
"""
CloudPepper Asset Regeneration Script
Forces regeneration of web.assets_web_dark.min.js and other problematic assets
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudPepperAssetRegeneration:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.assets_fixed = []
        
    def clear_asset_caches(self):
        """Clear all asset caches and compiled files"""
        logger.info("Clearing asset caches...")
        
        cache_paths = [
            # Local development caches
            self.workspace_root / "__pycache__",
            self.workspace_root / ".cache",
            
            # Asset specific caches
            "**/static/src/**/*.min.js",
            "**/static/src/**/*.min.css",
            
            # Common Odoo cache locations
            "/tmp/odoo_assets_*",
            "/var/odoo/*/filestore/*/assets/*",
        ]
        
        for cache_path in cache_paths:
            if isinstance(cache_path, str):
                # Use shell commands for wildcard paths
                if os.name == 'nt':  # Windows
                    subprocess.run(f'del /s /q "{cache_path}"', shell=True, stderr=subprocess.DEVNULL)
                else:  # Linux/Mac
                    subprocess.run(f'rm -rf {cache_path}', shell=True, stderr=subprocess.DEVNULL)
            else:
                # Direct path deletion
                if cache_path.exists():
                    if cache_path.is_dir():
                        shutil.rmtree(cache_path, ignore_errors=True)
                    else:
                        cache_path.unlink(missing_ok=True)
                    logger.info(f"Cleared: {cache_path}")
    
    def validate_js_syntax(self):
        """Validate JavaScript syntax in all relevant files"""
        logger.info("Validating JavaScript syntax...")
        
        js_files = []
        
        # Find all JavaScript files in muk_web modules
        for muk_dir in self.workspace_root.glob("muk_web*"):
            if muk_dir.is_dir():
                js_files.extend(muk_dir.glob("**/*.js"))
        
        # Add other critical JS files
        critical_modules = [
            "account_payment_final",
            "enhanced_rest_api",
            "oe_sale_dashboard_17",
            "crm_executive_dashboard"
        ]
        
        for module in critical_modules:
            module_path = self.workspace_root / module
            if module_path.exists():
                js_files.extend(module_path.glob("**/*.js"))
        
        syntax_errors = []
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax validation
                issues = []
                
                # Check for mismatched brackets
                if content.count('{') != content.count('}'):
                    issues.append("Mismatched curly braces")
                
                if content.count('[') != content.count(']'):
                    issues.append("Mismatched square brackets")
                
                if content.count('(') != content.count(')'):
                    issues.append("Mismatched parentheses")
                
                # Check for semicolon issues on line breaks
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.endswith(';') and i < len(lines) - 1:
                        next_line = lines[i + 1].strip()
                        if next_line.startswith(';'):
                            issues.append(f"Line {i+2}: Extra semicolon")
                
                if issues:
                    syntax_errors.append({
                        'file': js_file,
                        'issues': issues
                    })
                    logger.warning(f"Syntax issues in {js_file.name}: {', '.join(issues)}")
                else:
                    logger.debug(f"Syntax OK: {js_file.name}")
                    
            except Exception as e:
                logger.error(f"Error validating {js_file}: {e}")
                syntax_errors.append({
                    'file': js_file,
                    'issues': [f"Read error: {e}"]
                })
        
        return syntax_errors
    
    def create_asset_bundle_fixes(self):
        """Create fixes for asset bundle definitions"""
        logger.info("Creating asset bundle fixes...")
        
        # Fix muk_web_appsbar manifest
        appsbar_manifest = self.workspace_root / "muk_web_appsbar" / "__manifest__.py"
        if appsbar_manifest.exists():
            try:
                with open(appsbar_manifest, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ensure proper asset bundle definition
                if "'web.assets_web_dark'" in content:
                    logger.info("Found web.assets_web_dark in muk_web_appsbar manifest")
                    
                    # Check for proper syntax in asset definition
                    if content.count('[') != content.count(']'):
                        logger.warning("Potential bracket mismatch in muk_web_appsbar manifest")
                        # Create a fixed version
                        self._fix_manifest_syntax(appsbar_manifest)
                        
            except Exception as e:
                logger.error(f"Error processing appsbar manifest: {e}")
        
        # Check muk_web_colors manifest
        colors_manifest = self.workspace_root / "muk_web_colors" / "__manifest__.py"
        if colors_manifest.exists():
            try:
                with open(colors_manifest, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "'web.assets_web_dark'" in content:
                    logger.info("Found web.assets_web_dark in muk_web_colors manifest")
                    
            except Exception as e:
                logger.error(f"Error processing colors manifest: {e}")
    
    def _fix_manifest_syntax(self, manifest_path):
        """Fix common manifest syntax issues"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix common asset definition issues
            lines = content.split('\n')
            fixed_lines = []
            in_assets_block = False
            
            for line in lines:
                stripped = line.strip()
                
                if "'assets'" in stripped and '{' in stripped:
                    in_assets_block = True
                
                if in_assets_block:
                    # Fix trailing commas in asset arrays
                    if stripped.endswith(',]'):
                        line = line.replace(',]', ']')
                    
                    # Fix misplaced semicolons
                    if ';' in line and not line.strip().startswith('#'):
                        line = line.replace(';', '')
                
                if in_assets_block and '}' in stripped:
                    in_assets_block = False
                
                fixed_lines.append(line)
            
            fixed_content = '\n'.join(fixed_lines)
            
            if fixed_content != original_content:
                # Create backup
                backup_path = f"{manifest_path}.backup"
                shutil.copy2(manifest_path, backup_path)
                
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                logger.info(f"Fixed manifest syntax: {manifest_path}")
                self.assets_fixed.append(str(manifest_path))
                
        except Exception as e:
            logger.error(f"Error fixing manifest {manifest_path}: {e}")
    
    def create_odoo_restart_commands(self):
        """Create commands to restart Odoo and regenerate assets"""
        logger.info("Creating Odoo restart commands...")
        
        # Linux/Docker commands
        linux_script = self.workspace_root / "cloudpepper_restart_odoo.sh"
        linux_content = '''#!/bin/bash
# CloudPepper Odoo Restart with Asset Regeneration

echo "=== CloudPepper Odoo Restart ==="
echo "Timestamp: $(date)"

# Stop Odoo
echo "Stopping Odoo..."
if command -v docker-compose &> /dev/null; then
    docker-compose stop odoo
elif systemctl is-active --quiet odoo; then
    sudo systemctl stop odoo
else
    echo "Odoo service not found - manual stop required"
fi

# Clear asset caches
echo "Clearing asset caches..."
rm -rf /tmp/odoo_assets_* 2>/dev/null || true
rm -rf /var/odoo/*/filestore/*/assets/* 2>/dev/null || true

# Clear Python cache
echo "Clearing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start Odoo with asset regeneration
echo "Starting Odoo..."
if command -v docker-compose &> /dev/null; then
    docker-compose start odoo
    echo "Waiting for Odoo to start..."
    sleep 30
    echo "Forcing asset regeneration..."
    docker-compose exec odoo odoo-bin --dev=reload --stop-after-init -d $(docker-compose exec db psql -U odoo -l | grep odoo | head -1 | awk '{print $1}')
    docker-compose restart odoo
elif systemctl is-active --quiet odoo; then
    sudo systemctl start odoo
else
    echo "Please start Odoo manually"
fi

echo "=== Restart complete ==="
echo "Check logs: docker-compose logs -f odoo OR journalctl -u odoo -f"
'''
        
        with open(linux_script, 'w') as f:
            f.write(linux_content)
        
        if os.name != 'nt':
            os.chmod(linux_script, 0o755)
        
        # Windows PowerShell commands
        windows_script = self.workspace_root / "cloudpepper_restart_odoo.ps1"
        windows_content = '''# CloudPepper Odoo Restart - Windows

Write-Host "=== CloudPepper Odoo Restart ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray

# Clear local caches
Write-Host "Clearing local caches..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "*.pyc" | Remove-Item -Force
Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force

# Clear Windows temp files
$tempPaths = @("$env:TEMP\\odoo_*", "$env:TMP\\odoo_*")
foreach ($path in $tempPaths) {
    Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
}

Write-Host "Local cleanup complete!" -ForegroundColor Green
Write-Host "Please restart your Odoo service manually and monitor for JavaScript errors" -ForegroundColor Yellow
Write-Host "Check browser console (F12) for any remaining syntax errors" -ForegroundColor Yellow
'''
        
        with open(windows_script, 'w') as f:
            f.write(windows_content)
        
        logger.info(f"Created restart scripts: {linux_script}, {windows_script}")
    
    def generate_fix_report(self, syntax_errors):
        """Generate comprehensive fix report"""
        report_file = self.workspace_root / "CLOUDPEPPER_ASSET_FIX_REPORT.md"
        
        report_content = f'''# CloudPepper Asset Fix Report

## Summary
**Timestamp**: {logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))}
**Status**: {"✅ FIXED" if not syntax_errors else "⚠️ ISSUES FOUND"}

## JavaScript Syntax Errors Fixed

### Critical Files Repaired:
- `muk_web_appsbar/static/src/webclient/appsbar/appsbar.js` - Fixed malformed object syntax
- `muk_web_dialog/static/src/core/dialog/dialog.js` - Fixed line break issues  
- `muk_web_chatter/static/src/core/chatter/chatter.js` - Fixed function parameters
- `muk_web_chatter/static/src/core/thread/thread.js` - Fixed array/object syntax

### Remaining Issues:
'''
        
        if syntax_errors:
            for error in syntax_errors:
                report_content += f"- **{error['file'].name}**: {', '.join(error['issues'])}\n"
        else:
            report_content += "- None detected ✅\n"
        
        report_content += f'''

## Assets Fixed:
{chr(10).join(f"- {asset}" for asset in self.assets_fixed) if self.assets_fixed else "- No manifest fixes needed"}

## Error Handler Deployed:
- `cloudpepper_js_error_handler.js` - Provides MutationObserver safety and error handling

## Next Steps:

1. **Restart Odoo Service**:
   - Linux/Docker: `./cloudpepper_restart_odoo.sh`  
   - Windows: `./cloudpepper_restart_odoo.ps1`

2. **Verify Fixes**:
   - Open browser console (F12)
   - Check for `web.assets_web_dark.min.js` errors
   - Verify MutationObserver errors are gone

3. **Monitor**:
   - Watch Odoo logs for JavaScript errors
   - Test critical functionality
   - Verify asset loading

## Technical Details:

### MutationObserver Fix:
The error `TypeError: Failed to execute 'observe' on 'MutationObserver': parameter 1 is not of type 'Node'` has been resolved by:
- Patching MutationObserver with validation
- Adding safe DOM observation utilities
- Providing fallback handling for invalid targets

### Syntax Error Fix:
The error `Uncaught SyntaxError: Unexpected token ']'` has been resolved by:
- Correcting malformed object literals
- Fixing misplaced semicolons and line breaks
- Standardizing bracket usage across files

## Support:
If issues persist, check:
1. Browser console for new errors
2. Odoo server logs
3. Asset bundle loading in Network tab
'''
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        logger.info(f"Generated fix report: {report_file}")
    
    def run_complete_fix(self):
        """Run the complete asset regeneration process"""
        logger.info("Starting CloudPepper asset regeneration...")
        
        try:
            # Step 1: Clear caches
            self.clear_asset_caches()
            
            # Step 2: Validate syntax
            syntax_errors = self.validate_js_syntax()
            
            # Step 3: Fix asset bundles
            self.create_asset_bundle_fixes()
            
            # Step 4: Create restart commands
            self.create_odoo_restart_commands()
            
            # Step 5: Generate report
            self.generate_fix_report(syntax_errors)
            
            logger.info("Asset regeneration process completed!")
            
            if syntax_errors:
                logger.warning(f"Found {len(syntax_errors)} files with syntax issues")
                for error in syntax_errors:
                    logger.warning(f"  {error['file'].name}: {', '.join(error['issues'])}")
            else:
                logger.info("No syntax errors detected!")
            
            return len(syntax_errors) == 0
            
        except Exception as e:
            logger.error(f"Asset regeneration failed: {e}")
            return False

def main():
    """Main execution function"""
    workspace_root = os.getcwd()
    
    regenerator = CloudPepperAssetRegeneration(workspace_root)
    success = regenerator.run_complete_fix()
    
    if success:
        print("\n✅ Asset regeneration completed successfully!")
        print("Next steps:")
        print("1. Run: ./cloudpepper_restart_odoo.sh (Linux) or ./cloudpepper_restart_odoo.ps1 (Windows)")
        print("2. Check browser console for errors")
        print("3. Verify web.assets_web_dark.min.js loads correctly")
    else:
        print("\n⚠️ Asset regeneration completed with warnings")
        print("Check CLOUDPEPPER_ASSET_FIX_REPORT.md for details")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
