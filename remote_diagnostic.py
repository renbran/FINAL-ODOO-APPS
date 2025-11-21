#!/usr/bin/env python3
"""
Remote Odoo 17 Database Diagnostic Tool
Connects to remote server and performs comprehensive health checks
"""

import sys
import os
from datetime import datetime

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

class OdooDiagnostic:
    def __init__(self, host, port, username, key_path):
        self.host = host
        self.port = port
        self.username = username
        self.key_path = key_path
        self.client = None
        self.report = []

    def connect(self):
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            print(f"Connecting to {self.username}@{self.host}:{self.port}...")
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

    def execute_command(self, command, description=None):
        """Execute remote command and return output"""
        if description:
            print(f"→ {description}")
            self.report.append(f"\n{'='*60}\n{description}\n{'='*60}")

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=30)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()

            result = output if output else error
            self.report.append(result)

            if exit_code == 0:
                print(f"  ✓ Success")
            else:
                print(f"  ⚠ Exit code: {exit_code}")

            return result, exit_code
        except Exception as e:
            error_msg = f"  ✗ Error: {e}"
            print(error_msg)
            self.report.append(error_msg)
            return str(e), -1

    def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        print("="*60)
        print("ODOO 17 DATABASE SERVER DIAGNOSTIC")
        print(f"Server: {self.host}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        # 1. System Information
        self.execute_command("hostname", "1. Hostname")
        self.execute_command("cat /etc/os-release | head -5", "2. OS Information")
        self.execute_command("uname -r", "3. Kernel Version")
        self.execute_command("uptime", "4. System Uptime")

        # 2. System Resources
        self.execute_command("free -h", "5. Memory Usage")
        self.execute_command("df -h", "6. Disk Usage")
        self.execute_command("cat /proc/loadavg", "7. Load Average")

        # 3. PostgreSQL Status
        self.execute_command("systemctl status postgresql --no-pager | head -20", "8. PostgreSQL Service Status")
        self.execute_command("sudo -u postgres psql -c 'SELECT version();'", "9. PostgreSQL Version")
        self.execute_command("ss -tlnp | grep postgres", "10. PostgreSQL Listening Port")
        self.execute_command("sudo -u postgres psql -c '\\l'", "11. Database List")
        self.execute_command(
            "sudo -u postgres psql -c \"SELECT datname, pg_size_pretty(pg_database_size(datname)) as size FROM pg_database ORDER BY pg_database_size(datname) DESC;\"",
            "12. Database Sizes"
        )
        self.execute_command(
            "sudo -u postgres psql -c \"SELECT datname, count(*) as connections FROM pg_stat_activity GROUP BY datname;\"",
            "13. Active Database Connections"
        )
        self.execute_command(
            "sudo -u postgres psql -c \"SELECT pid, usename, datname, client_addr, state FROM pg_stat_activity WHERE state != 'idle';\"",
            "14. Active Queries"
        )

        # 4. PostgreSQL Configuration
        self.execute_command("sudo -u postgres psql -c 'SHOW max_connections;'", "15. PostgreSQL Max Connections")
        self.execute_command("sudo -u postgres psql -c 'SHOW shared_buffers;'", "16. PostgreSQL Shared Buffers")
        self.execute_command("sudo -u postgres psql -c 'SHOW config_file;'", "17. PostgreSQL Config File")

        # 5. Odoo Status
        self.execute_command("ps aux | grep odoo | grep -v grep", "18. Odoo Processes")
        self.execute_command("ss -tlnp | grep 8069", "19. Odoo Port (8069)")
        self.execute_command("systemctl list-units | grep odoo", "20. Odoo Service")
        self.execute_command("find /etc -name 'odoo*.conf' 2>/dev/null", "21. Odoo Configuration Files")
        self.execute_command("find /opt /usr /home -name 'odoo-bin' 2>/dev/null | head -5", "22. Odoo Installation Path")

        # 6. Odoo Configuration
        config_check = self.execute_command("find /etc -name 'odoo*.conf' 2>/dev/null | head -1", "23. Finding Odoo Config")
        if config_check[0].strip():
            config_file = config_check[0].strip()
            self.execute_command(f"cat {config_file}", f"24. Odoo Configuration Content ({config_file})")

        # 7. CloudPepper Setup
        self.execute_command("id odoo 2>/dev/null || echo 'Odoo user not found'", "25. Odoo User")
        self.execute_command("id cloudpepper 2>/dev/null || echo 'CloudPepper user not found'", "26. CloudPepper User")
        self.execute_command("ls -la /opt/odoo 2>/dev/null | head -20 || echo 'Directory not found'", "27. /opt/odoo Directory")

        # 8. Network & Security
        self.execute_command("ss -tlnp | head -30", "28. Listening Ports")
        self.execute_command("ufw status verbose 2>/dev/null || echo 'UFW not available'", "29. Firewall Status (UFW)")

        # 9. Web Server
        self.execute_command("systemctl is-active nginx 2>/dev/null || echo 'Nginx not active'", "30. Nginx Status")
        self.execute_command("systemctl is-active apache2 2>/dev/null || echo 'Apache not active'", "31. Apache Status")

        # 10. Logs
        self.execute_command("find /var/log -name '*odoo*.log' 2>/dev/null | head -5", "32. Odoo Log Files")
        log_check = self.execute_command("find /var/log -name '*odoo*.log' 2>/dev/null | head -1", None)
        if log_check[0].strip():
            log_file = log_check[0].strip()
            self.execute_command(f"tail -30 {log_file}", f"33. Recent Odoo Logs ({log_file})")

        # 11. Performance
        self.execute_command("ps aux --sort=-%mem | head -11", "34. Top Memory Processes")
        self.execute_command("ps aux --sort=-%cpu | head -11", "35. Top CPU Processes")

        # 12. Backups
        self.execute_command("crontab -l 2>/dev/null | grep -i backup || echo 'No backup cron jobs'", "36. Backup Cron Jobs")
        self.execute_command("ls -lah /backup 2>/dev/null | head -10 || ls -lah /backups 2>/dev/null | head -10 || echo 'No backup directories found'", "37. Backup Files")

        # 13. Health Summary
        print("\n" + "="*60)
        print("HEALTH CHECK SUMMARY")
        print("="*60)

        health = {
            "PostgreSQL": self.check_service("postgresql"),
            "Odoo Process": self.check_process("odoo"),
            "Disk Space": self.check_disk_space(),
            "Memory": self.check_memory()
        }

        for component, status in health.items():
            symbol = "✓" if status["ok"] else "✗"
            print(f"{symbol} {component}: {status['message']}")

        return health

    def check_service(self, service):
        """Check if a service is running"""
        result, code = self.execute_command(f"systemctl is-active {service}", None)
        is_active = result.strip() == "active"
        return {
            "ok": is_active,
            "message": "Running" if is_active else "Not Running"
        }

    def check_process(self, process_name):
        """Check if a process is running"""
        result, code = self.execute_command(f"ps aux | grep {process_name} | grep -v grep", None)
        is_running = len(result.strip()) > 0 and code == 0
        return {
            "ok": is_running,
            "message": "Running" if is_running else "Not Running"
        }

    def check_disk_space(self):
        """Check disk space usage"""
        result, code = self.execute_command("df -h / | awk 'NR==2 {print $5}' | sed 's/%//'", None)
        try:
            usage = int(result.strip())
            if usage < 80:
                return {"ok": True, "message": f"{usage}% (Good)"}
            elif usage < 90:
                return {"ok": True, "message": f"{usage}% (Monitor)"}
            else:
                return {"ok": False, "message": f"{usage}% (Critical)"}
        except:
            return {"ok": False, "message": "Unable to determine"}

    def check_memory(self):
        """Check memory usage"""
        result, code = self.execute_command("free | awk 'NR==2 {printf \"%d\", $3*100/$2}'", None)
        try:
            usage = int(result.strip())
            if usage < 80:
                return {"ok": True, "message": f"{usage}% (Good)"}
            elif usage < 90:
                return {"ok": True, "message": f"{usage}% (Monitor)"}
            else:
                return {"ok": False, "message": f"{usage}% (Critical)"}
        except:
            return {"ok": False, "message": "Unable to determine"}

    def save_report(self, filename=None):
        """Save diagnostic report to file"""
        if not filename:
            filename = f"odoo_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, 'w') as f:
            f.write('\n'.join(self.report))

        print(f"\n✓ Report saved to: {filename}")
        return filename

    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("\n✓ Disconnected from server")

def main():
    """Main execution function"""
    diagnostic = OdooDiagnostic(
        host=REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        key_path=SSH_KEY_PATH
    )

    if not diagnostic.connect():
        print("\nFailed to establish connection. Please check:")
        print("  1. Server is reachable")
        print("  2. SSH key is correct")
        print("  3. Network connectivity")
        sys.exit(1)

    try:
        diagnostic.run_diagnostics()
        report_file = diagnostic.save_report()

        print("\n" + "="*60)
        print("DIAGNOSTIC COMPLETE")
        print("="*60)
        print(f"\nFull report: {report_file}")

    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
    except Exception as e:
        print(f"\n✗ Error during diagnostic: {e}")
    finally:
        diagnostic.disconnect()

if __name__ == "__main__":
    main()
