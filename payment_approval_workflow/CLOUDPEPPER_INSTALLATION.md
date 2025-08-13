# CloudPepper Installation Guide for Payment Approval Workflow

## ✅ Import Error Fixed

The critical import error you encountered has been resolved:

**Error:** `ImportError: cannot import name 'safe_str_cmp' from 'werkzeug.security'`

**Fix Applied:** Changed the import in `controllers/portal.py` from:
```python
from werkzeug.security import safe_str_cmp as consteq
```

To:
```python
from odoo.tools import consteq
```

This uses Odoo's built-in secure comparison function instead of the deprecated werkzeug function.

## 📦 Installation Steps for CloudPepper

1. **Upload Module Files**
   - Upload the entire `payment_approval_workflow` folder to your CloudPepper addons directory
   - Ensure all files are uploaded correctly (24 files total)

2. **Install Python Dependencies**
   Since CloudPepper manages the environment, the required dependencies should already be available:
   - `qrcode` - For QR code generation
   - `uuid` - For unique token generation (built-in Python)

3. **Update App List**
   - Go to Apps in your Odoo interface
   - Click "Update App List"
   - Search for "Payment Approval Workflow"

4. **Install the Module**
   - Click Install on the "Payment Approval Workflow" module
   - The module should install successfully without the import error

## 🔧 Post-Installation Configuration

1. **Assign Security Groups**
   - Go to Settings → Users & Companies → Groups
   - Assign users to appropriate groups:
     - Payment Reviewer
     - Payment Approver
     - Payment Authorizer

2. **Verify Email Configuration**
   - Ensure your email server is configured
   - Test email notifications

3. **Test the Module**
   - Create a test payment
   - Submit it for review
   - Verify the approval workflow works

## 🚨 Troubleshooting

If you still encounter issues after the import fix:

1. **Clear Browser Cache**
   - Hard refresh your browser (Ctrl+F5)
   - Clear Odoo assets cache if possible

2. **Check Module Dependencies**
   - Ensure all required modules are installed:
     - account, mail, web, portal, website

3. **Verify File Upload**
   - Ensure all 24 module files are properly uploaded
   - Check file permissions on CloudPepper

4. **Check Logs**
   - Review CloudPepper logs for any other errors
   - Look for specific error messages

## 📞 Support

If you continue to experience issues, please provide:
- The exact error message
- Steps that led to the error
- Your CloudPepper configuration details

The module is now fully compatible with Odoo 17 and should install successfully on CloudPepper!
