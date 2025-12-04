# SSH Key Setup for Remote Server Access

## 🔑 SSH Key Generated Successfully!

**Key Location**: `C:\Users\branm\.ssh\scholarixv2_key`
**Public Key**: `C:\Users\branm\.ssh\scholarixv2_key.pub`

## 📋 Your Public Key (Add this to your remote server)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDI+GWFNBwvLvBV46yfnD1WSUj50YDodlQl0nwuD2Xs4 scholarixv2-deployment
```

## 🚀 Steps to Add SSH Key to Remote Server

### Method 1: Using ssh-copy-id (Recommended)
```bash
ssh-copy-id -i C:\Users\branm\.ssh\scholarixv2_key.pub root@YOUR_SERVER_IP
```

### Method 2: Manual Setup
1. **Connect to your server**:
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

2. **Add the public key**:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDI+GWFNBwvLvBV46yfnD1WSUj50YDodlQl0nwuD2Xs4 scholarixv2-deployment" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Test the connection** (from your local machine):
   ```powershell
   ssh -i C:\Users\branm\.ssh\scholarixv2_key root@YOUR_SERVER_IP
   ```

## 🔧 Configure SSH Config (Optional but Recommended)

Create/edit: `C:\Users\branm\.ssh\config`

```
Host scholarixv2
    HostName YOUR_SERVER_IP
    User root
    IdentityFile C:\Users\branm\.ssh\scholarixv2_key
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

After setup, you can connect simply with:
```bash
ssh scholarixv2
```

## 🛡️ Security Best Practices

1. **Never share your private key** (`scholarixv2_key`)
2. **Only share the public key** (`scholarixv2_key.pub`)
3. **Set proper permissions**:
   ```powershell
   icacls C:\Users\branm\.ssh\scholarixv2_key /inheritance:r
   icacls C:\Users\branm\.ssh\scholarixv2_key /grant:r "$env:USERNAME:(R)"
   ```

## 🔍 Troubleshooting

### Connection Test
```powershell
ssh -vvv -i C:\Users\branm\.ssh\scholarixv2_key root@YOUR_SERVER_IP
```

### If Permission Denied
- Verify public key was added correctly to `~/.ssh/authorized_keys`
- Check server logs: `sudo tail -f /var/log/auth.log`
- Ensure SSH daemon allows key authentication: `sudo nano /etc/ssh/sshd_config`
  - Set: `PubkeyAuthentication yes`
  - Restart SSH: `sudo systemctl restart sshd`

## 📞 Next Steps

Once SSH key is configured:
1. Test connection: `ssh scholarixv2`
2. Apply Odoo fixes for serialization error
3. Deploy module updates

---

**Generated**: December 2, 2025
**Key Type**: ED25519 (Modern, secure, fast)
