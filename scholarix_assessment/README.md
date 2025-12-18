# SCHOLARIX Assessment System - Odoo 17 Module

## 📋 Overview

World-class AI-powered candidate assessment and evaluation system for Odoo 17. This module provides a complete end-to-end solution for evaluating candidates through intelligent assessments, AI scoring, human reviews, and comprehensive analytics.

## ✨ Key Features

### 🎯 Core Functionality
- **Public Assessment Portal** - Candidate-facing form with 10 comprehensive questions
- **AI-Powered Scoring** - OpenAI GPT-4 integration for intelligent evaluation across 5 categories
- **Human Review System** - Override and adjust AI scores with detailed review workflow
- **Candidate Rankings** - Automatic leaderboard and percentile calculations
- **Advanced Analytics Dashboard** - Real-time insights and statistics
- **Audit Trail** - Complete activity logging for compliance

### 📊 Scoring Categories
1. **Technical Score** (25% weight) - Odoo/ERP knowledge, automation skills
2. **Sales Score** (25% weight) - Client management, objection handling
3. **Communication Score** (20% weight) - Clarity, articulation, simplification
4. **Learning Agility** (15% weight) - Adaptability, growth mindset
5. **Cultural Fit** (15% weight) - Values alignment, professionalism

### 🔐 Security Features
- Multi-tier access control (Viewer, Reviewer, Manager)
- Record-level security rules
- Portal access with secure tokens
- Complete audit logging
- GDPR compliant

### 📈 Assessment Workflow
```
Candidate Submission → AI Scoring → Human Review → Ranking → Export to Recruitment
```

## 🚀 Installation

### Prerequisites
1. Odoo 17 (Community or Enterprise)
2. Python 3.10+
3. Required Python packages:
   ```bash
   pip install openai tiktoken numpy pandas
   ```

### Installation Steps

1. **Copy module to addons directory:**
   ```bash
   cp -r scholarix_assessment /path/to/odoo/addons/
   ```

2. **Update Apps List:**
   - Go to Odoo → Apps → Update Apps List

3. **Install Module:**
   - Search for "SCHOLARIX Assessment System"
   - Click Install

4. **Configure OpenAI API (Optional):**
   - Go to Settings → Technical → System Parameters
   - Create new parameter:
     - Key: `scholarix_assessment.openai_api_key`
     - Value: `your-openai-api-key`
   - If not configured, module will use mock AI scoring for testing

5. **Assign User Groups:**
   - Settings → Users & Companies → Users
   - Edit user → Assessment System tab
   - Assign appropriate group (Viewer/Reviewer/Manager)

## 📖 Usage Guide

### For Candidates

1. **Access Assessment:**
   - Visit: `https://your-domain.com/assessment`
   - Fill in personal details
   - Answer 10 assessment questions (minimum 50 characters each)
   - Submit assessment

2. **View Results:**
   - Check email for confirmation and access token link
   - View AI scores and analysis
   - Final results available after human review (3-5 business days)

### For Reviewers

1. **Review Dashboard:**
   - Access: Apps → Assessment → Candidates
   - View list of submitted assessments
   - Filter by status, score, date, etc.

2. **Review Candidate:**
   - Open candidate record
   - Review responses and AI analysis
   - Click "Human Review" button
   - Adjust scores if needed
   - Add reviewer notes and recommendation
   - Submit review

3. **View Rankings:**
   - Apps → Assessment → Rankings
   - View leaderboard by category
   - Export top candidates

### For Managers

1. **Analytics Dashboard:**
   - Apps → Assessment → Dashboard
   - View statistics:
     - Total submissions
     - Average scores
     - Score distribution
     - Submission trends
     - Common skill gaps

2. **Export Data:**
   - Select candidates
   - Action → Export
   - Choose format (CSV, Excel, PDF)
   - Apply filters

3. **Configuration:**
   - Manage assessment questions
   - Configure scoring weights
   - Set up email templates
   - Configure automation rules

## 🔧 Configuration

### Assessment Questions

Edit questions via: Apps → Assessment → Configuration → Questions

Default 10 questions cover:
1. Automation Experience
2. AI Tools Usage
3. Client Communication
4. Project Estimation
5. Learning New Technologies
6. Objection Handling
7. Difficult Client Management
8. Technical Simplification
9. Setting Professional Boundaries
10. Motivation & Concerns

### Email Templates

Customize at: Settings → Technical → Email → Templates

Templates included:
- Assessment Submission Confirmation
- AI Scoring Complete
- Human Review Request
- Shortlist Notification
- Rejection Notification

### Scoring Configuration

#### AI Scoring Weights (hardcoded, can be customized in code):
- Technical: 25%
- Sales: 25%
- Communication: 20%
- Learning: 15%
- Cultural Fit: 15%

#### Per-Question Scoring Criteria:
Configured in `assessment.question` model with detailed scoring criteria for AI.

### Automation Rules

#### Cron Jobs:
1. **Daily Rankings Update** - Regenerate rankings at midnight
2. **Pending Review Reminders** - Email reviewers about pending assessments
3. **Cleanup Old Drafts** - Remove abandoned assessments after 30 days

Configure at: Settings → Technical → Automation → Scheduled Actions

## 📊 API Documentation

### Public Endpoints

#### Submit Assessment
```bash
POST /assessment/submit
Content-Type: application/json

{
  "candidate": {
    "candidateName": "John Doe",
    "candidateEmail": "john@example.com",
    "candidatePhone": "+1234567890",
    "candidateLocation": "Dubai, UAE",
    "odooExperience": "2-5",
    "salesExperience": "3-5"
  },
  "responses": {
    "q1_answer": "...",
    ...
    "q10_answer": "..."
  },
  "metadata": {
    "timeSpent": {"q1": 120, ...}
  }
}
```

#### Get Questions
```bash
GET /assessment/questions
```

#### Check Email
```bash
POST /assessment/check-email
{"email": "test@example.com"}
```

### Authenticated Endpoints (Require API Key)

#### Get Candidates List
```bash
GET /api/v1/dashboard/candidates?page=1&limit=20&status=ai_scored
Authorization: Bearer <api_key>
```

#### Get Candidate Detail
```bash
GET /api/v1/dashboard/candidate/<id>
Authorization: Bearer <api_key>
```

#### Get Rankings
```bash
GET /api/v1/dashboard/rankings?category=overall&limit=50
Authorization: Bearer <api_key>
```

## 🗄️ Database Models

### Main Models:
- `assessment.candidate` - Candidate information and status
- `assessment.response` - 10 assessment question responses
- `assessment.ai.score` - AI-generated scores and analysis
- `assessment.human.review` - Human reviewer scores and notes
- `assessment.ranking` - Candidate rankings and percentiles
- `assessment.question` - Assessment question configuration
- `assessment.audit.log` - Audit trail and activity log

### Relationships:
```
candidate (1) ←→ (1) response
candidate (1) ←→ (1) ai_score
candidate (1) ←→ (0..1) human_review
candidate (1) ←→ (0..1) ranking
candidate (1) ←→ (n) audit_logs
```

## 🎨 Customization

### Adding New Questions

```python
self.env['assessment.question'].create({
    'name': 'Question 11',
    'sequence': 110,
    'question_text': 'Your question here?',
    'question_type': 'technical',
    'category': 'automation',
    'scoring_weight': 1.0,
    'min_char_count': 50,
    'max_char_count': 1000,
    'is_required': True,
    'is_active': True,
})
```

### Custom Scoring Logic

Edit `assessment_ai_score.py` → `_run_ai_scoring()` method to customize AI scoring logic or integrate different AI providers.

### Custom Reports

Create QWeb reports in `reports/` directory following Odoo's reporting framework.

## 🐛 Troubleshooting

### AI Scoring Fails
- Check OpenAI API key is configured correctly
- Verify internet connectivity
- Check API quota/billing
- Review logs: Settings → Technical → Logging

### Module Installation Errors
- Ensure all dependencies are installed: `pip install openai tiktoken numpy pandas`
- Check Python version: Python 3.10+
- Review Odoo logs for specific errors

### Portal Form Not Loading
- Clear browser cache
- Check website is published
- Verify portal routes in Settings → Technical → Menu Items

### Email Notifications Not Sending
- Configure outgoing mail server: Settings → Technical → Email → Outgoing Mail Servers
- Test email configuration
- Check email template configuration

## 📈 Performance Optimization

### For High Volume:
1. **Enable database indexing** (already configured on key fields)
2. **Use cron jobs** for batch processing
3. **Configure AI rate limiting** to avoid API throttling
4. **Archive old assessments** after 12 months
5. **Use read replicas** for reporting queries

### Recommended Server Specs:
- **< 100 submissions/month:** 2 CPU, 4GB RAM
- **100-500 submissions/month:** 4 CPU, 8GB RAM
- **500+ submissions/month:** 8 CPU, 16GB RAM

## 🔄 Backup & Recovery

### Regular Backups:
```bash
# Database backup
pg_dump odoo_db > assessment_backup_$(date +%Y%m%d).sql

# File backup
tar -czf assessment_files_$(date +%Y%m%d).tar.gz /path/to/odoo/filestore
```

### Disaster Recovery:
1. Restore database from backup
2. Restore filestore
3. Restart Odoo services
4. Verify module functionality

## 📞 Support & Contact

- **Developer:** SCHOLARIX Development Team
- **Website:** https://scholarix.com
- **Documentation:** https://docs.scholarix.com/assessment
- **Support Email:** support@scholarix.com

## 📄 License

LGPL-3 - See LICENSE file for details

## 🎯 Roadmap

### v17.0.2.0.0 (Planned)
- [ ] Video response integration
- [ ] Multi-language support
- [ ] Advanced analytics with ML predictions
- [ ] Mobile app (iOS/Android)
- [ ] Integration with LinkedIn for profile import
- [ ] Automated interview scheduling
- [ ] Candidate comparison tool
- [ ] Custom assessment templates

### v17.0.3.0.0 (Future)
- [ ] Real-time collaborative review
- [ ] AI-powered video analysis
- [ ] Skill gap training recommendations
- [ ] Integration with HR training platforms
- [ ] Advanced reporting with Power BI/Tableau
- [ ] White-label customization options

## 🙏 Acknowledgments

Built with ❤️ by the SCHOLARIX team for the Odoo community.

Special thanks to:
- OpenAI for GPT-4 API
- Odoo SA for the amazing framework
- All contributors and beta testers

---

**Version:** 17.0.1.0.0  
**Last Updated:** 2025-11-14  
**Odoo Version:** 17.0  
**Status:** Production Ready ✅
