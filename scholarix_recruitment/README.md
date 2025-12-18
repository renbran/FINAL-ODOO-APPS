# Scholarix Global - Recruitment Extension

![Version](https://img.shields.io/badge/version-17.0.1.0.0-blue)
![License](https://img.shields.io/badge/license-LGPL--3-green)
![Odoo](https://img.shields.io/badge/odoo-17.0-purple)

**Navigate. Innovate. Transform.**

---

## 📋 Overview

The **Scholarix Global Recruitment Extension** is a production-ready Odoo 17 module that extends the standard recruitment functionality with UAE-compliant offer letter generation, comprehensive candidate tracking, and professional branded documentation.

This module transforms the recruitment process with:
- ✅ UAE Labour Law compliance
- ✅ Professional offer letter generation
- ✅ Automated compensation calculations
- ✅ Email automation with branded templates
- ✅ Deep Ocean brand identity throughout

---

## 🎨 Brand Identity

This module implements Scholarix Global's **Deep Ocean** visual identity:

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Deep Navy** | `#0c1e34` | Primary headers, authority |
| **Ocean Blue** | `#1e3a8a` | Secondary elements, professionalism |
| **Sky Blue** | `#4fc3f7` | Accents, interactive elements |
| **Ice White** | `#e8f4fd` | Backgrounds, clarity |

**Typography:**
- Headings: Poppins (Bold)
- Body: Roboto (Regular)

---

## ✨ Features

### 1. Extended Applicant Information

**Personal Information Tab:**
- Full name in Arabic (للاسم الكامل)
- Nationality tracking
- Emirates ID (15-digit format)
- Passport number
- Date of birth
- UAE mobile number
- Personal email
- Current UAE address

**Employment Details Tab:**
- Position title
- Department assignment
- Reporting manager
- Employment type (Unlimited/Limited/Part-Time/Consultant)
- Contract duration (for limited contracts)
- Probation period (default: 180 days)
- Proposed start date
- Work location
- Notice period

**Compensation & Benefits Tab:**
- Basic salary (monthly)
- Housing allowance
- Transport allowance
- Other allowances
- **Automated totals:** Monthly + Annual
- Annual leave days (default: 30)
- Health insurance tier (Basic/Enhanced/Premium)
- Visa sponsorship checkbox
- Flight tickets (None/Annual/Bi-annual)
- Additional benefits notes

**Offer Letter Tab:**
- Auto-generated reference number (format: `SGO-YYYYMMDD-XXXX`)
- Offer letter date
- Offer validity (auto-calculated: +14 days)
- Acceptance date tracking
- Digital signature upload
- Quick action buttons

---

### 2. Professional Offer Letter Generation

**UAE-Compliant Content:**
- ✅ Company letterhead with logo
- ✅ Unique reference number
- ✅ Employment details section
- ✅ Salary breakdown table
- ✅ Benefits & entitlements
- ✅ Working hours (Sunday-Thursday, 9 AM - 6 PM)
- ✅ Notice period & termination clause
- ✅ Confidentiality & NDA reference
- ✅ Required documents checklist
- ✅ Signature sections (Company + Candidate)
- ✅ Offer validity period

**Visual Design:**
- Minimalist, data-driven aesthetic
- Professional gradient dividers
- Color-coded sections (Deep Ocean palette)
- Clean typography hierarchy
- Generous white space
- Print-optimized layout

---

### 3. Email Automation

**Branded Email Template:**
- Gradient header with Scholarix branding
- Professional body content
- Offer details summary box
- Call-to-action for document submission
- Footer with tagline and contact info
- Automatic PDF attachment

**Smart Sending:**
- One-click email dispatch
- Success notification
- Tracks email status
- Uses candidate's personal email

---

## 📦 Installation

### Prerequisites
- Odoo 17 (Community or Enterprise)
- Standard `hr_recruitment` module installed
- Docker environment (recommended)

### Installation Steps

#### Method 1: Docker Installation (Recommended)

```bash
# 1. Copy module to extra-addons directory
cp -r scholarix_recruitment /path/to/odoo/extra-addons/

# 2. Restart Odoo container
docker-compose restart odoo

# 3. Update apps list (via Odoo UI)
# Settings > Apps > Update Apps List

# 4. Search and install
# Apps > Search "Scholarix" > Install
```

#### Method 2: Manual Installation

```bash
# 1. Copy module to addons path
cp -r scholarix_recruitment /opt/odoo/custom/addons/

# 2. Update apps list
odoo --update=base --stop-after-init

# 3. Install via UI
# Apps > Scholarix Global - Recruitment Extension > Install
```

### Post-Installation Setup

1. **Add Company Logo:**
   - Go to Settings > General Settings > Companies
   - Upload Scholarix Global logo
   - Recommended size: 300x80px, PNG format

2. **Configure Email Server:**
   - Settings > Technical > Outgoing Mail Servers
   - Set `careers@scholarixglobal.com` as sender

3. **Verify Installation:**
   - Go to Recruitment > Applicants
   - Open any applicant
   - Verify new tabs appear: Personal Information, Employment Details, Compensation, Offer Letter

---

## 🚀 Usage Guide

### Creating an Offer Letter

**Step 1: Fill Applicant Information**
1. Go to **Recruitment > Applications**
2. Create new applicant or open existing
3. Fill basic details (Name, Email, Job Position)

**Step 2: Add Personal Information**
1. Navigate to **Personal Information** tab
2. Enter:
   - Full name in Arabic
   - Nationality
   - Emirates ID
   - Passport number
   - Date of birth
   - UAE mobile number
   - Personal email
   - Current address

**Step 3: Define Employment Terms**
1. Go to **Employment Details** tab
2. Set:
   - Position title (e.g., "Senior Odoo Consultant")
   - Department
   - Reporting manager
   - Employment type
   - Start date
   - Probation period (default: 180 days)
   - Notice period (default: 30 days)

**Step 4: Configure Compensation**
1. Open **Compensation & Benefits** tab
2. Enter salary breakdown:
   - Basic salary (AED)
   - Housing allowance
   - Transport allowance
   - Other allowances
3. System auto-calculates totals
4. Set benefits:
   - Annual leave days (default: 30)
   - Health insurance tier
   - Visa sponsorship (checkbox)
   - Flight tickets
   - Additional benefits notes

**Step 5: Generate Offer Letter**
1. Navigate to **Offer Letter** tab
2. Verify auto-generated reference number
3. Adjust offer letter date if needed
4. Click **"Generate Offer Letter"** button
5. Review PDF output

**Step 6: Send to Candidate**
1. Verify candidate email address
2. Click **"Send Offer Letter"** button
3. Confirm success notification
4. PDF automatically attached to email

---

## 📄 Sample Offer Letter Output

```
┌─────────────────────────────────────────────────────────────┐
│  SCHOLARIX GLOBAL                                           │
│  Where Ancient Wisdom Meets Artificial Intelligence         │
├─────────────────────────────────────────────────────────────┤
│  Reference: SGO-20241114-0042     Date: 14 November 2024   │
│                                                             │
│  Ahmed Al-Mahmoud                                           │
│  Dubai Marina, Dubai, UAE                                   │
│                                                             │
│  SUBJECT: OFFER OF EMPLOYMENT – SENIOR ODOO CONSULTANT     │
│                                                             │
│  Dear Ahmed Al-Mahmoud,                                     │
│                                                             │
│  1. EMPLOYMENT DETAILS                                      │
│     Position: Senior Odoo Consultant                        │
│     Department: Technology Solutions                        │
│     Start Date: 1 December 2024                             │
│     Contract: Unlimited                                     │
│                                                             │
│  2. COMPENSATION                                            │
│     ┌───────────────────────┬──────────────┐              │
│     │ Basic Salary          │ AED 15,000   │              │
│     │ Housing Allowance     │ AED 5,000    │              │
│     │ Transport Allowance   │ AED 2,000    │              │
│     ├───────────────────────┼──────────────┤              │
│     │ Total Monthly         │ AED 22,000   │              │
│     │ Total Annual          │ AED 264,000  │              │
│     └───────────────────────┴──────────────┘              │
│                                                             │
│  3. BENEFITS                                                │
│     • Annual Leave: 30 days                                 │
│     • Visa: Fully sponsored                                 │
│     • Health Insurance: Enhanced Plan                       │
│     • Flight Tickets: Annual return ticket                  │
│                                                             │
│  [Additional sections...]                                   │
│                                                             │
│  Navigate. Innovate. Transform.                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Details

### Module Structure

```
scholarix_recruitment/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── hr_applicant.py          # Extended applicant model
├── views/
│   └── hr_applicant_views.xml   # Form, tree, search views
├── reports/
│   └── offer_letter_template.xml # QWeb PDF template
├── data/
│   └── email_templates.xml      # Email templates
├── security/
│   └── ir.model.access.csv      # Access rights
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── banner.png
│   └── src/
│       ├── img/
│       │   └── scholarix_logo.png
│       └── scss/
│           └── report_styles.scss # Report styling
└── README.md
```

### Key Files

**`models/hr_applicant.py`**
- Inherits `hr.applicant` model
- Adds 30+ new fields
- Implements computed fields for salary totals
- Auto-generates offer reference numbers
- Action methods for PDF generation and email sending

**`reports/offer_letter_template.xml`**
- QWeb PDF report definition
- Professional letterhead layout
- Conditional sections based on data
- Brand-compliant styling
- Print-optimized formatting

**`data/email_templates.xml`**
- Mail template for offer letters
- HTML email with inline CSS
- Automatic PDF attachment
- Responsive design

---

## 🎯 UAE Compliance Checklist

This module ensures 100% compliance with UAE Ministry of Human Resources requirements:

✅ **Essential Elements:**
- [x] Company legal name and address
- [x] Employee full name and nationality
- [x] Position title and department
- [x] Employment type (unlimited/limited contract)
- [x] Start date and probation period (max 180 days)
- [x] Salary breakdown (basic + allowances)
- [x] Working hours and weekly rest days
- [x] Annual leave entitlement (minimum 30 days)
- [x] Notice period for termination
- [x] Visa and health insurance provisions
- [x] Signature sections for both parties

✅ **Additional Standards:**
- [x] Unique reference number
- [x] Offer validity period
- [x] Document submission requirements
- [x] Confidentiality clause reference
- [x] Professional letterhead with contact details

---

## 🔐 Security & Permissions

**Access Rights:**
- **Base User:** Read, Write, Create (no delete)
- **Recruitment User:** Full access (Read, Write, Create, Delete)
- **Recruitment Manager:** Full access (Read, Write, Create, Delete)

**Record Rules:**
- Inherits from `hr_recruitment` module rules
- Multi-company support
- User-based visibility controls

---

## 🐛 Troubleshooting

### Common Issues

**Issue 1: Offer letter PDF not generating**
```
Solution:
1. Check Odoo logs: docker-compose logs -f odoo
2. Verify wkhtmltopdf is installed
3. Update module: docker-compose exec odoo odoo -u scholarix_recruitment --stop-after-init
```

**Issue 2: Email not sending**
```
Solution:
1. Configure outgoing mail server (Settings > Technical > Email > Outgoing Mail Servers)
2. Test email configuration
3. Check email template: Settings > Technical > Email > Templates
4. Verify candidate email address is valid
```

**Issue 3: New fields not visible**
```
Solution:
1. Clear browser cache (Ctrl + Shift + Delete)
2. Restart Odoo: docker-compose restart odoo
3. Update module: Apps > Scholarix Recruitment > Upgrade
```

**Issue 4: Logo not appearing in PDF**
```
Solution:
1. Upload company logo: Settings > Companies > Upload Logo
2. Recommended format: PNG, 300x80px
3. Regenerate offer letter
```

**Issue 5: Styling not applied**
```
Solution:
1. Clear assets: Settings > Technical > Assets > Clear Cache
2. Restart Odoo container
3. Regenerate PDF
```

---

## 📊 Database Schema

### New Fields Added to `hr.applicant`

| Field Name | Type | Description |
|------------|------|-------------|
| `full_name_arabic` | Char | Full name in Arabic |
| `nationality` | Many2one | Nationality (res.country) |
| `emirates_id` | Char | UAE Emirates ID (15 digits) |
| `passport_number` | Char | Passport number |
| `date_of_birth` | Date | Date of birth |
| `uae_mobile` | Char | UAE mobile number |
| `personal_email` | Char | Personal email address |
| `current_address` | Text | Current UAE address |
| `position_title` | Char | Official job title |
| `department_id` | Many2one | Department (hr.department) |
| `reporting_manager` | Many2one | Reporting manager (hr.employee) |
| `employment_type` | Selection | Contract type |
| `contract_duration_months` | Integer | Contract duration |
| `probation_period_days` | Integer | Probation period (default: 180) |
| `proposed_start_date` | Date | Expected start date |
| `work_location` | Char | Primary work location |
| `basic_salary` | Monetary | Monthly basic salary |
| `housing_allowance` | Monetary | Monthly housing allowance |
| `transport_allowance` | Monetary | Monthly transport allowance |
| `other_allowances` | Monetary | Other monthly allowances |
| `total_monthly_salary` | Monetary | Computed: Total monthly |
| `annual_salary` | Monetary | Computed: Total annual |
| `annual_leave_days` | Integer | Annual leave entitlement |
| `health_insurance` | Selection | Insurance tier |
| `visa_provided` | Boolean | Visa sponsorship |
| `flight_tickets` | Selection | Flight ticket provision |
| `additional_benefits` | Text | Other benefits notes |
| `notice_period_days` | Integer | Notice period (default: 30) |
| `offer_letter_date` | Date | Offer letter issue date |
| `offer_valid_until` | Date | Computed: Offer expiry |
| `offer_letter_reference` | Char | Computed: Unique reference |
| `candidate_signature` | Binary | Digital signature image |
| `acceptance_date` | Date | Date of acceptance |
| `company_currency_id` | Many2one | Currency (res.currency) |

---

## 🔄 Update & Maintenance

### Updating the Module

```bash
# 1. Stop Odoo
docker-compose stop odoo

# 2. Update module files
# (Replace files in /path/to/extra-addons/scholarix_recruitment/)

# 3. Update in Odoo
docker-compose start odoo
docker-compose exec odoo odoo -u scholarix_recruitment --stop-after-init

# 4. Verify update
# Apps > Scholarix Recruitment > Check version number
```

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 17.0.1.0.0 | 2024-11-14 | Initial release |

---

## 📞 Support & Contact

**Scholarix Global**
- **Website:** [www.scholarixglobal.com](https://www.scholarixglobal.com)
- **Email:** careers@scholarixglobal.com
- **Location:** Dubai, United Arab Emirates

**Module Support:**
- Report issues: [GitHub Issues](#)
- Documentation: This README
- Email support: support@scholarixglobal.com

---

## 📜 License

This module is licensed under **LGPL-3** (GNU Lesser General Public License v3.0).

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Sublicense

Under the conditions:
- ⚖️ License and copyright notice
- ⚖️ State changes
- ⚖️ Disclose source
- ⚖️ Same license

---

## 🙏 Credits

**Developed by:** Scholarix Global Technology Team

**Odoo Framework:** [Odoo S.A.](https://www.odoo.com)

**Fonts:**
- Poppins: Google Fonts
- Roboto: Google Fonts

**Icons:** Font Awesome

---

## 🎯 Roadmap

**Planned Features (v17.0.2.0.0):**
- [ ] Multi-language support (Arabic, English)
- [ ] Digital signature integration (DocuSign/SignNow)
- [ ] Custom branding per company (multi-company)
- [ ] Offer letter templates library
- [ ] Candidate portal for offer acceptance
- [ ] Integration with onboarding module
- [ ] Advanced analytics dashboard
- [ ] Mobile app support

---

## 📚 Additional Resources

**Related Documentation:**
- [Odoo 17 HR Documentation](https://www.odoo.com/documentation/17.0/applications/hr.html)
- [UAE Labour Law Guide](https://u.ae/en/information-and-services/jobs/employment-contracts)
- [QWeb Reports Tutorial](https://www.odoo.com/documentation/17.0/developer/reference/backend/reports.html)

**Learning Resources:**
- [Odoo Module Development](https://www.odoo.com/slides/fundamentals-16)
- [Python for Odoo](https://www.odoo.com/slides/python-32)
- [QWeb Templating](https://www.odoo.com/slides/qweb-29)

---

<div align="center">

**Navigate. Innovate. Transform.**

![Scholarix Global](https://via.placeholder.com/150x50/0c1e34/4fc3f7?text=SCHOLARIX+GLOBAL)

*Building the future with Ancient Wisdom and Artificial Intelligence*

</div>

---

## 🔖 Quick Reference

**Module Technical Name:** `scholarix_recruitment`
**Display Name:** Scholarix Global - Recruitment Extension
**Version:** 17.0.1.0.0
**Category:** Human Resources
**Author:** Scholarix Global
**License:** LGPL-3
**Website:** https://www.scholarixglobal.com

**Dependencies:**
- `base`
- `hr`
- `hr_recruitment`
- `mail`

**Supported Odoo Versions:** 17.0 Community & Enterprise

**Installation Time:** < 5 minutes
**Configuration Time:** 10-15 minutes
**Learning Curve:** Easy (if familiar with hr_recruitment)

---

**Last Updated:** November 14, 2024
**Maintained By:** Scholarix Global Development Team
