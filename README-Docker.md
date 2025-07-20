# Odoo 17 Docker Setup

This repository contains a complete Odoo 17 setup with custom modules using Docker and Docker Compose.

## Prerequisites

### 1. Install Docker Desktop

Before running Odoo, you need Docker Desktop installed on Windows:

**Option A: Download from Docker**
1. Go to https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Run the installer as Administrator
4. Restart your computer after installation
5. Start Docker Desktop from the Start menu

**Option B: Using Chocolatey (as Administrator)**
```powershell
choco install docker-desktop -y
```

**Option C: Using Windows Package Manager**
```powershell
winget install Docker.DockerDesktop
```

### 2. Verify Docker Installation

After installation and restart:
```powershell
docker --version
docker-compose --version
```

## Quick Start

### 1. Clone and Navigate
```powershell
cd d:\odoo17_final
```

### 2. Start Odoo (Easy Way)
Double-click `start-odoo.bat` or run:
```powershell
.\start-odoo.bat
```

### 3. Manual Start
```powershell
# Build the images
docker-compose build

# Start the services
docker-compose up -d

# Check status
docker-compose ps
```

## Accessing Odoo

Once started, you can access:
- **Odoo Web Interface**: http://localhost:8069
- **PostgreSQL Database**: localhost:5432

### Database Setup
1. Go to http://localhost:8069
2. Click "Create Database"
3. Enter database details:
   - **Database Name**: Choose your preferred name (e.g., `odoo_prod`)
   - **Master Password**: `VillaRicca` (as configured)
   - **Load demonstration data**: Uncheck for production

## Available Scripts

### Main Scripts
- `start-odoo.bat` - Start Odoo with Docker
- `setup.bat` - Full setup menu with multiple options
- `troubleshoot.bat` - Troubleshooting and maintenance tools

### Manual Commands

**View logs:**
```powershell
# All logs
docker-compose logs -f

# Odoo logs only
docker-compose logs -f odoo

# Database logs only
docker-compose logs -f db
```

**Stop services:**
```powershell
docker-compose down
```

**Restart services:**
```powershell
docker-compose restart
```

**Clean rebuild:**
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Custom Modules

The following custom modules are included:
- `automated_employee_announce/`
- `calendar_extended/`
- `hrms_dashboard/`
- `osus_dashboard/`
- `osus_invoice_report/`
- `payment_account_enhanced/`
- And many more...

All modules are automatically loaded from the current directory.

## Configuration

### Docker Compose Services
- **db**: PostgreSQL 15 database
- **odoo**: Odoo 17 application server

### Environment Variables
- `POSTGRES_USER=odoo`
- `POSTGRES_PASSWORD=odoo`
- `POSTGRES_DB=postgres`

### Volumes
- `odoo-web-data`: Odoo application data
- `odoo-db-data`: PostgreSQL database data
- `./config:/etc/odoo`: Configuration files
- `./logs:/var/log/odoo`: Log files

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```powershell
# Check what's using the ports
netstat -an | findstr :8069
netstat -an | findstr :5432

# Stop any conflicting services
```

**2. Docker Not Starting**
- Ensure Docker Desktop is running (check system tray for whale icon)
- Try restarting Docker Desktop
- Check Windows virtualization is enabled

**3. Database Connection Issues**
```powershell
# Check database container
docker-compose logs db

# Restart database
docker-compose restart db
```

**4. Module Loading Issues**
```powershell
# Check Odoo logs
docker-compose logs odoo

# Update module list (in Odoo interface):
# Settings > Apps > Update Apps List
```

### Using Troubleshoot Script
Run `troubleshoot.bat` for guided troubleshooting options.

## Development

### Adding New Modules
1. Place your module folder in the root directory
2. Restart Odoo: `docker-compose restart odoo`
3. Update Apps List in Odoo interface
4. Install/upgrade your module

### Accessing Container Shell
```powershell
# Odoo container
docker-compose exec odoo bash

# Database container
docker-compose exec db psql -U odoo -d postgres
```

### Backup & Restore

**Backup Database:**
```powershell
docker-compose exec db pg_dump -U odoo -d your_db_name > backup.sql
```

**Restore Database:**
```powershell
docker-compose exec -T db psql -U odoo -d your_db_name < backup.sql
```

## Security Notes

- Default admin password is set in `config/odoo.conf`
- Change default passwords in production
- Configure proper firewall rules for production deployment

## Support

For issues:
1. Check the troubleshooting section above
2. Run `troubleshoot.bat` for guided diagnostics
3. Check Docker and Odoo logs for error messages
