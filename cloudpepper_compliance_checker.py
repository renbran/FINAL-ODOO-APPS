#!/usr/bin/env python3
"""
CloudPepper Compliance & Issue Detector for Odoo 17
Identifies setup issues, database problems, and problematic custom apps
"""

import sys
import json
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

class CloudPepperCompliance:
    def __init__(self, host, port, username, key_path):
        self.host = host
        self.port = port
        self.username = username
        self.key_path = key_path
        self.client = None
        self.issues = []
        self.warnings = []
        self.successes = []
        self.recommendations = []

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
            stdin, stdout, stderr = self.client.exec_command(command, timeout=60)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()

            if not silent and exit_code != 0 and error:
                print(f"  ⚠ Command warning: {error[:200]}")

            return output.strip(), exit_code
        except Exception as e:
            if not silent:
                print(f"  ✗ Command error: {e}")
            return "", -1

    def add_issue(self, category, description, severity="HIGH"):
        """Add an issue to the list"""
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity
        })

    def add_warning(self, category, description):
        """Add a warning to the list"""
        self.warnings.append({
            "category": category,
            "description": description
        })

    def add_success(self, category, description):
        """Add a success to the list"""
        self.successes.append({
            "category": category,
            "description": description
        })

    def add_recommendation(self, description):
        """Add a recommendation"""
        self.recommendations.append(description)

    def check_cloudpepper_users(self):
        """Check for required system users"""
        print("👥 Checking CloudPepper Users...")

        # Check odoo user
        output, code = self.execute_command("id odoo 2>/dev/null", silent=True)
        if code == 0:
            self.add_success("Users", "Odoo user exists")
            print("  ✓ Odoo user exists")

            # Check odoo user shell
            shell_output, _ = self.execute_command("getent passwd odoo | cut -d: -f7")
            if "/bin/false" in shell_output or "/usr/sbin/nologin" in shell_output:
                self.add_success("Security", "Odoo user has no login shell (secure)")
            else:
                self.add_warning("Security", f"Odoo user has login shell: {shell_output}")
        else:
            self.add_issue("Users", "Odoo user does not exist", "CRITICAL")
            print("  ✗ Odoo user does not exist")
            self.add_recommendation("Create odoo user: sudo adduser --system --home=/opt/odoo --group odoo")

        # Check postgres user
        output, code = self.execute_command("id postgres 2>/dev/null", silent=True)
        if code == 0:
            self.add_success("Users", "PostgreSQL user exists")
            print("  ✓ PostgreSQL user exists")
        else:
            self.add_issue("Users", "PostgreSQL user does not exist", "CRITICAL")
            print("  ✗ PostgreSQL user does not exist")

    def check_cloudpepper_directories(self):
        """Check for required directories and permissions"""
        print("\n📁 Checking CloudPepper Directory Structure...")

        required_dirs = {
            "/opt/odoo": "Odoo installation directory",
            "/var/log/odoo": "Odoo log directory",
            "/opt/odoo/.local/share/Odoo": "Odoo data directory",
        }

        for directory, description in required_dirs.items():
            output, code = self.execute_command(f"test -d {directory} && echo 'exists' || echo 'missing'", silent=True)

            if "exists" in output:
                # Check ownership
                owner_output, _ = self.execute_command(f"stat -c '%U:%G' {directory}")

                if "odoo" in owner_output:
                    self.add_success("Directories", f"{directory} exists with correct ownership ({owner_output})")
                    print(f"  ✓ {directory} - {owner_output}")
                else:
                    self.add_warning("Directories", f"{directory} exists but ownership is {owner_output}, should be odoo:odoo")
                    print(f"  ⚠ {directory} - Wrong owner: {owner_output}")
                    self.add_recommendation(f"Fix ownership: sudo chown -R odoo:odoo {directory}")

                # Check permissions
                perms, _ = self.execute_command(f"stat -c '%a' {directory}")
                if directory == "/var/log/odoo":
                    if perms.strip() in ["755", "750", "775"]:
                        self.add_success("Permissions", f"{directory} has correct permissions ({perms.strip()})")
                    else:
                        self.add_warning("Permissions", f"{directory} has unusual permissions: {perms.strip()}")
            else:
                self.add_issue("Directories", f"{directory} ({description}) does not exist", "HIGH")
                print(f"  ✗ {directory} missing")
                self.add_recommendation(f"Create directory: sudo mkdir -p {directory} && sudo chown odoo:odoo {directory}")

    def check_odoo_configuration(self):
        """Check Odoo configuration file"""
        print("\n⚙️  Checking Odoo Configuration...")

        # Find config file
        config_paths = ["/etc/odoo.conf", "/etc/odoo-server.conf", "/opt/odoo/.odoorc"]
        config_file = None

        for path in config_paths:
            output, code = self.execute_command(f"test -f {path} && echo '{path}'", silent=True)
            if output:
                config_file = output.strip()
                break

        if not config_file:
            self.add_issue("Configuration", "Odoo configuration file not found in standard locations", "CRITICAL")
            print("  ✗ Odoo configuration file not found")
            self.add_recommendation("Create Odoo config: /etc/odoo.conf or /etc/odoo-server.conf")
            return

        print(f"  ✓ Found config: {config_file}")
        self.add_success("Configuration", f"Odoo config file exists: {config_file}")

        # Read and analyze config
        config_content, _ = self.execute_command(f"cat {config_file}")

        # Check critical settings
        critical_settings = {
            "db_host": "Database host",
            "db_port": "Database port",
            "db_user": "Database user",
            "db_password": "Database password",
            "addons_path": "Addons path",
            "data_dir": "Data directory",
            "logfile": "Log file path"
        }

        for setting, description in critical_settings.items():
            if setting in config_content:
                # Extract value
                for line in config_content.split('\n'):
                    if line.strip().startswith(setting):
                        value = line.split('=', 1)[1].strip() if '=' in line else ''
                        if value and value != "False":
                            self.add_success("Configuration", f"{description} is configured")
                            print(f"  ✓ {setting} = {value[:50]}")
                        else:
                            self.add_warning("Configuration", f"{description} is set but empty")
                        break
            else:
                if setting in ["db_host", "db_port", "db_user"]:
                    self.add_warning("Configuration", f"{description} ({setting}) not configured")
                    print(f"  ⚠ {setting} not configured")

        # Check workers configuration
        if "workers" in config_content:
            for line in config_content.split('\n'):
                if line.strip().startswith("workers"):
                    workers = line.split('=')[1].strip() if '=' in line else '0'
                    workers_num = int(workers) if workers.isdigit() else 0

                    if workers_num >= 2:
                        self.add_success("Performance", f"Workers configured: {workers}")
                        print(f"  ✓ Workers = {workers}")
                    else:
                        self.add_warning("Performance", f"Workers set to {workers} (production should be >= 2)")
                        print(f"  ⚠ Workers = {workers} (low for production)")
                        self.add_recommendation("Increase workers for production: workers = (CPU cores * 2) + 1")
                    break
        else:
            self.add_warning("Performance", "Workers not configured (running in single-process mode)")
            self.add_recommendation("Add workers configuration for production")

    def check_postgresql_setup(self):
        """Check PostgreSQL setup and configuration"""
        print("\n🐘 Checking PostgreSQL Setup...")

        # Check service
        output, code = self.execute_command("systemctl is-active postgresql", silent=True)
        if code == 0 and "active" in output:
            self.add_success("PostgreSQL", "PostgreSQL service is running")
            print("  ✓ PostgreSQL service is running")
        else:
            self.add_issue("PostgreSQL", "PostgreSQL service is not running", "CRITICAL")
            print("  ✗ PostgreSQL service is NOT running")
            self.add_recommendation("Start PostgreSQL: sudo systemctl start postgresql")
            return

        # Check version
        version_output, _ = self.execute_command("sudo -u postgres psql -t -c 'SHOW server_version;'")
        if version_output:
            version = version_output.strip().split()[0]
            print(f"  ✓ PostgreSQL version: {version}")

            version_major = int(version.split('.')[0]) if version.split('.')[0].isdigit() else 0
            if version_major >= 12:
                self.add_success("PostgreSQL", f"PostgreSQL version {version} is supported")
            else:
                self.add_warning("PostgreSQL", f"PostgreSQL version {version} is old, consider upgrading")

        # Check if odoo can connect
        test_connection, code = self.execute_command("sudo -u postgres psql -c '\\l' 2>&1", silent=True)
        if code == 0:
            self.add_success("PostgreSQL", "Can connect to PostgreSQL")
            print("  ✓ PostgreSQL is accessible")
        else:
            self.add_issue("PostgreSQL", "Cannot connect to PostgreSQL", "HIGH")
            print("  ✗ Cannot connect to PostgreSQL")

        # Check configuration
        max_conn, _ = self.execute_command("sudo -u postgres psql -t -c 'SHOW max_connections;'")
        if max_conn:
            max_conn_num = int(max_conn.strip())
            if max_conn_num >= 100:
                self.add_success("PostgreSQL", f"max_connections = {max_conn_num}")
                print(f"  ✓ max_connections = {max_conn_num}")
            else:
                self.add_warning("PostgreSQL", f"max_connections = {max_conn_num} (low for production)")
                print(f"  ⚠ max_connections = {max_conn_num}")
                self.add_recommendation("Increase max_connections to at least 100")

        # Check shared_buffers
        shared_buf, _ = self.execute_command("sudo -u postgres psql -t -c 'SHOW shared_buffers;'")
        if shared_buf:
            print(f"  ✓ shared_buffers = {shared_buf.strip()}")
            # Parse memory size
            if "MB" in shared_buf and int(shared_buf.split('MB')[0].strip()) < 256:
                self.add_warning("PostgreSQL", f"shared_buffers is {shared_buf.strip()} (recommended: at least 25% of RAM)")
                self.add_recommendation("Increase shared_buffers to 25% of total RAM")

    def check_databases(self):
        """Check all databases for issues"""
        print("\n💾 Checking Databases for Issues...")

        # Get list of databases
        db_list, code = self.execute_command(
            "sudo -u postgres psql -t -c \"SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';\"",
            silent=True
        )

        if code != 0:
            self.add_issue("Databases", "Cannot retrieve database list", "HIGH")
            return

        databases = [db.strip() for db in db_list.split('\n') if db.strip()]
        print(f"  Found {len(databases)} database(s): {', '.join(databases)}")

        for db in databases:
            print(f"\n  📊 Analyzing database: {db}")

            # Check database size
            size_output, _ = self.execute_command(
                f"sudo -u postgres psql -t -c \"SELECT pg_size_pretty(pg_database_size('{db}'));\"",
                silent=True
            )
            if size_output:
                size = size_output.strip()
                print(f"    Size: {size}")

                # Warn if database is very large
                if "GB" in size:
                    size_gb = float(size.split('GB')[0].strip())
                    if size_gb > 50:
                        self.add_warning("Databases", f"Database '{db}' is very large ({size}) - consider archiving old data")

            # Check active connections
            conn_output, _ = self.execute_command(
                f"sudo -u postgres psql -t -c \"SELECT count(*) FROM pg_stat_activity WHERE datname = '{db}';\"",
                silent=True
            )
            if conn_output:
                connections = int(conn_output.strip())
                print(f"    Active connections: {connections}")

                if connections > 50:
                    self.add_warning("Databases", f"Database '{db}' has {connections} active connections (high)")
                elif connections == 0:
                    self.add_warning("Databases", f"Database '{db}' has no active connections (possibly unused)")

            # Check for bloated tables
            bloat_query = f"""
            SELECT schemaname, tablename,
                   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 5;
            """

            bloat_output, code = self.execute_command(
                f"sudo -u postgres psql -d {db} -t -c \"{bloat_query}\"",
                silent=True
            )

            if code == 0 and bloat_output:
                print(f"    Top 5 largest tables:")
                for line in bloat_output.strip().split('\n')[:5]:
                    if line.strip():
                        print(f"      {line.strip()}")

            # Check for long-running queries
            long_query = f"""
            SELECT pid, now() - query_start as duration, state, substring(query, 1, 50) as query
            FROM pg_stat_activity
            WHERE datname = '{db}'
              AND state != 'idle'
              AND (now() - query_start) > interval '5 minutes'
            ORDER BY duration DESC;
            """

            long_output, code = self.execute_command(
                f"sudo -u postgres psql -t -c \"{long_query}\"",
                silent=True
            )

            if code == 0 and long_output.strip():
                self.add_warning("Performance", f"Database '{db}' has long-running queries (>5 min)")
                print(f"    ⚠ Long-running queries detected!")
                self.add_recommendation(f"Investigate long-running queries in database '{db}'")

            # Check database encoding
            encoding_output, _ = self.execute_command(
                f"sudo -u postgres psql -t -c \"SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = '{db}';\"",
                silent=True
            )
            if encoding_output:
                encoding = encoding_output.strip()
                if encoding == "UTF8":
                    print(f"    ✓ Encoding: {encoding}")
                else:
                    self.add_warning("Databases", f"Database '{db}' encoding is {encoding}, should be UTF8")
                    print(f"    ⚠ Encoding: {encoding} (should be UTF8)")

    def check_custom_modules(self):
        """Check for custom Odoo modules and potential issues"""
        print("\n🔌 Checking Custom Odoo Modules...")

        # Find addons paths from config
        config_paths = ["/etc/odoo.conf", "/etc/odoo-server.conf", "/opt/odoo/.odoorc"]
        addons_paths = []

        for config_path in config_paths:
            config_content, code = self.execute_command(f"cat {config_path} 2>/dev/null", silent=True)
            if code == 0:
                for line in config_content.split('\n'):
                    if line.strip().startswith('addons_path'):
                        paths = line.split('=')[1].strip() if '=' in line else ''
                        addons_paths = [p.strip() for p in paths.split(',') if p.strip()]
                        break
                if addons_paths:
                    break

        if not addons_paths:
            self.add_warning("Modules", "Cannot find addons_path in configuration")
            print("  ⚠ Cannot find addons_path")
            return

        print(f"  Addons paths: {len(addons_paths)}")

        custom_modules = []

        for addon_path in addons_paths:
            # Skip standard Odoo addons
            if "odoo/addons" in addon_path or "odoo-server/addons" in addon_path:
                continue

            # List modules in this path
            modules_output, code = self.execute_command(
                f"find {addon_path} -maxdepth 2 -name '__manifest__.py' -o -name '__openerp__.py' 2>/dev/null | xargs -I {{}} dirname {{}}",
                silent=True
            )

            if code == 0 and modules_output:
                modules = [m.strip() for m in modules_output.split('\n') if m.strip()]
                custom_modules.extend(modules)

        print(f"  Found {len(custom_modules)} custom module(s)")

        if custom_modules:
            print(f"\n  Custom modules:")
            for module_path in custom_modules[:20]:  # Limit to first 20
                module_name = module_path.split('/')[-1]
                print(f"    - {module_name}")

                # Check for common issues
                # 1. Check if module has __init__.py
                init_check, code = self.execute_command(f"test -f {module_path}/__init__.py && echo 'yes' || echo 'no'", silent=True)
                if "no" in init_check:
                    self.add_warning("Modules", f"Custom module '{module_name}' missing __init__.py")
                    self.add_recommendation(f"Add __init__.py to module: {module_path}")

                # 2. Check manifest
                manifest_check, code = self.execute_command(
                    f"test -f {module_path}/__manifest__.py && cat {module_path}/__manifest__.py || test -f {module_path}/__openerp__.py && cat {module_path}/__openerp__.py",
                    silent=True
                )

                if code == 0 and manifest_check:
                    # Check for version compatibility
                    if "'version'" not in manifest_check and '"version"' not in manifest_check:
                        self.add_warning("Modules", f"Module '{module_name}' missing version in manifest")

                    # Check for installable flag
                    if "'installable': False" in manifest_check or '"installable": false' in manifest_check.lower():
                        self.add_warning("Modules", f"Module '{module_name}' is marked as not installable")
                        print(f"      ⚠ Not installable")

                # 3. Check for Python syntax errors
                py_check, code = self.execute_command(
                    f"python3 -m py_compile {module_path}/*.py 2>&1",
                    silent=True
                )

                if code != 0 and py_check:
                    self.add_issue("Modules", f"Module '{module_name}' has Python syntax errors", "HIGH")
                    print(f"      ✗ Syntax errors detected")
                    self.add_recommendation(f"Fix Python syntax errors in module: {module_name}")

        # Check Odoo logs for module errors
        log_paths = ["/var/log/odoo/odoo-server.log", "/var/log/odoo.log", "/var/log/odoo/odoo.log"]

        for log_path in log_paths:
            log_check, code = self.execute_command(f"test -f {log_path} && echo 'exists'", silent=True)
            if "exists" in log_check:
                # Check for recent errors
                error_check, _ = self.execute_command(
                    f"tail -1000 {log_path} | grep -i 'error\\|exception\\|failed' | tail -20",
                    silent=True
                )

                if error_check:
                    print(f"\n  ⚠ Recent errors found in {log_path}:")
                    for line in error_check.split('\n')[:5]:
                        if line.strip():
                            print(f"    {line.strip()[:100]}")

                    self.add_warning("Modules", "Recent errors found in Odoo logs")
                    self.add_recommendation(f"Review Odoo logs: {log_path}")
                break

    def check_system_resources(self):
        """Check system resources and performance"""
        print("\n💻 Checking System Resources...")

        # Check disk space
        disk_output, _ = self.execute_command("df -h / | awk 'NR==2 {print $5,$4}'")
        if disk_output:
            parts = disk_output.split()
            usage_pct = int(parts[0].replace('%', ''))
            available = parts[1] if len(parts) > 1 else "unknown"

            print(f"  Disk usage: {usage_pct}% (Available: {available})")

            if usage_pct >= 90:
                self.add_issue("Resources", f"Disk usage critical: {usage_pct}%", "CRITICAL")
                self.add_recommendation("Free up disk space immediately - clean logs, old backups")
            elif usage_pct >= 80:
                self.add_warning("Resources", f"Disk usage high: {usage_pct}%")
                self.add_recommendation("Monitor disk space - consider cleanup or expansion")
            else:
                self.add_success("Resources", f"Disk usage healthy: {usage_pct}%")

        # Check memory
        mem_output, _ = self.execute_command("free -m | awk 'NR==2 {printf \"%.0f %.0f\\n\", $3*100/$2, $2}'")
        if mem_output:
            parts = mem_output.split()
            mem_usage_pct = int(float(parts[0]))
            total_mem = int(float(parts[1])) if len(parts) > 1 else 0

            print(f"  Memory usage: {mem_usage_pct}% (Total: {total_mem}MB)")

            if mem_usage_pct >= 90:
                self.add_warning("Resources", f"Memory usage high: {mem_usage_pct}%")
                self.add_recommendation("Consider adding more RAM or reducing Odoo workers")
            else:
                self.add_success("Resources", f"Memory usage acceptable: {mem_usage_pct}%")

        # Check load average
        load_output, _ = self.execute_command("cat /proc/loadavg | awk '{print $1,$2,$3}'")
        if load_output:
            load_parts = load_output.split()
            load_1min = float(load_parts[0])

            # Get CPU count
            cpu_output, _ = self.execute_command("nproc")
            cpu_count = int(cpu_output.strip()) if cpu_output else 1

            print(f"  Load average: {load_output} (CPUs: {cpu_count})")

            if load_1min > cpu_count * 2:
                self.add_warning("Resources", f"High load average: {load_1min} on {cpu_count} CPUs")
                self.add_recommendation("Investigate high system load - check for runaway processes")
            else:
                self.add_success("Resources", f"Load average normal: {load_1min}")

    def check_security(self):
        """Check security configurations"""
        print("\n🔒 Checking Security Configuration...")

        # Check firewall
        ufw_status, code = self.execute_command("ufw status 2>/dev/null", silent=True)
        if code == 0:
            if "Status: active" in ufw_status:
                self.add_success("Security", "UFW firewall is active")
                print("  ✓ UFW firewall is active")

                # Check if PostgreSQL port is blocked externally
                if "5432" in ufw_status:
                    self.add_warning("Security", "PostgreSQL port 5432 may be exposed in firewall")
                    self.add_recommendation("Ensure PostgreSQL port 5432 is only accessible locally")
            else:
                self.add_warning("Security", "UFW firewall is inactive")
                print("  ⚠ UFW firewall is inactive")
                self.add_recommendation("Enable UFW firewall: sudo ufw enable")

        # Check SSH configuration
        ssh_root, _ = self.execute_command("grep '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null")
        if "PermitRootLogin yes" in ssh_root:
            self.add_warning("Security", "SSH root login is permitted")
            self.add_recommendation("Disable root SSH login: PermitRootLogin no")
        elif ssh_root:
            self.add_success("Security", "SSH root login is restricted")
            print("  ✓ SSH root login restricted")

        # Check if PostgreSQL is listening externally
        pg_listen, _ = self.execute_command("ss -tlnp | grep 5432")
        if pg_listen:
            if "127.0.0.1:5432" in pg_listen or "localhost:5432" in pg_listen:
                self.add_success("Security", "PostgreSQL only listening on localhost")
                print("  ✓ PostgreSQL listening only on localhost")
            else:
                self.add_warning("Security", "PostgreSQL may be listening on external interface")
                print("  ⚠ PostgreSQL listening externally")
                self.add_recommendation("Configure PostgreSQL to listen only on localhost for security")

    def check_backups(self):
        """Check backup configuration"""
        print("\n💾 Checking Backup Configuration...")

        # Check for backup directories
        backup_dirs = ["/backup", "/backups", "/var/backups/odoo", "/opt/odoo/backups"]
        found_backup_dir = False

        for backup_dir in backup_dirs:
            output, code = self.execute_command(f"test -d {backup_dir} && echo 'exists' || echo 'missing'", silent=True)
            if "exists" in output:
                found_backup_dir = True
                print(f"  ✓ Backup directory found: {backup_dir}")

                # Check for recent backups
                recent_backups, _ = self.execute_command(
                    f"find {backup_dir} -type f -name '*.zip' -o -name '*.sql' -o -name '*.dump' -mtime -7 2>/dev/null | wc -l"
                )

                if recent_backups:
                    count = int(recent_backups.strip())
                    if count > 0:
                        self.add_success("Backups", f"Found {count} recent backup(s) in {backup_dir}")
                        print(f"    {count} recent backup(s) found")
                    else:
                        self.add_warning("Backups", f"No recent backups in {backup_dir}")
                        print(f"    ⚠ No recent backups")

        if not found_backup_dir:
            self.add_warning("Backups", "No backup directory found")
            print("  ⚠ No backup directory found")
            self.add_recommendation("Create backup directory and set up automated backups")

        # Check cron jobs
        cron_output, _ = self.execute_command("crontab -l 2>/dev/null | grep -i backup", silent=True)
        if cron_output:
            self.add_success("Backups", "Backup cron job configured")
            print("  ✓ Backup cron job found")
        else:
            self.add_warning("Backups", "No backup cron job found")
            print("  ⚠ No backup cron job")
            self.add_recommendation("Set up automated backup cron job")

    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*70)
        print("📊 CLOUDPEPPER COMPLIANCE & ISSUE REPORT")
        print("="*70)

        print(f"\n✅ SUCCESSES ({len(self.successes)}):")
        for success in self.successes[:10]:  # Show first 10
            print(f"  ✓ [{success['category']}] {success['description']}")
        if len(self.successes) > 10:
            print(f"  ... and {len(self.successes) - 10} more")

        print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
        if self.warnings:
            for warning in self.warnings:
                print(f"  ⚠ [{warning['category']}] {warning['description']}")
        else:
            print("  None")

        print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
        if self.issues:
            for issue in self.issues:
                severity = issue['severity']
                print(f"  ✗ [{severity}] [{issue['category']}] {issue['description']}")
        else:
            print("  None - All checks passed!")

        print(f"\n💡 RECOMMENDATIONS ({len(self.recommendations)}):")
        if self.recommendations:
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  No recommendations - system is properly configured!")

        # Overall health score
        total_checks = len(self.successes) + len(self.warnings) + len(self.issues)
        if total_checks > 0:
            health_score = (len(self.successes) / total_checks) * 100
            print(f"\n📈 OVERALL HEALTH SCORE: {health_score:.1f}%")

            if health_score >= 90:
                print("   Status: ✅ EXCELLENT")
            elif health_score >= 75:
                print("   Status: ✅ GOOD")
            elif health_score >= 60:
                print("   Status: ⚠️  FAIR - Improvements needed")
            else:
                print("   Status: ❌ POOR - Immediate attention required")

        print("\n" + "="*70)

    def save_report(self, filename=None):
        """Save report to JSON file"""
        if not filename:
            filename = f"cloudpepper_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "server": self.host,
            "successes": self.successes,
            "warnings": self.warnings,
            "issues": self.issues,
            "recommendations": self.recommendations
        }

        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n✓ Detailed report saved to: {filename}")
        return filename

    def run_full_compliance_check(self):
        """Run all compliance checks"""
        print("="*70)
        print("🔍 CLOUDPEPPER COMPLIANCE & ISSUE DETECTION")
        print(f"Server: {self.host}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        self.check_cloudpepper_users()
        self.check_cloudpepper_directories()
        self.check_odoo_configuration()
        self.check_postgresql_setup()
        self.check_databases()
        self.check_custom_modules()
        self.check_system_resources()
        self.check_security()
        self.check_backups()

        self.generate_report()

    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("\n✓ Disconnected from server")

def main():
    """Main execution"""
    checker = CloudPepperCompliance(
        host=REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        key_path=SSH_KEY_PATH
    )

    if not checker.connect():
        print("\n❌ Failed to establish connection")
        print("\nPlease verify:")
        print("  1. Server is reachable: nc -zv", REMOTE_HOST, REMOTE_PORT)
        print("  2. SSH key exists:", SSH_KEY_PATH)
        print("  3. Key permissions: chmod 600", SSH_KEY_PATH)
        sys.exit(1)

    try:
        checker.run_full_compliance_check()
        checker.save_report()

        print("\n" + "="*70)
        print("✅ COMPLIANCE CHECK COMPLETE")
        print("="*70)

        # Exit code based on issues
        if len(checker.issues) > 0:
            sys.exit(2)  # Has critical issues
        elif len(checker.warnings) > 0:
            sys.exit(1)  # Has warnings
        else:
            sys.exit(0)  # All good

    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during compliance check: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        checker.disconnect()

if __name__ == "__main__":
    main()
