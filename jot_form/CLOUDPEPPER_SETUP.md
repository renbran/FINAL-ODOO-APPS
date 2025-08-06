# JotForm Webhook for CloudPepper Hosting

## CloudPepper Setup Instructions

Since you're hosted on CloudPepper, here are the specific steps to set up the JotForm webhook:

### 1. CloudPepper Environment Considerations
- CloudPepper uses managed Python environments
- System packages are pre-installed
- Custom Python packages may need special handling

### 2. Installation Options for CloudPepper

#### Option A: Use CloudPepper's Python Environment
```bash
# On CloudPepper, try installing to user directory
pip3 install --user Flask==2.3.3 requests==2.31.0 gunicorn==21.2.0 python-dotenv==1.0.0
```

#### Option B: Use System Packages (Recommended for CloudPepper)
```bash
# Most packages are likely already available on CloudPepper
# Check what's available:
python3 -c "import flask; print('Flask available')"
python3 -c "import requests; print('Requests available')"
python3 -c "import gunicorn; print('Gunicorn available')"
```

#### Option C: Contact CloudPepper Support
If the above don't work, contact CloudPepper support to:
- Install the required packages system-wide
- Get access to a virtual environment
- Configure the webhook service

### 3. CloudPepper Deployment Steps

1. **Upload Files**: Use CloudPepper's file manager to upload:
   - `jotform_odoo_webhook.py`
   - `enhanced_webhook.py`
   - `.env` (configured with your settings)

2. **Configure Environment Variables**:
   ```
   ODOO_URL=https://your-cloudpepper-odoo-url
   ODOO_DB=your_database_name
   ODOO_USERNAME=your_username
   ODOO_PASSWORD=your_password
   WEBHOOK_SECRET=your_secret_key
   ```

3. **Set Up the Service**:
   - Use CloudPepper's process manager
   - Or run as a background service
   - Configure reverse proxy if needed

### 4. CloudPepper-Specific Configuration

Since CloudPepper manages the server environment, you'll need to:
- Work with their support team for custom services
- Use their recommended deployment methods
- Follow their security and networking guidelines

### 5. Alternative: Simple Python Script (No Dependencies)

If package installation is problematic, I can create a version that uses only standard library modules.

### Next Steps:
1. Check what Python packages are already available
2. Configure your .env file
3. Test the webhook locally
4. Deploy through CloudPepper's management interface
