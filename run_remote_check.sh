#!/bin/bash
###############################################################################
# Run CloudPepper Auto-Remediation Remotely
# This script can be run from any machine with network access to the server
###############################################################################

set -e

SERVER="139.84.163.11"
USER="root"
SSH_KEY="/tmp/ssh_key"

echo "============================================================"
echo "CloudPepper Auto-Remediation Remote Execution"
echo "Server: $USER@$SERVER"
echo "============================================================"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found at $SSH_KEY"
    echo ""
    echo "Please create the SSH key file first:"
    echo "  1. Create file: nano $SSH_KEY"
    echo "  2. Paste your private key"
    echo "  3. Set permissions: chmod 600 $SSH_KEY"
    exit 1
fi

# Check SSH key permissions
PERMS=$(stat -c '%a' "$SSH_KEY" 2>/dev/null || stat -f '%A' "$SSH_KEY" 2>/dev/null)
if [ "$PERMS" != "600" ]; then
    echo "⚠️  Fixing SSH key permissions..."
    chmod 600 "$SSH_KEY"
fi

# Test connection
echo "🔌 Testing connection to server..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$SERVER" "echo 'Connected'" 2>/dev/null; then
    echo "✓ Connection successful!"
else
    echo "❌ Cannot connect to server"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check server is online: ping $SERVER"
    echo "  2. Check SSH port: nc -zv $SERVER 22"
    echo "  3. Verify SSH key is correct"
    echo "  4. Check firewall allows SSH from your IP"
    exit 1
fi

echo ""
echo "============================================================"
echo "Select an option:"
echo "============================================================"
echo "1) Run full diagnostic (detection only)"
echo "2) Run compliance checker (detection + health score)"
echo "3) Run auto-remediation (DRY RUN - preview only)"
echo "4) Run auto-remediation (INTERACTIVE - fix with confirmation)"
echo "5) Run auto-remediation (AUTOMATIC - fix all issues)"
echo "6) Just open SSH shell"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "Running full diagnostic..."
        ssh -i "$SSH_KEY" -t "$USER@$SERVER" "bash -s" <<'ENDSSH'
#!/bin/bash
echo "Downloading diagnostic script..."
curl -sSL https://raw.githubusercontent.com/renbran/FINAL-ODOO-APPS/claude/diagnose-remote-database-01QN7eaqKZFCSx622jXobrTo/odoo_db_diagnostic.sh -o /tmp/diagnostic.sh
chmod +x /tmp/diagnostic.sh
echo "Running diagnostic..."
/tmp/diagnostic.sh
ENDSSH
        ;;

    2)
        echo ""
        echo "Running compliance checker..."
        echo "Note: This requires Python 3 and will install paramiko if needed"

        # Copy compliance checker to server
        scp -i "$SSH_KEY" cloudpepper_compliance_checker.py "$USER@$SERVER:/tmp/"

        # Run it
        ssh -i "$SSH_KEY" -t "$USER@$SERVER" "bash -s" <<'ENDSSH'
#!/bin/bash
echo "Installing dependencies..."
pip3 install paramiko >/dev/null 2>&1 || echo "⚠️  Could not install paramiko, trying anyway..."

echo "Running compliance checker..."
cd /tmp
# Modify script to connect to localhost
sed -i 's/REMOTE_HOST = "139.84.163.11"/REMOTE_HOST = "localhost"/' cloudpepper_compliance_checker.py
sed -i 's/SSH_KEY_PATH = "\/tmp\/ssh_key"/SSH_KEY_PATH = ""/' cloudpepper_compliance_checker.py

# Create simpler local version
cat > /tmp/local_compliance_check.py <<'PYTHON'
import subprocess
import sys

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

print("="*70)
print("🔍 CLOUDPEPPER COMPLIANCE CHECK")
print("="*70 + "\n")

# Check PostgreSQL
print("🐘 PostgreSQL Status:")
output, code = run_cmd("systemctl is-active postgresql")
if code == 0:
    print("  ✓ PostgreSQL is running")
else:
    print("  ✗ PostgreSQL is NOT running")

# Check Odoo
print("\n🟣 Odoo Status:")
output, code = run_cmd("ps aux | grep odoo-bin | grep -v grep")
if output:
    print("  ✓ Odoo is running")
else:
    print("  ✗ Odoo is NOT running")

# Check users
print("\n👥 Users:")
output, code = run_cmd("id odoo 2>/dev/null")
if code == 0:
    print("  ✓ Odoo user exists")
else:
    print("  ✗ Odoo user missing")

# Check directories
print("\n📁 Directories:")
for dir in ["/opt/odoo", "/var/log/odoo", "/opt/odoo/.local/share/Odoo"]:
    output, code = run_cmd(f"test -d {dir} && echo 'exists'")
    if "exists" in output:
        owner_output, _ = run_cmd(f"stat -c '%U:%G' {dir}")
        print(f"  ✓ {dir} ({owner_output})")
    else:
        print(f"  ✗ {dir} missing")

# Check disk space
print("\n💽 Disk Space:")
output, _ = run_cmd("df -h / | awk 'NR==2 {print $5, $4}'")
print(f"  {output}")

# Check memory
print("\n💾 Memory:")
output, _ = run_cmd("free -h | awk 'NR==2 {print $3\"/\"$2}'")
print(f"  Used: {output}")

print("\n" + "="*70)
PYTHON

python3 /tmp/local_compliance_check.py
ENDSSH
        ;;

    3)
        echo ""
        echo "Running auto-remediation (DRY RUN)..."
        python3 auto_remediation.py --dry-run
        ;;

    4)
        echo ""
        echo "Running auto-remediation (INTERACTIVE)..."
        python3 auto_remediation.py
        ;;

    5)
        echo ""
        echo "⚠️  WARNING: This will automatically fix all issues without confirmation!"
        read -p "Are you sure? [y/N]: " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo "Running auto-remediation (AUTOMATIC)..."
            python3 auto_remediation.py --auto
        else
            echo "Cancelled."
        fi
        ;;

    6)
        echo ""
        echo "Opening SSH shell to $SERVER..."
        ssh -i "$SSH_KEY" "$USER@$SERVER"
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "✓ Done"
echo "============================================================"
