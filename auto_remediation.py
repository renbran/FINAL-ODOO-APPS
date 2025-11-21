#!/usr/bin/env python3
"""
Automated CloudPepper Compliance Remediation Tool
Detects issues and automatically fixes them one by one
"""

import sys
import json
import time
from datetime import datetime
from collections import defaultdict

try:
    import paramiko
except ImportError:
    print("ERROR: paramiko module not installed")
    print("Install with: pip install paramiko")
    sys.exit(1)

# Configuration
REMOTE_HOST = "139.84.163.11"
REMOTE_PORT = 22
REMOTE_USER = "root"
SSH_KEY_PATH = "/tmp/ssh_key"

class AutoRemediator:
    def __init__(self, host, port, username, key_path, interactive=True, dry_run=False):
        self.host = host
        self.port = port
        self.username = username
        self.key_path = key_path
        self.client = None
        self.interactive = interactive
        self.dry_run = dry_run

        # Tracking
        self.issues_detected = []
        self.issues_fixed = []
        self.issues_failed = []
        self.issues_skipped = []

    def connect(self):
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            print(f"🔌 Connecting to {self.username}@{self.host}:{self.port}...")
            private_key = paramiko.Ed25519Key.from_private_key_file(self.key_path)

            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                pkey=private_key,
                timeout=10
            )
            print("✓ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def execute_command(self, command, silent=False):
        """Execute remote command and return output"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=120)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()

            if not silent and exit_code != 0 and error:
                print(f"  ⚠ {error[:200]}")

            return output.strip(), exit_code
        except Exception as e:
            if not silent:
                print(f"  ✗ Error: {e}")
            return "", -1

    def ask_confirmation(self, message, default="y"):
        """Ask user for confirmation"""
        if not self.interactive:
            return default.lower() == "y"

        valid = {"yes": True, "y": True, "no": False, "n": False}
        prompt = f"{message} [Y/n]: " if default == "y" else f"{message} [y/N]: "

        while True:
            choice = input(prompt).lower() or default
            if choice in valid:
                return valid[choice]
            print("  Please respond with 'y' or 'n'")

    def log_fix(self, issue, status, details=""):
        """Log fix attempt"""
        log_entry = {
            "issue": issue,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        if status == "fixed":
            self.issues_fixed.append(log_entry)
        elif status == "failed":
            self.issues_failed.append(log_entry)
        elif status == "skipped":
            self.issues_skipped.append(log_entry)

    # ========================================================================
    # DETECTION METHODS
    # ========================================================================

    def detect_all_issues(self):
        """Detect all issues"""
        print("="*70)
        print("🔍 DETECTING ISSUES")
        print("="*70 + "\n")

        self.issues_detected = []

        # Check each category
        self.check_postgresql_service()
        self.check_odoo_service()
        self.check_users()
        self.check_directories()
        self.check_odoo_config()
        self.check_postgresql_config()
        self.check_firewall()
        self.check_backups()
        self.check_security()
        self.check_disk_space()

        print(f"\n📊 Found {len(self.issues_detected)} issue(s) to address\n")
        return self.issues_detected

    def check_postgresql_service(self):
        """Check if PostgreSQL is running"""
        print("🐘 Checking PostgreSQL service...")
        output, code = self.execute_command("systemctl is-active postgresql", silent=True)

        if code != 0 or "active" not in output:
            self.issues_detected.append({
                "id": "postgresql_service_down",
                "category": "PostgreSQL",
                "severity": "CRITICAL",
                "description": "PostgreSQL service is not running",
                "auto_fixable": True
            })
            print("  ✗ PostgreSQL is not running")
        else:
            print("  ✓ PostgreSQL is running")

    def check_odoo_service(self):
        """Check if Odoo is running"""
        print("🟣 Checking Odoo service...")
        output, code = self.execute_command("ps aux | grep odoo-bin | grep -v grep", silent=True)

        if code != 0 or not output:
            # Check if service exists
            service_check, _ = self.execute_command("systemctl list-unit-files | grep odoo", silent=True)
            if service_check:
                self.issues_detected.append({
                    "id": "odoo_service_down",
                    "category": "Odoo",
                    "severity": "CRITICAL",
                    "description": "Odoo service is not running",
                    "auto_fixable": True
                })
                print("  ✗ Odoo is not running")
            else:
                print("  ⚠ Odoo service not found (may need manual setup)")
        else:
            print("  ✓ Odoo is running")

    def check_users(self):
        """Check system users"""
        print("👥 Checking system users...")

        # Check odoo user
        output, code = self.execute_command("id odoo 2>/dev/null", silent=True)
        if code != 0:
            self.issues_detected.append({
                "id": "odoo_user_missing",
                "category": "Users",
                "severity": "CRITICAL",
                "description": "Odoo user does not exist",
                "auto_fixable": True
            })
            print("  ✗ Odoo user missing")
        else:
            print("  ✓ Odoo user exists")

            # Check shell
            shell_output, _ = self.execute_command("getent passwd odoo | cut -d: -f7")
            if shell_output and "/bin/bash" in shell_output:
                self.issues_detected.append({
                    "id": "odoo_user_has_shell",
                    "category": "Security",
                    "severity": "MEDIUM",
                    "description": "Odoo user has login shell (security risk)",
                    "auto_fixable": True
                })
                print("  ⚠ Odoo user has login shell")

    def check_directories(self):
        """Check required directories"""
        print("📁 Checking directory structure...")

        required_dirs = {
            "/opt/odoo": "Odoo installation",
            "/var/log/odoo": "Odoo logs",
            "/opt/odoo/.local/share/Odoo": "Odoo data directory",
        }

        for directory, description in required_dirs.items():
            output, code = self.execute_command(f"test -d {directory} && echo 'exists' || echo 'missing'", silent=True)

            if "missing" in output:
                self.issues_detected.append({
                    "id": f"directory_missing_{directory.replace('/', '_')}",
                    "category": "Directories",
                    "severity": "HIGH",
                    "description": f"Directory {directory} is missing",
                    "directory": directory,
                    "auto_fixable": True
                })
                print(f"  ✗ {directory} missing")
            else:
                # Check ownership
                owner_output, _ = self.execute_command(f"stat -c '%U:%G' {directory}")
                if "odoo" not in owner_output:
                    self.issues_detected.append({
                        "id": f"directory_wrong_owner_{directory.replace('/', '_')}",
                        "category": "Directories",
                        "severity": "HIGH",
                        "description": f"Directory {directory} has wrong ownership ({owner_output})",
                        "directory": directory,
                        "current_owner": owner_output,
                        "auto_fixable": True
                    })
                    print(f"  ⚠ {directory} - wrong owner: {owner_output}")
                else:
                    print(f"  ✓ {directory} - correct")

    def check_odoo_config(self):
        """Check Odoo configuration"""
        print("⚙️  Checking Odoo configuration...")

        # Check if config exists
        config_paths = ["/etc/odoo.conf", "/etc/odoo-server.conf"]
        config_file = None

        for path in config_paths:
            output, code = self.execute_command(f"test -f {path} && echo '{path}'", silent=True)
            if output:
                config_file = output.strip()
                break

        if not config_file:
            self.issues_detected.append({
                "id": "odoo_config_missing",
                "category": "Configuration",
                "severity": "CRITICAL",
                "description": "Odoo configuration file not found",
                "auto_fixable": False  # Needs user input for DB password
            })
            print("  ✗ Odoo config file missing")
            return

        print(f"  ✓ Config file found: {config_file}")

        # Check workers configuration
        config_content, _ = self.execute_command(f"cat {config_file}")

        if "workers" not in config_content or "workers = 0" in config_content or "workers=0" in config_content:
            self.issues_detected.append({
                "id": "odoo_workers_not_configured",
                "category": "Performance",
                "severity": "HIGH",
                "description": "Odoo workers not configured (single-process mode)",
                "config_file": config_file,
                "auto_fixable": True
            })
            print("  ⚠ Workers not configured")

    def check_postgresql_config(self):
        """Check PostgreSQL configuration"""
        print("🔧 Checking PostgreSQL configuration...")

        # Check if we can connect
        output, code = self.execute_command("sudo -u postgres psql -c '\\l' 2>&1", silent=True)
        if code != 0:
            print("  ⚠ Cannot check PostgreSQL config (connection failed)")
            return

        # Check max_connections
        max_conn, _ = self.execute_command("sudo -u postgres psql -t -c 'SHOW max_connections;'", silent=True)
        if max_conn:
            max_conn_num = int(max_conn.strip())
            if max_conn_num < 100:
                self.issues_detected.append({
                    "id": "postgresql_low_max_connections",
                    "category": "PostgreSQL",
                    "severity": "MEDIUM",
                    "description": f"max_connections is {max_conn_num} (should be >= 100)",
                    "current_value": max_conn_num,
                    "auto_fixable": False  # Requires restart and config file edit
                })
                print(f"  ⚠ max_connections = {max_conn_num} (low)")
            else:
                print(f"  ✓ max_connections = {max_conn_num}")

    def check_firewall(self):
        """Check firewall configuration"""
        print("🔒 Checking firewall...")

        output, code = self.execute_command("ufw status 2>/dev/null", silent=True)
        if code == 0:
            if "Status: active" not in output:
                self.issues_detected.append({
                    "id": "firewall_inactive",
                    "category": "Security",
                    "severity": "HIGH",
                    "description": "UFW firewall is not active",
                    "auto_fixable": True  # But requires confirmation
                })
                print("  ⚠ Firewall inactive")
            else:
                print("  ✓ Firewall active")

    def check_backups(self):
        """Check backup configuration"""
        print("💾 Checking backups...")

        # Check for backup directories
        backup_dirs = ["/backup/odoo", "/backup", "/backups", "/var/backups/odoo"]
        found_backup = False

        for backup_dir in backup_dirs:
            output, code = self.execute_command(f"test -d {backup_dir} && echo 'exists'", silent=True)
            if "exists" in output:
                found_backup = True
                break

        if not found_backup:
            self.issues_detected.append({
                "id": "backup_directory_missing",
                "category": "Backups",
                "severity": "MEDIUM",
                "description": "No backup directory found",
                "auto_fixable": True
            })
            print("  ⚠ No backup directory")
        else:
            print("  ✓ Backup directory exists")

        # Check cron jobs
        cron_output, code = self.execute_command("crontab -l 2>/dev/null | grep -i backup", silent=True)
        if code != 0 or not cron_output:
            self.issues_detected.append({
                "id": "backup_cron_missing",
                "category": "Backups",
                "severity": "MEDIUM",
                "description": "No backup cron job configured",
                "auto_fixable": False  # Requires DB name input
            })
            print("  ⚠ No backup cron job")

    def check_security(self):
        """Check security settings"""
        print("🔐 Checking security settings...")

        # Check PostgreSQL external exposure
        pg_listen, _ = self.execute_command("ss -tlnp | grep 5432", silent=True)
        if pg_listen and "0.0.0.0:5432" in pg_listen:
            self.issues_detected.append({
                "id": "postgresql_exposed_externally",
                "category": "Security",
                "severity": "CRITICAL",
                "description": "PostgreSQL is listening on external interface (security risk)",
                "auto_fixable": False  # Requires config edit and restart
            })
            print("  ✗ PostgreSQL exposed externally")
        elif pg_listen:
            print("  ✓ PostgreSQL listening locally only")

    def check_disk_space(self):
        """Check disk space"""
        print("💽 Checking disk space...")

        disk_output, _ = self.execute_command("df -h / | awk 'NR==2 {print $5}' | sed 's/%//'")
        if disk_output:
            usage = int(disk_output.strip())
            if usage >= 90:
                self.issues_detected.append({
                    "id": "disk_space_critical",
                    "category": "Resources",
                    "severity": "CRITICAL",
                    "description": f"Disk space critical: {usage}%",
                    "usage": usage,
                    "auto_fixable": False  # Needs manual cleanup
                })
                print(f"  ✗ Disk space critical: {usage}%")
            elif usage >= 80:
                self.issues_detected.append({
                    "id": "disk_space_high",
                    "category": "Resources",
                    "severity": "MEDIUM",
                    "description": f"Disk space high: {usage}%",
                    "usage": usage,
                    "auto_fixable": False
                })
                print(f"  ⚠ Disk space high: {usage}%")
            else:
                print(f"  ✓ Disk space: {usage}%")

    # ========================================================================
    # FIX METHODS
    # ========================================================================

    def fix_issue(self, issue):
        """Attempt to fix an issue"""
        issue_id = issue['id']

        print(f"\n{'='*70}")
        print(f"🔧 Fixing: {issue['description']}")
        print(f"   Category: {issue['category']}")
        print(f"   Severity: {issue['severity']}")
        print(f"{'='*70}")

        if not issue.get('auto_fixable', False):
            print("  ⚠ This issue requires manual intervention")
            self.log_fix(issue['description'], "skipped", "Not auto-fixable")
            return False

        # Get appropriate fix method
        fix_method = getattr(self, f"fix_{issue_id}", None)

        if not fix_method:
            print(f"  ⚠ No automated fix available for: {issue_id}")
            self.log_fix(issue['description'], "skipped", "No fix method")
            return False

        # Ask for confirmation if interactive
        if self.interactive:
            if not self.ask_confirmation(f"  Apply fix?"):
                print("  ⊘ Skipped by user")
                self.log_fix(issue['description'], "skipped", "User declined")
                return False

        # Apply fix
        if self.dry_run:
            print("  [DRY RUN] Would apply fix")
            self.log_fix(issue['description'], "skipped", "Dry run mode")
            return False

        try:
            success = fix_method(issue)
            if success:
                print("  ✅ Fixed successfully!")
                self.log_fix(issue['description'], "fixed")
                time.sleep(1)  # Give services time to start
                return True
            else:
                print("  ✗ Fix failed")
                self.log_fix(issue['description'], "failed")
                return False
        except Exception as e:
            print(f"  ✗ Fix error: {e}")
            self.log_fix(issue['description'], "failed", str(e))
            return False

    # ========================================================================
    # SPECIFIC FIX IMPLEMENTATIONS
    # ========================================================================

    def fix_postgresql_service_down(self, issue):
        """Start PostgreSQL service"""
        print("  → Starting PostgreSQL service...")
        output, code = self.execute_command("systemctl start postgresql")

        if code == 0:
            # Enable on boot
            self.execute_command("systemctl enable postgresql")

            # Verify
            time.sleep(2)
            verify_output, verify_code = self.execute_command("systemctl is-active postgresql")
            return verify_code == 0 and "active" in verify_output
        return False

    def fix_odoo_service_down(self, issue):
        """Start Odoo service"""
        print("  → Starting Odoo service...")

        # Try to find service name
        service_list, _ = self.execute_command("systemctl list-unit-files | grep odoo | awk '{print $1}'")

        if service_list:
            service_name = service_list.strip().split('\n')[0]
            print(f"  → Found service: {service_name}")

            output, code = self.execute_command(f"systemctl start {service_name}")

            if code == 0:
                self.execute_command(f"systemctl enable {service_name}")
                time.sleep(3)

                # Verify
                verify_output, verify_code = self.execute_command("ps aux | grep odoo-bin | grep -v grep")
                return verify_code == 0 and len(verify_output) > 0

        return False

    def fix_odoo_user_missing(self, issue):
        """Create odoo user"""
        print("  → Creating odoo system user...")
        output, code = self.execute_command(
            "adduser --system --home=/opt/odoo --group odoo"
        )

        if code == 0:
            # Set no login shell
            self.execute_command("usermod -s /usr/sbin/nologin odoo")

            # Verify
            verify_output, verify_code = self.execute_command("id odoo")
            return verify_code == 0

        return False

    def fix_odoo_user_has_shell(self, issue):
        """Remove login shell from odoo user"""
        print("  → Disabling odoo user login shell...")
        output, code = self.execute_command("usermod -s /usr/sbin/nologin odoo")

        if code == 0:
            # Verify
            verify_output, _ = self.execute_command("getent passwd odoo | cut -d: -f7")
            return "nologin" in verify_output or "false" in verify_output

        return False

    def fix_directory_missing_(self, issue):
        """Create missing directory"""
        directory = issue.get('directory', '')
        if not directory:
            return False

        print(f"  → Creating directory: {directory}")
        output, code = self.execute_command(f"mkdir -p {directory}")

        if code == 0:
            # Set ownership
            self.execute_command(f"chown odoo:odoo {directory}")
            self.execute_command(f"chmod 755 {directory}")

            # Verify
            verify_output, verify_code = self.execute_command(f"test -d {directory} && echo 'exists'")
            return "exists" in verify_output

        return False

    def fix_directory_wrong_owner_(self, issue):
        """Fix directory ownership"""
        directory = issue.get('directory', '')
        if not directory:
            return False

        print(f"  → Fixing ownership: {directory}")
        output, code = self.execute_command(f"chown -R odoo:odoo {directory}")

        if code == 0:
            # Verify
            verify_output, _ = self.execute_command(f"stat -c '%U:%G' {directory}")
            return "odoo:odoo" in verify_output

        return False

    def fix_odoo_workers_not_configured(self, issue):
        """Configure Odoo workers"""
        config_file = issue.get('config_file', '/etc/odoo.conf')

        # Calculate workers: (CPU cores * 2) + 1
        cpu_output, _ = self.execute_command("nproc")
        cpu_count = int(cpu_output.strip()) if cpu_output else 1
        workers = min((cpu_count * 2) + 1, 8)  # Cap at 8

        print(f"  → Setting workers = {workers} (based on {cpu_count} CPUs)")

        # Check if workers line exists
        config_content, _ = self.execute_command(f"cat {config_file}")

        if "workers" in config_content:
            # Update existing line
            cmd = f"sed -i 's/^workers.*/workers = {workers}/' {config_file}"
        else:
            # Add workers line
            cmd = f"sed -i '/^\\[options\\]/a workers = {workers}' {config_file}"

        output, code = self.execute_command(cmd)

        if code == 0:
            # Also add memory limits if not present
            if "limit_memory_hard" not in config_content:
                self.execute_command(f"sed -i '/^workers/a limit_memory_hard = 2684354560' {config_file}")
                self.execute_command(f"sed -i '/^workers/a limit_memory_soft = 2147483648' {config_file}")

            # Restart Odoo
            print("  → Restarting Odoo...")
            service_list, _ = self.execute_command("systemctl list-unit-files | grep odoo | awk '{print $1}'")
            if service_list:
                service_name = service_list.strip().split('\n')[0]
                self.execute_command(f"systemctl restart {service_name}")
                time.sleep(3)

            return True

        return False

    def fix_firewall_inactive(self, issue):
        """Enable UFW firewall"""
        print("  ⚠ IMPORTANT: This will enable the firewall!")
        print("  → Ensuring SSH port 22 is allowed first...")

        # CRITICAL: Allow SSH first!
        self.execute_command("ufw allow 22/tcp")
        self.execute_command("ufw allow 80/tcp")
        self.execute_command("ufw allow 443/tcp")

        print("  → Enabling firewall...")
        output, code = self.execute_command("yes | ufw enable")

        if code == 0:
            # Verify
            verify_output, _ = self.execute_command("ufw status")
            return "Status: active" in verify_output

        return False

    def fix_backup_directory_missing(self, issue):
        """Create backup directory"""
        backup_dir = "/backup/odoo"

        print(f"  → Creating backup directory structure...")
        self.execute_command(f"mkdir -p {backup_dir}/database")
        self.execute_command(f"mkdir -p {backup_dir}/filestore")
        self.execute_command(f"chown -R odoo:odoo {backup_dir}")
        self.execute_command(f"chmod 750 {backup_dir}")

        # Verify
        verify_output, verify_code = self.execute_command(f"test -d {backup_dir} && echo 'exists'")
        return "exists" in verify_output

    # ========================================================================
    # ORCHESTRATION
    # ========================================================================

    def run_auto_remediation(self):
        """Main remediation orchestration"""
        print("="*70)
        print("🤖 AUTOMATED CLOUDPEPPER REMEDIATION")
        print(f"Server: {self.host}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE FIX'}")
        print(f"Interactive: {'Yes' if self.interactive else 'No'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # Detect issues
        issues = self.detect_all_issues()

        if not issues:
            print("\n🎉 No issues detected! System is healthy.\n")
            return

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 99))

        # Show summary
        print("\n" + "="*70)
        print("📋 ISSUES SUMMARY")
        print("="*70)

        auto_fixable = [i for i in issues if i.get('auto_fixable', False)]
        manual_only = [i for i in issues if not i.get('auto_fixable', False)]

        print(f"\n✅ Auto-fixable issues: {len(auto_fixable)}")
        for issue in auto_fixable:
            print(f"  • [{issue['severity']}] {issue['description']}")

        print(f"\n⚠️  Manual intervention needed: {len(manual_only)}")
        for issue in manual_only:
            print(f"  • [{issue['severity']}] {issue['description']}")

        if not auto_fixable:
            print("\n⚠️  No auto-fixable issues found. Please review manual fixes.")
            return

        # Confirm to proceed
        if self.interactive and not self.dry_run:
            print("\n" + "="*70)
            if not self.ask_confirmation(f"Proceed with fixing {len(auto_fixable)} issue(s)?"):
                print("❌ Remediation cancelled by user")
                return

        # Fix each auto-fixable issue
        print("\n" + "="*70)
        print("🔧 APPLYING FIXES")
        print("="*70)

        for i, issue in enumerate(auto_fixable, 1):
            print(f"\n[{i}/{len(auto_fixable)}]")
            self.fix_issue(issue)

        # Final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate final remediation report"""
        print("\n" + "="*70)
        print("📊 REMEDIATION REPORT")
        print("="*70)

        print(f"\n✅ Issues Fixed: {len(self.issues_fixed)}")
        for fix in self.issues_fixed:
            print(f"  ✓ {fix['issue']}")

        print(f"\n❌ Issues Failed: {len(self.issues_failed)}")
        for fail in self.issues_failed:
            print(f"  ✗ {fail['issue']}")
            if fail.get('details'):
                print(f"    Details: {fail['details']}")

        print(f"\n⊘ Issues Skipped: {len(self.issues_skipped)}")
        for skip in self.issues_skipped:
            print(f"  ⊘ {skip['issue']}")
            if skip.get('details'):
                print(f"    Reason: {skip['details']}")

        # Save detailed report
        report_file = f"remediation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "server": self.host,
            "dry_run": self.dry_run,
            "fixed": self.issues_fixed,
            "failed": self.issues_failed,
            "skipped": self.issues_skipped
        }

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved: {report_file}")

        # Next steps
        if self.issues_failed or self.issues_skipped:
            print("\n📝 NEXT STEPS:")
            print("  1. Review failed/skipped issues above")
            print("  2. Consult CLOUDPEPPER_REMEDIATION_GUIDE.md")
            print("  3. Run compliance checker again: python3 cloudpepper_compliance_checker.py")

        print("\n" + "="*70)
        print("✅ REMEDIATION COMPLETE")
        print("="*70 + "\n")

    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("✓ Disconnected from server\n")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated CloudPepper Compliance Remediation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default) - asks before each fix
  python3 auto_remediation.py

  # Automatic mode - fixes all issues without prompting
  python3 auto_remediation.py --auto

  # Dry run - show what would be fixed without making changes
  python3 auto_remediation.py --dry-run

  # Automatic dry run
  python3 auto_remediation.py --auto --dry-run
        """
    )

    parser.add_argument('--auto', action='store_true',
                      help='Non-interactive mode (no confirmation prompts)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be done without making changes')

    args = parser.parse_args()

    remediator = AutoRemediator(
        host=REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        key_path=SSH_KEY_PATH,
        interactive=not args.auto,
        dry_run=args.dry_run
    )

    if not remediator.connect():
        print("\n❌ Failed to connect to server")
        print("\nTroubleshooting:")
        print("  1. Verify server is reachable")
        print("  2. Check SSH key exists: ls -la /tmp/ssh_key")
        print("  3. Verify key permissions: chmod 600 /tmp/ssh_key")
        sys.exit(1)

    try:
        remediator.run_auto_remediation()

        # Exit code based on results
        if len(remediator.issues_failed) > 0:
            sys.exit(2)  # Some fixes failed
        elif len(remediator.issues_fixed) > 0:
            sys.exit(0)  # Success - issues were fixed
        else:
            sys.exit(0)  # No issues found

    except KeyboardInterrupt:
        print("\n\n⚠️  Remediation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during remediation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        remediator.disconnect()


if __name__ == "__main__":
    main()
