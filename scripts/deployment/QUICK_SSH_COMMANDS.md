# Quick SSH Connection Commands

## Step 1: Add SSH Key to Server (One-Time Setup)

Copy this public key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDI+GWFNBwvLvBV46yfnD1WSUj50YDodlQl0nwuD2Xs4 scholarixv2-deployment
```

Connect with password and add key:
```bash
ssh root@139.84.163.11
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDI+GWFNBwvLvBV46yfnD1WSUj50YDodlQl0nwuD2Xs4 scholarixv2-deployment" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

## Step 2: Test Key-Based Connection

```powershell
ssh -i C:\Users\branm\.ssh\scholarixv2_key root@139.84.163.11
```

## Step 3: Execute Fix Commands

Once connected, run these commands one by one:

```bash
# Stop Odoo
ps aux | grep odoo
sudo pkill -f odoo-bin
sudo pkill -f "python.*odoo"

# Clear DB connections
sudo -u postgres psql -d scholarixv2 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'scholarixv2' AND pid <> pg_backend_pid();"

# Backup config
sudo cp /var/odoo/scholarixv2/odoo.conf /var/odoo/scholarixv2/odoo.conf.backup

# Edit config
sudo nano /var/odoo/scholarixv2/odoo.conf
# Add these lines:
# workers = 0
# max_cron_threads = 0

# Start Odoo
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=info > logs/odoo.log 2>&1 &

# Monitor
tail -f /var/odoo/scholarixv2/logs/odoo.log
```
