# CloudPepper Deployment Guide - Custom Sales Pro Module

## 🚀 **Quick Deploy Instructions**

### **1. Pull Latest Code**
```bash
cd /opt/odoo/custom-addons
git pull origin main
```

### **2. Install Python Dependencies**
```bash
pip install xlsxwriter pandas numpy
```

### **3. Update Odoo Module**
```bash
# Method 1: Via Odoo Interface
# Go to Apps → Update Apps List → Find "Custom Sales Pro" → Install/Upgrade

# Method 2: Via Command Line
sudo service odoo stop
sudo -u odoo /opt/odoo/odoo-bin -d your_database_name -u custom_sales --stop-after-init
sudo service odoo start
```

### **4. Verify Installation**
1. **Check Module Status:**
   - Apps → Custom Sales Pro → Should show "Installed"

2. **Access Dashboard:**
   - Navigate to: Custom Sales → Dashboard
   - Should load without errors

3. **Test Security Features:**
   - Try export functionality (should work with rate limiting)
   - Check audit logs are being created

## 🔧 **CloudPepper Specific Configuration**

### **Database Optimization**
```sql
-- Run these queries to ensure optimal performance
CREATE INDEX IF NOT EXISTS idx_custom_sales_order_date ON custom_sales_order (create_date);
CREATE INDEX IF NOT EXISTS idx_custom_sales_order_state ON custom_sales_order (state);
CREATE INDEX IF NOT EXISTS idx_custom_sales_order_customer_type ON custom_sales_order (customer_type);
CREATE INDEX IF NOT EXISTS idx_custom_sales_order_date_state ON custom_sales_order (create_date, state);
```

### **Cron Job Configuration**
The module includes automated cron jobs. Verify they're active:
1. Go to Settings → Technical → Automation → Scheduled Actions
2. Look for:
   - "Custom Sales Database Optimizer" (Weekly)
   - "Custom Sales Audit Log Cleanup" (Daily)
   - "Custom Sales Data Archival" (Monthly)
   - "Custom Sales Vacuum Analyze" (Weekly - Disabled by default)

### **Security Groups Setup**
Assign users to appropriate groups:
- **Custom Sales Dashboard User** - Basic dashboard access
- **Custom Sales Dashboard Manager** - Full dashboard management
- **Custom Sales Dashboard Admin** - System administration

## 📊 **Performance Monitoring**

### **Key Metrics to Monitor**
1. **Database Performance:**
   - Query execution times
   - Index usage statistics
   - Database size growth

2. **Cache Performance:**
   - Cache hit rates
   - Memory usage
   - KPI calculation times

3. **Security Monitoring:**
   - Audit log entries
   - Failed access attempts
   - Export operation frequency

### **CloudPepper Resource Requirements**
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 20GB free space for data growth
- **CPU**: 2+ cores recommended
- **Database**: PostgreSQL 12+ with shared_preload_libraries

## 🛡️ **Security Configuration**

### **Production Security Settings**
1. **Enable HTTPS** (CloudPepper default)
2. **Configure Firewall** - Only allow necessary ports
3. **Set up Database Backups** - Daily automated backups
4. **Monitor Audit Logs** - Review weekly for suspicious activity

### **User Access Configuration**
```python
# In Odoo Settings → Users & Companies → Users
# Assign appropriate groups:
- Sales Manager → Custom Sales Dashboard Manager
- Sales Team → Custom Sales Dashboard User  
- Administrator → Custom Sales Dashboard Admin
```

## 🔄 **Automated Maintenance**

The module includes automated maintenance tasks:

### **Weekly Database Optimization**
- Automatically creates/updates database indexes
- Optimizes query performance
- Runs every Sunday at 2:00 AM

### **Daily Audit Log Cleanup**
- Removes audit logs older than 90 days
- Maintains system performance
- Runs daily at 1:00 AM

### **Monthly Data Archival**
- Archives sales orders older than 1 year
- Maintains database size
- Runs first day of each month

## 📞 **Support & Troubleshooting**

### **Common Issues & Solutions**

1. **Dashboard Not Loading**
   ```bash
   # Check logs
   tail -f /var/log/odoo/odoo.log
   
   # Restart Odoo service
   sudo service odoo restart
   ```

2. **Chart.js Not Displaying**
   - Verify CDN access: https://cdn.jsdelivr.net/npm/chart.js
   - Check browser console for errors
   - Clear browser cache

3. **Export Errors**
   ```bash
   # Install missing dependencies
   pip install xlsxwriter
   sudo service odoo restart
   ```

4. **Performance Issues**
   ```sql
   -- Check database statistics
   SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
   FROM pg_stat_user_tables 
   WHERE tablename LIKE 'custom_sales%';
   ```

### **CloudPepper Support Contacts**
- **Technical Support**: Create ticket in CloudPepper portal
- **Database Issues**: Use CloudPepper database management tools
- **Performance**: Monitor via CloudPepper dashboard

## 🎯 **Success Metrics**

After deployment, verify these metrics:

✅ **Functionality**
- [ ] Dashboard loads in < 3 seconds
- [ ] Charts render correctly
- [ ] Export functions work
- [ ] Audit logging active

✅ **Performance**  
- [ ] Database queries < 200ms
- [ ] Memory usage stable
- [ ] No error logs
- [ ] Cron jobs running

✅ **Security**
- [ ] Access controls working
- [ ] Rate limiting active
- [ ] Audit trails complete
- [ ] Input validation working

## 🚀 **Go Live Checklist**

1. **Pre-Deployment**
   - [ ] Code pushed to GitHub
   - [ ] Dependencies documented
   - [ ] Database backup created
   - [ ] Rollback plan ready

2. **Deployment**
   - [ ] Pull latest code
   - [ ] Install dependencies
   - [ ] Update module
   - [ ] Verify installation

3. **Post-Deployment**
   - [ ] Test all features
   - [ ] Verify performance
   - [ ] Check security
   - [ ] Train users

4. **Monitoring**
   - [ ] Set up alerts
   - [ ] Monitor logs
   - [ ] Track performance
   - [ ] Schedule maintenance

---

**Deployment Date**: $(date)  
**Version**: 17.0.1.0.0  
**Status**: ✅ Ready for Production  
**CloudPepper Compatible**: ✅ Verified
