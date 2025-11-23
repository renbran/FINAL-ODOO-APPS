# SCHOLARIX Assessment - Landing Page & Timer Feature

## Overview
This document describes the implementation of the professional landing page, countdown timer, and shareable link features for the SCHOLARIX Assessment module.

## Features Implemented

### 1. 🎯 Landing Page (`/assessment`)
**Location:** `views/portal_assessment_landing.xml`

**Components:**
- **Hero Section**
  - Professional gradient background (purple)
  - Animated floating effect
  - Title: "Prove Your Excellence"
  - Subtitle: AI-Powered Assessment System
  - Key stats display (45 min, 10 questions, AI scoring)
  - Primary CTA button to start assessment

- **What to Expect Section**
  - 4 information cards:
    - Comprehensive evaluation
    - AI-powered analysis
    - Fair & objective scoring
    - Quick turnaround (48-72 hours)

- **Assessment Criteria Section**
  - 6 evaluation criteria with icons:
    1. Technical Expertise (Odoo knowledge)
    2. Sales Capabilities (B2B sales)
    3. Communication Skills (written & verbal)
    4. Problem Solving (analytical thinking)
    5. Learning Agility (adaptability)
    6. Cultural Fit (values alignment)

- **Share Section**
  - "Share this assessment" call-to-action
  - Copy Link button (clipboard functionality)
  - Email Share button (mailto: link)
  - LinkedIn Share button

- **Final CTA Section**
  - Ready to begin prompt
  - Large "Start Assessment" button
  - Estimated time reminder

**Styling:** `static/src/css/assessment_landing.css`
- Modern gradient backgrounds
- Float animation keyframes
- Hover effects with transform/shadow
- Fully responsive (mobile, tablet, desktop)
- Professional color scheme (purple/blue gradient)

---

### 2. ⏱️ Countdown Timer (`/assessment/start`)
**Location:** `views/portal_assessment_templates.xml`

**Features:**
- **Fixed Top Bar**
  - Always visible during assessment
  - Gradient background (purple → changes color based on time)
  - Digital clock display (MM:SS format)
  - Visual progress bar
  - Warning indicator

- **Timer Logic (JavaScript)**
  - Default duration: 45 minutes (configurable via `time_limit` parameter)
  - Automatic start on page load
  - Persistent timer using localStorage (survives page refresh)
  - Real-time countdown every second
  - Tracks total time spent (saved in hidden form field)

- **Visual Warnings**
  - **Normal state (> 10 min):** Purple gradient, white progress bar
  - **10-minute warning:** Orange/yellow gradient, warning icon appears
  - **5-minute warning:** Red gradient, "Time almost up!" message
  - **Alert popups:** At 10 min and 5 min remaining

- **Auto-Submit**
  - When timer reaches 0:00
  - Shows confirmation dialog
  - If user cancels, force-submit after 5 seconds
  - Clears localStorage timer state

- **Page Unload Protection**
  - Browser warning if user tries to leave mid-assessment
  - Only shows if assessment is in progress (not at start/end)

---

### 3. 🔗 Shareable Links

**Landing Page Sharing:**
- **Copy Link Button:** Copies `https://scholarixglobal.com/assessment` to clipboard
- **Email Share:** Opens email client with pre-filled subject and body
- **LinkedIn Share:** Opens LinkedIn share dialog

**Email Invitation Template:**
- Already configured with landing page link in CTA button
- Professional Scholarix Global branding
- Located: `data/mail_template_data.xml`
- CTA URL: `https://scholarixglobal.com/assessment`

---

## Routes Structure

| Route | Controller Method | Template | Purpose |
|-------|------------------|----------|---------|
| `/assessment` | `assessment_landing_page()` | `portal_assessment_landing` | Landing page with info & start button |
| `/assessment/start` | `assessment_form(time_limit=45)` | `portal_assessment_form` | Assessment form with timer |
| `/assessment/submit` | `assessment_submit()` | N/A | Form submission handler |
| `/assessment/view/<token>` | `assessment_view(token)` | `portal_assessment_view` | Results view (private) |

---

## Technical Details

### Timer Implementation

**LocalStorage Schema:**
```json
{
  "startTime": 1735123456789,  // Unix timestamp (ms)
  "timeRemaining": 2700         // Seconds remaining
}
```

**Storage Key:** `scholarix_assessment_timer`

**Functions:**
- `loadTimerState()` - Load saved timer on page load
- `saveTimerState()` - Save every second
- `clearTimerState()` - Clear on submit/timeout
- `updateTimerDisplay()` - Update UI elements
- `timerTick()` - Main countdown loop

**Edge Cases Handled:**
- Page refresh → Timer resumes from saved state
- Browser close/reopen → Timer continues if reopened
- Time expired before page load → Immediate auto-submit
- localStorage error → Falls back to session timer

---

## Styling Classes

### Landing Page CSS Classes
- `.assessment-hero` - Hero section with gradient
- `.hero-title`, `.hero-subtitle` - Typography
- `.stats-container`, `.stat-item` - Stats boxes
- `.expect-cards`, `.expect-card` - What to expect section
- `.criteria-cards`, `.criteria-card` - Assessment criteria
- `.share-section`, `.share-buttons` - Sharing controls
- `.float` - Animated floating effect

### Timer CSS (Inline Styles)
- `#timerBar` - Fixed top bar with gradient
- `#timerMinutes`, `#timerSeconds` - Clock display
- `#timerProgress` - Progress bar fill
- `#timerWarning` - Warning indicator

---

## Configuration

### Timer Duration
**Default:** 45 minutes
**How to Change:**
```python
# In portal.py controller
@http.route('/assessment/start', ...)
def assessment_form(self, time_limit=45, **kwargs):  # Change default here
    ...
```

### Warning Thresholds
**Default:** 10 minutes (yellow), 5 minutes (red)
**How to Change:**
```javascript
// In portal_assessment_templates.xml
const WARNING_THRESHOLD_1 = 10 * 60; // Change here (seconds)
const WARNING_THRESHOLD_2 = 5 * 60;  // Change here (seconds)
```

### Share URLs
**Location:** `views/portal_assessment_landing.xml`
```xml
<!-- Copy Link Button -->
<button onclick="navigator.clipboard.writeText('https://scholarixglobal.com/assessment')">
    Copy Link
</button>

<!-- Email Share -->
<a href="mailto:?subject=...&amp;body=https://scholarixglobal.com/assessment">
    Email
</a>

<!-- LinkedIn Share -->
<a href="https://www.linkedin.com/sharing/share-offsite/?url=https://scholarixglobal.com/assessment">
    LinkedIn
</a>
```

---

## Testing Checklist

### Landing Page
- [ ] Landing page loads at `/assessment`
- [ ] All sections render correctly (hero, stats, criteria, share)
- [ ] "Start Assessment" button redirects to `/assessment/start`
- [ ] Copy link button copies correct URL
- [ ] Email share opens email client with correct content
- [ ] LinkedIn share opens LinkedIn with correct URL
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] Animations play smoothly (float effect, hover states)

### Timer Functionality
- [ ] Timer starts at 45:00 on page load
- [ ] Countdown updates every second
- [ ] Progress bar decreases proportionally
- [ ] Timer state persists on page refresh
- [ ] Alert pops up at 10 minutes remaining
- [ ] Alert pops up at 5 minutes remaining
- [ ] Timer bar turns yellow at 10 min
- [ ] Timer bar turns red at 5 min
- [ ] Auto-submit triggers at 0:00
- [ ] Total time spent is saved in form field
- [ ] Browser warning shows when leaving mid-assessment

### Email Integration
- [ ] Email template has correct landing page link
- [ ] Email renders correctly in Gmail
- [ ] Email renders correctly in Outlook
- [ ] CTA button links to `/assessment`
- [ ] Email subject and body are correct

---

## User Flow

```
1. User receives email invitation
   ↓
2. Clicks "Start Your Assessment" in email
   ↓
3. Lands on /assessment (landing page)
   - Reads about assessment
   - Sees criteria and expectations
   - Can share link with others (optional)
   ↓
4. Clicks "Start Assessment Now" button
   ↓
5. Redirects to /assessment/start (form with timer)
   - Timer starts at 45:00
   - User fills out 10 questions
   - Character counters update in real-time
   - Timer warnings at 10 min and 5 min
   ↓
6. User submits form OR timer expires
   ↓
7. Form submits to /assessment/submit
   ↓
8. Success page or error page
```

---

## Files Modified/Created

### New Files
1. `views/portal_assessment_landing.xml` - Landing page template
2. `static/src/css/assessment_landing.css` - Landing page styles
3. `LANDING_PAGE_TIMER_FEATURE.md` - This documentation

### Modified Files
1. `controllers/portal.py` - Added landing page route, updated form route with timer parameter
2. `views/portal_assessment_templates.xml` - Added timer bar and JavaScript to form template
3. `__manifest__.py` - Added new XML and CSS files to data and assets

### Existing Files (No Changes)
- `data/mail_template_data.xml` - Already had correct landing page link
- All other module files remain unchanged

---

## Deployment Instructions

### 1. Update Module Files
```bash
# Ensure all new files are present:
- views/portal_assessment_landing.xml
- static/src/css/assessment_landing.css

# Ensure modified files are updated:
- controllers/portal.py
- views/portal_assessment_templates.xml
- __manifest__.py
```

### 2. Update Odoo Module
```bash
# Via Docker
docker-compose exec odoo odoo --update=scholarix_assessment --stop-after-init

# Via Odoo UI
Apps > Scholarix Assessment System > Upgrade
```

### 3. Clear Browser Cache
```bash
# Ctrl+Shift+R (hard refresh) or:
Settings > Privacy > Clear browsing data
```

### 4. Test Routes
- Visit: `http://localhost:8069/assessment` (landing page)
- Visit: `http://localhost:8069/assessment/start` (form with timer)
- Submit a test assessment
- Verify email invitation link

### 5. Production Deployment
```bash
# 1. Backup database
pg_dump properties > backup_$(date +%Y%m%d).sql

# 2. Clear cache
bash clean_cache.sh

# 3. Copy to production
scp -r scholarix_assessment/ vultr:/var/odoo/properties/extra-addons/

# 4. Update module on production
ssh vultr "cd /var/odoo/properties && odoo --update=scholarix_assessment --stop-after-init"

# 5. Restart Odoo service
ssh vultr "sudo systemctl restart odoo"

# 6. Monitor logs
ssh vultr "tail -f /var/log/odoo/odoo.log"
```

---

## Troubleshooting

### Landing Page Not Loading
**Issue:** 404 error on `/assessment`
**Solution:** 
- Check `portal.py` has `assessment_landing_page()` method
- Verify `portal_assessment_landing.xml` is in `__manifest__.py` data list
- Update module and clear cache

### Timer Not Starting
**Issue:** Timer shows 45:00 but doesn't count down
**Solution:**
- Check browser console for JavaScript errors
- Verify `portal_assessment_templates.xml` has timer JavaScript
- Clear browser cache (Ctrl+Shift+R)
- Check localStorage is enabled in browser

### Timer Not Persisting on Refresh
**Issue:** Timer resets to 45:00 after page refresh
**Solution:**
- Check browser localStorage is enabled
- Verify `STORAGE_KEY` is consistent
- Check browser console for localStorage errors

### Copy Link Not Working
**Issue:** Copy link button doesn't copy URL
**Solution:**
- Modern browsers only: Check browser supports `navigator.clipboard`
- HTTPS required for clipboard API (localhost exempt)
- Check browser console for security errors

### Auto-Submit Not Triggering
**Issue:** Timer reaches 0:00 but form doesn't submit
**Solution:**
- Check `form` has `id="assessmentForm"`
- Verify JavaScript has `document.getElementById('assessmentForm').submit()`
- Check browser console for errors
- Test manually: Open console and run `document.getElementById('assessmentForm').submit()`

---

## Future Enhancements

### Potential Improvements
1. **Pause/Resume Timer:** Allow candidates to pause for breaks
2. **Multiple Languages:** i18n support for landing page
3. **Video Instructions:** Add intro video on landing page
4. **Progress Indicator:** Show which question user is on
5. **Auto-Save Answers:** Save answers to localStorage every minute
6. **Mobile App Link:** Deep link to mobile app if installed
7. **Analytics Tracking:** Google Analytics events for funnel analysis
8. **A/B Testing:** Test different hero messages and CTAs
9. **Social Proof:** Display recent assessment stats ("1,234 assessed this month")
10. **Countdown Animation:** Visual countdown animation at last 10 seconds

---

## Support & Contact

**Module Maintainer:** SCHOLARIX Development Team  
**Email:** dev@scholarixglobal.com  
**Documentation:** This file and `PRODUCTION_READY_REPORT.md`  
**Version:** 17.0.1.0.0 (Odoo 17)

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Created landing page with hero, stats, criteria, and share sections
- ✅ Implemented 45-minute countdown timer with warnings
- ✅ Added timer persistence with localStorage
- ✅ Added auto-submit on timeout
- ✅ Added shareable link functionality (copy, email, LinkedIn)
- ✅ Updated email invitation template
- ✅ Implemented responsive design for all screen sizes
- ✅ Added page unload protection
- ✅ Created comprehensive documentation

### Future Versions
- 🔄 Add pause/resume functionality
- 🔄 Add auto-save for answers
- 🔄 Add progress indicator
- 🔄 Add analytics tracking
