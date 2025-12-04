#!/bin/bash
# Direct module update via Odoo running instance
# This connects to the running Odoo service and triggers module update

TIMESTAMP=$(date +%s)
LOG="/var/log/odoo/module_update_${TIMESTAMP}.log"

echo "=========================================="
echo "🔄 RENTAL_MANAGEMENT MODULE UPDATE"
echo "=========================================="
echo "Starting: $(date)" | tee "$LOG"

# Check if Odoo is running on expected ports
echo "Checking Odoo service..." | tee -a "$LOG"
if netstat -tulpn 2>/dev/null | grep -q ':3004.*LISTEN'; then
    echo "✅ Odoo service is running on port 3004" | tee -a "$LOG"
    PORT=3004
elif netstat -tulpn 2>/dev/null | grep -q ':8069.*LISTEN'; then
    echo "✅ Odoo service is running on port 8069" | tee -a "$LOG"
    PORT=8069
else
    echo "❌ Odoo service not found on standard ports" | tee -a "$LOG"
    PORT=3004  # Try default anyway
fi

# Use Odoo shell via environment to trigger update
echo "Attempting module update via Odoo shell..." | tee -a "$LOG"

# Method 1: Try direct update via odoo-bin
echo "Method 1: Direct update via odoo-bin..." | tee -a "$LOG"
cd /var/odoo/scholarixv2

# First kill existing processes gracefully
echo "Stopping Odoo processes gracefully..." | tee -a "$LOG"
pkill -TERM -f "odoo-bin.*odoo.conf" 2>/dev/null || true
sleep 5

# Remove any locks
rm -f /var/odoo/scholarixv2/pid.lock 2>/dev/null || true

# Now run the update
echo "Running: /var/odoo/scholarixv2/venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u rental_management --stop-after-init" | tee -a "$LOG"
timeout 600 /var/odoo/scholarixv2/venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u rental_management --stop-after-init >> "$LOG" 2>&1

UPDATE_EXIT=$?

if [ $UPDATE_EXIT -eq 0 ]; then
    echo "✅ Module update completed successfully" | tee -a "$LOG"
elif [ $UPDATE_EXIT -eq 124 ]; then
    echo "⚠️  Update timed out (may still have worked), checking status..." | tee -a "$LOG"
else
    echo "❌ Update returned error code: $UPDATE_EXIT" | tee -a "$LOG"
    tail -50 "$LOG" | tee -a "$LOG"
fi

# Start Odoo again
echo "Starting Odoo service..." | tee -a "$LOG"
systemctl start odoo 2>/dev/null || /var/odoo/scholarixv2/venv/bin/python3 src/odoo-bin -c odoo.conf &
sleep 3

# Verify module state
echo "Verifying module state..." | tee -a "$LOG"
psql scholarixv2 -c "SELECT name, state FROM ir_module_module WHERE name = 'rental_management';" | tee -a "$LOG"

echo ""
echo "=========================================="
echo "✅ COMPLETE"
echo "=========================================="
echo "Log: $LOG"
echo "=========================================="

# Show last lines
tail -20 "$LOG"
