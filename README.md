# 🚀 OSUS Odoo 17 Final - Docker Setup

This repository contains a complete Odoo 17 setup with custom modules designed for comprehensive business management.

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Custom Modules](#custom-modules)
- [Docker Commands](#docker-commands)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git installed
- 8GB+ RAM recommended
- 20GB+ free disk space

### 1. Clone the Repository
```bash
git clone https://github.com/renbran/odoo17_final.git
cd odoo17_final
```

### 2. Start the Environment
**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Access Odoo
- Open browser: http://localhost:8069
- Database: `odoo`
- Username: `admin`
- Password: `admin`

## 🏗️ Repository Structure

```
odoo17_final/
├── 📁 accounting_pdf_reports/          # Advanced PDF reporting
├── 📁 account_payment_approval/        # Payment approval workflows
├── 📁 crm_dashboard/                   # CRM analytics dashboard
├── 📁 dynamic_accounts_report/         # Dynamic financial reports
├── 📁 osus_invoice_report/             # Custom invoice reporting
├── 📁 whatsapp_mail_messaging/         # WhatsApp integration
├── 📁 config/                          # Odoo configuration
├── 📁 logs/                            # Application logs
├── 🐳 Dockerfile                       # Docker image definition
├── 🐳 docker-compose.yml               # Multi-container setup
├── 🔧 setup.sh                         # Linux/Mac setup script
├── 🔧 setup.bat                        # Windows setup script
└── 📖 README.md                        # This file
```

## 🛠️ Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space
- **Network**: Internet connection for initial setup

### Required Software
1. **Docker Desktop**
   - [Download for Windows](https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe)
   - [Download for Mac](https://desktop.docker.com/mac/stable/Docker.dmg)
   - [Install on Linux](https://docs.docker.com/engine/install/)

2. **Git**
   - [Download Git](https://git-scm.com/downloads)

## 🚀 Installation

### Method 1: Automated Setup (Recommended)

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/renbran/odoo17_final.git
   cd odoo17_final
   ```

2. **Run setup script:**
   
   **Windows:**
   ```cmd
   setup.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Choose option 1** for first-time setup

### Method 2: Manual Docker Commands

1. **Build the image:**
   ```bash
   docker-compose build
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   ```

## 🎯 Usage

### First Time Access
1. Navigate to http://localhost:8069
2. Create new database or use existing:
   - **Database name**: `odoo`
   - **Email**: `admin@company.com`
   - **Password**: `admin`
   - **Language**: English
   - **Country**: Your country

### Installing Custom Modules
1. Go to **Apps** menu
2. Remove "Apps" filter
3. Search for custom modules:
   - OSUS Invoice Report
   - Dynamic Accounts Report
   - CRM Dashboard
   - And many more...

### Daily Operations
- **Start**: Run setup script and choose option 2
- **Stop**: Run setup script and choose option 3
- **View logs**: Run setup script and choose option 4
- **Backup**: Run setup script and choose option 7

## 📦 Custom Modules Overview

### 📊 Financial & Accounting
- **`accounting_pdf_reports`** - Advanced PDF financial reports
- **`dynamic_accounts_report`** - Real-time financial dashboards
- **`base_accounting_kit`** - Complete accounting toolkit
- **`account_payment_approval`** - Payment approval workflows

### 🎯 CRM & Sales
- **`crm_dashboard`** - Comprehensive CRM analytics
- **`crm_check_approve_limiter`** - CRM approval processes
- **`sales_target_vs_achievement`** - Sales performance tracking

### 📋 Invoice & Reporting
- **`osus_invoice_report`** - Custom invoice templates with QR codes
- **`sale_invoice_detail`** - Enhanced invoice details
- **`statement_report`** - Customer/supplier statements

### 💬 Communication
- **`whatsapp_mail_messaging`** - WhatsApp integration
- **`whatsapp_redirect`** - WhatsApp messaging tools

### 🎨 UI/UX Enhancements
- **`backend_theme_infinito`** - Modern backend theme
- **`muk_web_theme`** - Advanced web interface
- **`web_login_styles`** - Custom login page styles

### 🔧 System Tools
- **`database_cleanup`** - Database maintenance tools
- **`cron_failure_notification`** - Automated job monitoring
- **`hide_menu_user`** - User-specific menu customization

## 🐳 Docker Commands Reference

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f odoo

# Restart Odoo only
docker-compose restart odoo

# Build without cache
docker-compose build --no-cache
```

### Database Operations
```bash
# Access database directly
docker-compose exec db psql -U odoo -d odoo

# Create backup
docker-compose exec db pg_dump -U odoo odoo > backup.sql

# Restore backup
docker-compose exec -T db psql -U odoo -d odoo < backup.sql
```

### Debugging
```bash
# Enter Odoo container
docker-compose exec odoo bash

# Check container status
docker-compose ps

# View resource usage
docker stats
```

## 🔧 Configuration

### Environment Variables
Edit `docker-compose.yml` to customize:
- **Ports**: Change `8069:8069` to use different port
- **Database credentials**: Modify POSTGRES_* variables
- **Odoo settings**: Edit environment section

### Odoo Configuration
Edit `config/odoo.conf` for:
- **Performance tuning**: Workers, memory limits
- **Security settings**: Admin password, database listing
- **Module paths**: Additional addon directories

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8069
netstat -tulpn | grep 8069

# Change port in docker-compose.yml
ports:
  - "8070:8069"  # Use port 8070 instead
```

#### 2. Database Connection Issues
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

#### 3. Module Installation Issues
```bash
# Update module list
docker-compose exec odoo odoo --update=all --stop-after-init

# Clear cache and restart
docker-compose down
docker-compose up -d
```

#### 4. Permission Issues (Linux/Mac)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x setup.sh
```

### Performance Optimization

#### 1. Increase Resources
Edit `config/odoo.conf`:
```ini
workers = 4                    # CPU cores * 2
max_cron_threads = 2          # Background job threads
limit_memory_hard = 2684354560  # 2.5GB
limit_memory_soft = 2147483648  # 2GB
```

#### 2. Database Tuning
```sql
-- Connect to database and run:
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET work_mem = '16MB';
```

## 🔐 Security Notes

### Production Deployment
1. **Change default passwords**:
   - Database password
   - Odoo admin password

2. **Use environment variables**:
   ```yaml
   environment:
     - POSTGRES_PASSWORD=${DB_PASSWORD}
     - ADMIN_PASSWORD=${ADMIN_PASSWORD}
   ```

3. **Enable SSL**:
   - Use reverse proxy (nginx/apache)
   - Configure SSL certificates

4. **Firewall rules**:
   - Restrict database access
   - Use VPN for remote access

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Check service health
docker-compose ps

# Monitor resources
docker stats

# View disk usage
docker system df
```

### Regular Maintenance
1. **Weekly**: Backup database
2. **Monthly**: Update Docker images
3. **Quarterly**: Clean unused Docker resources

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U odoo odoo > "backup_$DATE.sql"
# Upload to cloud storage
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes to modules
4. Test in Docker environment
5. Submit pull request

### Module Development
```bash
# Create new module
mkdir custom_module
cd custom_module
# Add __manifest__.py and module files
```

### Code Standards
- Follow Odoo development guidelines
- Add proper documentation
- Include unit tests
- Update CHANGELOG.md

## 📄 License

This project is licensed under the LGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
1. **Documentation**: Check Odoo official docs
2. **Issues**: Create GitHub issue
3. **Community**: Join Odoo community forums
4. **Commercial**: Contact for professional support

### Useful Links
- [Odoo Documentation](https://www.odoo.com/documentation/17.0/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🎉 What's Next?

After successful setup, you can:
1. **Customize modules** for your business needs
2. **Add new custom modules** to extend functionality
3. **Integrate with external systems** using APIs
4. **Scale horizontally** with multiple Odoo instances
5. **Deploy to production** with proper security measures

---

**Happy Odoo Development! 🚀**

For questions or support, please create an issue or contact the development team.
