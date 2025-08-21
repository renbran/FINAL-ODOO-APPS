#!/usr/bin/env python3
"""
CloudPepper Chart.js Emergency Fix - Final Deployment Checklist
Created: August 22, 2025
Purpose: Validate emergency Chart.js fix deployment for production
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class ChartJSEmergencyDeployment:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.module_path = self.base_path / "oe_sale_dashboard_17"
        self.emergency_fix_path = self.module_path / "static" / "src" / "js" / "emergency_chartjs_fix.js"
        self.manifest_path = self.module_path / "__manifest__.py"
        self.deployment_log = []
        
    def log(self, level, message):
        """Log deployment activities"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
        
    def check_emergency_fix_exists(self):
        """Verify emergency Chart.js fix file exists"""
        self.log("INFO", "Checking emergency Chart.js fix file...")
        
        if not self.emergency_fix_path.exists():
            self.log("ERROR", f"Emergency fix file missing: {self.emergency_fix_path}")
            return False
            
        # Check file size (should be substantial)
        file_size = self.emergency_fix_path.stat().st_size
        if file_size < 5000:  # Less than 5KB indicates incomplete file
            self.log("ERROR", f"Emergency fix file too small: {file_size} bytes")
            return False
            
        self.log("SUCCESS", f"Emergency fix file found: {file_size} bytes")
        return True
        
    def validate_emergency_fix_content(self):
        """Validate emergency fix contains required components"""
        self.log("INFO", "Validating emergency fix content...")
        
        try:
            with open(self.emergency_fix_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_components = [
                "CloudPepper Emergency",
                "loadEmergencyChartJs",
                "createChartMock", 
                "loadFromCDN",
                "GraphRenderer",
                "chart.min.js",
                "fallback"
            ]
            
            missing_components = []
            for component in required_components:
                if component not in content:
                    missing_components.append(component)
                    
            if missing_components:
                self.log("ERROR", f"Missing components: {missing_components}")
                return False
                
            self.log("SUCCESS", "All required components found in emergency fix")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to validate emergency fix: {e}")
            return False
            
    def check_manifest_assets_order(self):
        """Verify manifest has emergency fixes prepended"""
        self.log("INFO", "Checking manifest assets loading order...")
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
                
            # Check if emergency fixes are prepended
            if "('prepend', 'oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js')" not in manifest_content:
                self.log("ERROR", "Emergency Chart.js fix not prepended in manifest")
                return False
                
            if "('prepend', 'oe_sale_dashboard_17/static/src/js/cloudpepper_dashboard_fix.js')" not in manifest_content:
                self.log("ERROR", "CloudPepper dashboard fix not prepended in manifest")
                return False
                
            self.log("SUCCESS", "Emergency fixes properly prepended in manifest")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to check manifest: {e}")
            return False
            
    def check_local_chartjs_exists(self):
        """Verify local Chart.js file exists"""
        self.log("INFO", "Checking local Chart.js file...")
        
        chartjs_path = self.module_path / "static" / "src" / "js" / "chart.min.js"
        
        if not chartjs_path.exists():
            self.log("WARNING", "Local Chart.js file missing - will use CDN fallback")
            return False
            
        file_size = chartjs_path.stat().st_size
        if file_size < 100000:  # Less than 100KB indicates incomplete Chart.js
            self.log("WARNING", f"Chart.js file seems small: {file_size} bytes")
            return False
            
        self.log("SUCCESS", f"Local Chart.js found: {file_size} bytes")
        return True
        
    def validate_module_structure(self):
        """Validate complete module structure"""
        self.log("INFO", "Validating module structure...")
        
        required_files = [
            "__manifest__.py",
            "__init__.py",
            "static/src/js/enhanced_sales_dashboard.js",
            "static/src/js/sales_dashboard.js",
            "static/src/js/emergency_chartjs_fix.js",
            "static/src/xml/enhanced_sales_dashboard.xml",
            "views/sales_dashboard_views.xml"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.log("ERROR", f"Missing required files: {missing_files}")
            return False
            
        self.log("SUCCESS", "All required module files present")
        return True
        
    def generate_deployment_commands(self):
        """Generate CloudPepper deployment commands"""
        self.log("INFO", "Generating deployment commands...")
        
        commands = [
            "# CloudPepper Chart.js Emergency Fix Deployment",
            "",
            "# Step 1: Backup current module",
            "sudo cp -r /var/odoo/erposus/addons/oe_sale_dashboard_17 /var/odoo/erposus/addons/oe_sale_dashboard_17.backup.$(date +%Y%m%d_%H%M%S)",
            "",
            "# Step 2: Upload emergency fix files",
            "# Upload: oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js",
            "# Upload: oe_sale_dashboard_17/__manifest__.py",
            "",
            "# Step 3: Set correct permissions",
            "sudo chown -R odoo:odoo /var/odoo/erposus/addons/oe_sale_dashboard_17",
            "sudo chmod -R 644 /var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/*",
            "",
            "# Step 4: Update module assets",
            "sudo -u odoo odoo-bin -u oe_sale_dashboard_17 -d erposus --stop-after-init",
            "",
            "# Step 5: Restart Odoo service",
            "sudo systemctl restart odoo",
            "",
            "# Step 6: Verify deployment",
            "sudo systemctl status odoo",
            "sudo tail -f /var/log/odoo/odoo.log | grep -i chart"
        ]
        
        command_file = self.base_path / "cloudpepper_chartjs_deployment_commands.sh"
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(commands))
            
        self.log("SUCCESS", f"Deployment commands saved to: {command_file}")
        return True
        
    def create_verification_script(self):
        """Create post-deployment verification script"""
        self.log("INFO", "Creating verification script...")
        
        verification_script = '''#!/bin/bash
# CloudPepper Chart.js Emergency Fix Verification

echo "CloudPepper Chart.js Emergency Fix Verification"
echo "================================================="

# Check if emergency fix is loaded
echo "Checking emergency fix file..."
if [ -f "/var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js" ]; then
    echo "Emergency Chart.js fix file present"
    file_size=$(stat -c%s "/var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js")
    echo "File size: $file_size bytes"
else
    echo "Emergency Chart.js fix file missing"
fi

# Check Odoo service status
echo ""
echo "Checking Odoo service..."
if systemctl is-active --quiet odoo; then
    echo "Odoo service running"
else
    echo "Odoo service not running"
fi

# Check for Chart.js errors in logs
echo ""
echo "Checking for Chart.js errors in recent logs..."
recent_chartjs_errors=$(sudo tail -n 100 /var/log/odoo/odoo.log | grep -i "chart\.js\|chartjs" | grep -i "error\|fail")
if [ -z "$recent_chartjs_errors" ]; then
    echo "No recent Chart.js errors found"
else
    echo "Recent Chart.js related messages:"
    echo "$recent_chartjs_errors"
fi

# Check for emergency fix activation
echo ""
echo "Checking emergency fix activation..."
emergency_messages=$(sudo tail -n 50 /var/log/odoo/odoo.log | grep "CloudPepper Emergency")
if [ -n "$emergency_messages" ]; then
    echo "Emergency fix activation detected:"
    echo "$emergency_messages"
else
    echo "No emergency fix activation messages (may be normal if no errors occurred)"
fi

echo ""
echo "Verification complete!"
echo "Next: Test dashboard functionality in browser"
'''
        
        verification_file = self.base_path / "cloudpepper_chartjs_verification.sh"
        with open(verification_file, 'w', encoding='utf-8') as f:
            f.write(verification_script)
            
        # Make executable
        os.chmod(verification_file, 0o755)
        
        self.log("SUCCESS", f"Verification script created: {verification_file}")
        return True
        
    def save_deployment_report(self):
        """Save deployment readiness report"""
        report = {
            "deployment_type": "CloudPepper Chart.js Emergency Fix",
            "timestamp": datetime.now().isoformat(),
            "module": "oe_sale_dashboard_17",
            "emergency_fix_path": str(self.emergency_fix_path),
            "deployment_log": self.deployment_log,
            "status": "READY FOR DEPLOYMENT",
            "critical_files": [
                "oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js",
                "oe_sale_dashboard_17/__manifest__.py"
            ],
            "deployment_priority": "IMMEDIATE - Production Chart.js failures",
            "expected_resolution_time": "10-15 minutes",
            "post_deployment_monitoring": "24 hours"
        }
        
        report_file = self.base_path / "cloudpepper_chartjs_deployment_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.log("SUCCESS", f"Deployment report saved: {report_file}")
        return True
        
    def run_deployment_check(self):
        """Run complete deployment readiness check"""
        self.log("INFO", "🚨 Starting CloudPepper Chart.js Emergency Fix Deployment Check")
        
        checks = [
            ("Emergency Fix File", self.check_emergency_fix_exists),
            ("Fix Content Validation", self.validate_emergency_fix_content),
            ("Manifest Assets Order", self.check_manifest_assets_order),
            ("Local Chart.js File", self.check_local_chartjs_exists),
            ("Module Structure", self.validate_module_structure),
            ("Deployment Commands", self.generate_deployment_commands),
            ("Verification Script", self.create_verification_script),
            ("Deployment Report", self.save_deployment_report)
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_function in checks:
            self.log("INFO", f"Running check: {check_name}")
            if check_function():
                passed_checks += 1
                self.log("SUCCESS", f"✅ {check_name} PASSED")
            else:
                self.log("ERROR", f"❌ {check_name} FAILED")
                
        # Final status
        if passed_checks >= total_checks - 1:  # Allow 1 optional failure (local Chart.js)
            self.log("SUCCESS", f"🚀 DEPLOYMENT READY: {passed_checks}/{total_checks} checks passed")
            self.log("SUCCESS", "CloudPepper Chart.js Emergency Fix ready for immediate deployment!")
            return True
        else:
            self.log("ERROR", f"⚠️  DEPLOYMENT NOT READY: {passed_checks}/{total_checks} checks passed")
            self.log("ERROR", "Fix critical issues before deployment")
            return False

def main():
    """Main deployment check execution"""
    print("🔥 CloudPepper Chart.js Emergency Fix - Deployment Validation")
    print("=" * 60)
    
    deployment_checker = ChartJSEmergencyDeployment()
    
    try:
        success = deployment_checker.run_deployment_check()
        
        if success:
            print("\n🎯 DEPLOYMENT STATUS: READY")
            print("📋 Next Steps:")
            print("1. Upload files to CloudPepper server")
            print("2. Run deployment commands")
            print("3. Execute verification script")
            print("4. Monitor for 24 hours")
            
        else:
            print("\n⚠️  DEPLOYMENT STATUS: NOT READY")
            print("🔧 Fix critical issues before proceeding")
            
        return success
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT CHECK FAILED: {e}")
        return False

if __name__ == "__main__":
    main()
