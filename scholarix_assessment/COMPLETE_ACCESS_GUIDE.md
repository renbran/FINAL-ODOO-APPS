# 📋 SCHOLARIX Assessment - Complete Access Guide

## 🎯 How to Access the Assessment

### For Candidates (Public Access - No Login Required)

#### **Option 1: Direct URL Access**
Simply visit the landing page in your web browser:

```
http://localhost:8069/assessment
```

**For Production Server:**
```
https://scholarixglobal.com/assessment
```

This will show the professional landing page with:
- Assessment information
- What to expect
- Evaluation criteria
- "Start Assessment Now" button

---

#### **Option 2: Email Invitation Link**
When a candidate receives an email invitation, they click the **"Start Your Assessment"** button in the email, which takes them directly to the landing page.

---

### Assessment User Journey

```
Step 1: Landing Page
URL: /assessment
↓
View information about the assessment
Read evaluation criteria
See time limit (45 minutes)
↓
Click "Start Assessment Now" button

Step 2: Assessment Form
URL: /assessment/start
↓
Timer starts at 45:00
Fill out personal information:
  - Full Name (required)
  - Email (required)
  - Phone (optional)
  - Location (optional)
  - Odoo Experience (required)
  - Sales Experience (required)
↓
Answer 10 assessment questions
Each question requires minimum 50 characters
Character counter shows progress
↓
Click "Submit Assessment" button

Step 3: Submission
URL: /assessment/submit
↓
Form data is validated
Candidate record created
Response record created
Email confirmation sent
↓
Redirected to Thank You page

Step 4: Thank You Page
URL: /assessment/thank-you
↓
Success message displayed
Instructions to check email

Step 5: View Results (Later)
URL: /assessment/view/<access_token>
↓
Candidate receives unique link via email
Click link to view AI scores
See human review (if completed)
View ranking position
```

---

## 🔐 For HR/Admin Staff (Backend Access)

### Accessing the Module

1. **Login to Odoo**
   ```
   http://localhost:8069/web/login
   ```

2. **Navigate to Assessment Module**
   - Click on **"Assessment"** in the main menu (left sidebar)
   - Or search for "Assessment" in the app drawer

3. **Main Menu Structure**
   ```
   Assessment
   ├── Candidates
   │   ├── All Candidates
   │   ├── Pending Review
   │   ├── Under Review
   │   └── Reviewed
   ├── Responses
   ├── AI Scores
   ├── Human Reviews
   ├── Rankings
   ├── Questions
   └── Reports
       ├── Analytics Dashboard
       ├── Score Distribution
       └── Export Data
   ```

### Reviewing Candidates

1. **View All Candidates**
   - Go to: Assessment > Candidates > All Candidates
   - You'll see a list of all candidates with columns:
     - Name
     - Email
     - Status
     - Submission Date
     - Overall Score
     - Rank

2. **Open a Candidate Record**
   - Click on any candidate name
   - You'll see:
     - Personal Information tab
     - Response tab (all answers)
     - AI Score tab (if processed)
     - Human Review tab (for manual review)
     - Ranking tab
     - Notes/History

3. **Perform Human Review**
   - Open candidate record
   - Click "Human Review" tab
   - Click "Create" or "Add Review"
   - Fill in:
     - Overall Score (0-100)
     - Recommendation (dropdown)
     - Strengths (text)
     - Areas for Improvement (text)
     - Comments (text)
   - Click "Save"

---

## 🧪 Testing the Assessment System

### Quick Test Steps

1. **Test Landing Page**
   ```bash
   # Open browser and visit:
   http://localhost:8069/assessment
   ```
   ✅ Check: Landing page loads with hero section, stats, and start button

2. **Test Assessment Form**
   ```bash
   # Click "Start Assessment Now" or visit:
   http://localhost:8069/assessment/start
   ```
   ✅ Check: 
   - Timer starts at 45:00
   - Form has personal info fields
   - 10 questions are displayed
   - Character counters work

3. **Submit Test Assessment**
   - Fill out all required fields
   - Answer all questions (minimum 50 characters each)
   - Click "Submit Assessment"
   
   ✅ Check:
   - No errors
   - Redirected to Thank You page
   - Email confirmation sent

4. **Verify Backend**
   - Login to Odoo admin
   - Go to: Assessment > Candidates
   - Find your test submission
   
   ✅ Check:
   - Candidate record created
   - Status is "Submitted"
   - Responses are saved
   - AI scoring triggered (may take a few minutes)

---

## 🔧 Troubleshooting

### Problem 1: "Page Not Found" (404 Error)

**Issue:** Visiting `/assessment` shows 404 error

**Solutions:**
```bash
# 1. Ensure module is installed
Go to: Apps > Search "SCHOLARIX Assessment" > Install/Upgrade

# 2. Update the module
docker-compose exec odoo odoo --update=scholarix_assessment --stop-after-init

# 3. Restart Odoo
docker-compose restart odoo

# 4. Clear browser cache
Ctrl + Shift + R (hard refresh)
```

---

### Problem 2: Questions Not Showing

**Issue:** Assessment form loads but no questions appear

**Solutions:**
```bash
# 1. Check if questions exist in database
Login to Odoo > Assessment > Questions
Ensure there are 10 active questions (q10, q20, q30...q100)

# 2. If questions are missing, they should be loaded from data file
docker-compose exec odoo odoo --update=scholarix_assessment --stop-after-init

# 3. Check logs for errors
docker-compose logs -f odoo | grep "assessment"
```

---

### Problem 3: Timer Not Working

**Issue:** Timer doesn't start or doesn't count down

**Solutions:**
```bash
# 1. Check browser console for JavaScript errors
Press F12 > Console tab
Look for red error messages

# 2. Ensure JavaScript is enabled in browser
Settings > Site Settings > JavaScript > Allowed

# 3. Clear browser cache
Ctrl + Shift + Delete > Clear cached files

# 4. Try different browser (Chrome, Firefox, Edge)
```

---

### Problem 4: Form Submission Fails

**Issue:** Clicking "Submit Assessment" shows error or nothing happens

**Solutions:**
```bash
# 1. Check all required fields are filled:
- Full Name
- Email
- Odoo Experience
- Sales Experience
- All 10 questions (minimum 50 characters each)

# 2. Check browser console for errors
Press F12 > Console tab

# 3. Check Odoo logs
docker-compose logs -f odoo

# 4. Verify CSRF token is valid
Clear browser cookies and try again
```

---

### Problem 5: Can't Access Backend Module

**Issue:** No "Assessment" menu in Odoo

**Solutions:**
```bash
# 1. Check user has access rights
Settings > Users & Companies > Users
Select your user > Access Rights tab
Ensure "Assessment Manager" or "Assessment User" is checked

# 2. Check module is installed
Apps > Search "SCHOLARIX Assessment"
Status should be "Installed"

# 3. Refresh browser
Ctrl + Shift + R

# 4. Update module
Apps > SCHOLARIX Assessment > Upgrade
```

---

## 📧 Sending Assessment Invitations

### Method 1: Via Email Template (Recommended)

1. **Navigate to Candidate Record**
   - Assessment > Candidates > Create (or open existing)

2. **Fill Candidate Info**
   - Full Name
   - Email
   - (Other fields optional at this stage)

3. **Send Invitation**
   - Click "Send Invitation" button (if available)
   - Or use "Send Email" action
   - Select template: "Assessment: Invitation to Candidate"
   - Click "Send"

4. **Candidate Receives Email**
   - Professional Scholarix Global branded email
   - "Start Your Assessment" button
   - Clicking button opens landing page

---

### Method 2: Share Direct Link

Simply copy and share this link:
```
https://scholarixglobal.com/assessment
```

Or for local development:
```
http://localhost:8069/assessment
```

---

### Method 3: Embed in Website/Email Campaigns

```html
<!-- Email Template -->
<a href="https://scholarixglobal.com/assessment" 
   style="display:inline-block; background:#667eea; color:white; 
          padding:15px 30px; text-decoration:none; border-radius:5px;">
    Take Assessment Now
</a>

<!-- Website Button -->
<a href="https://scholarixglobal.com/assessment" class="btn btn-primary">
    Start Assessment
</a>
```

---

## 🎨 Customizing the Assessment

### Change Timer Duration

**File:** `scholarix_assessment/controllers/portal.py`

```python
@http.route('/assessment/start', type='http', auth='public', website=True)
def assessment_form(self, **kw):
    questions = request.env['assessment.question'].sudo().get_active_questions()
    
    values = {
        'questions': questions,
        'page_name': 'assessment',
        'time_limit': 60,  # Change to 60 minutes (default: 45)
    }
    
    return request.render('scholarix_assessment.portal_assessment_form', values)
```

After changing, update the module:
```bash
docker-compose exec odoo odoo --update=scholarix_assessment --stop-after-init
```

---

### Add/Edit Questions

1. **Via Odoo UI (Recommended)**
   - Login to Odoo
   - Go to: Assessment > Questions
   - Click "Create" or edit existing
   - Fill in:
     - Question Text
     - Help Text (optional)
     - Sequence (10, 20, 30...100)
     - Category
     - Active (checkbox)
     - Min/Max Character Count
   - Click "Save"

2. **Via Data File**
   - Edit: `scholarix_assessment/data/assessment_questions_data.xml`
   - Add new question record
   - Update module

---

## 📊 Viewing Results & Reports

### Analytics Dashboard

1. **Access Dashboard**
   - Assessment > Reports > Analytics Dashboard
   - Or click "Dashboard" button in main menu

2. **Available Metrics**
   - Total candidates
   - Pending reviews
   - Average scores
   - Score distribution chart
   - Top performers
   - Recent submissions

### Export Data

1. **Export Candidates**
   - Assessment > Candidates
   - Select candidates (checkboxes)
   - Action > Export
   - Choose fields
   - Download CSV/Excel

2. **Generate Reports**
   - Assessment > Reports
   - Select report type
   - Set filters (date range, status, etc.)
   - Click "Generate"
   - Print or export PDF

---

## 🔄 AI Scoring Process

### How It Works

1. **Automatic Trigger**
   - When candidate submits assessment
   - Cron job checks for new submissions
   - Runs every 15 minutes (configurable)

2. **AI Analysis**
   - Uses OpenAI GPT-4 API
   - Analyzes all 10 responses
   - Scores 5 categories:
     - Technical Expertise (Odoo)
     - Sales Capabilities
     - Communication Skills
     - Learning Agility
     - Cultural Fit

3. **Score Storage**
   - Creates AI Score record
   - Links to candidate
   - Calculates overall score
   - Identifies strengths/weaknesses

4. **Fallback Mode**
   - If API fails, uses mock scoring
   - Based on response length and quality
   - Ensures system continues working

### Manual Trigger

If AI scoring doesn't run automatically:

1. **Via Candidate Record**
   - Open candidate
   - Click "Trigger AI Scoring" button
   - Wait for process to complete

2. **Via Python Code**
   ```python
   # In Odoo shell or custom script
   candidate = env['assessment.candidate'].browse(CANDIDATE_ID)
   candidate.trigger_ai_scoring()
   ```

---

## 🎯 Quick Reference Commands

### Module Operations
```bash
# Install module
docker-compose exec odoo odoo -i scholarix_assessment --stop-after-init

# Update module
docker-compose exec odoo odoo -u scholarix_assessment --stop-after-init

# Restart Odoo
docker-compose restart odoo

# View logs
docker-compose logs -f odoo

# Clear cache
bash clean_cache.sh
```

### Test URLs
```bash
# Landing page
http://localhost:8069/assessment

# Assessment form
http://localhost:8069/assessment/start

# Thank you page
http://localhost:8069/assessment/thank-you

# View results (replace TOKEN)
http://localhost:8069/assessment/view/TOKEN
```

---

## 📞 Support & Additional Help

**Module:** scholarix_assessment  
**Version:** 17.0.2.0.0  
**Documentation:**
- `LANDING_PAGE_TIMER_FEATURE.md` - Feature documentation
- `PRODUCTION_READY_REPORT.md` - Production checklist
- `XML_SYNTAX_ERROR_FIX.md` - Recent fixes

**For Issues:**
1. Check logs: `docker-compose logs -f odoo`
2. Check browser console: Press F12
3. Clear cache: `bash clean_cache.sh`
4. Restart Odoo: `docker-compose restart odoo`

---

## ✅ Final Checklist

Before using in production:

- [ ] Module installed and upgraded
- [ ] All 10 questions exist and are active
- [ ] Landing page loads at `/assessment`
- [ ] Assessment form loads at `/assessment/start`
- [ ] Timer starts and counts down
- [ ] Form submits successfully
- [ ] Thank you page displays
- [ ] Backend menu accessible
- [ ] Email invitations work
- [ ] AI scoring configured (OpenAI API key set)
- [ ] Test candidate submission completed
- [ ] Access rights configured for users

---

**That's it! You're ready to use the SCHOLARIX Assessment System! 🎉**

Start by visiting: `http://localhost:8069/assessment`
