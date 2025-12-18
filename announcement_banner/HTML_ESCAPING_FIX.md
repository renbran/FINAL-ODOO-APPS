# HTML Escaping Fix - Announcement Banner

## Issue Description

The announcement banner was displaying HTML code as plain text instead of rendering it properly. For example:

**Before:**
```
<p style="margin: 0px 0px 16px; box-sizing: border-box; line-height: inherit; font-weight: 400; font-size: 14px;">The only way to do great work is to love what you do." - Steve Jobs</p>
```

**After:**
```
The only way to do great work is to love what you do." - Steve Jobs
```

## Root Cause

The HTML content from the `fields.Html` field was being double-escaped during the process:
1. Content stored in database with proper HTML tags
2. When retrieved via RPC, sometimes HTML entities were escaped (`<` became `&lt;`)
3. The frontend tried to render escaped HTML, showing the code instead of formatted content

## Solution Applied

### 1. Updated `process_message_content()` Method

Added HTML unescaping logic to handle cases where content comes pre-escaped:

```python
def process_message_content(self, message):
    """Process and clean HTML message content for proper display"""
    if not message:
        return ''
    
    # Get the HTML string - handle both Markup objects and regular strings
    if isinstance(message, Markup):
        html_content = str(message)
    elif hasattr(message, '__html__'):
        html_content = message.__html__()
    else:
        html_content = str(message)
    
    # Check if content is escaped and unescape it
    if '&lt;' in html_content or '&gt;' in html_content or '&amp;' in html_content:
        html_content = html.unescape(html_content)
    
    # ... rest of processing ...
    
    return html_content
```

### 2. Import Required Module

Added `html` module for unescaping:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
from odoo.tools import html_escape, html_sanitize
import re
import html  # NEW: For HTML unescaping
```

### 3. Removed Markup Return

Changed return type from `Markup(html_content)` to just `html_content` to avoid serialization issues with JSON RPC.

## How It Works

1. **Detection**: Checks if HTML content contains escaped entities (`&lt;`, `&gt;`, `&amp;`)
2. **Unescaping**: Uses `html.unescape()` to convert entities back to proper HTML tags
3. **Processing**: Continues with adding responsive classes to images and tables
4. **Return**: Returns clean HTML string that will be properly serialized by Odoo's RPC

## Testing

### Test Case 1: Simple Text with HTML Tags
```html
<p>This is a <strong>bold</strong> announcement.</p>
```
**Expected**: "This is a **bold** announcement." (with bold formatting)

### Test Case 2: Styled Content
```html
<p style="color: red; font-size: 16px;">Important message</p>
```
**Expected**: Red, 16px text saying "Important message"

### Test Case 3: Image
```html
<img src="/web/image/123" alt="Test"/>
```
**Expected**: Image displayed (not HTML code)

### Test Case 4: Complex Content
```html
<h2>Heading</h2>
<p>Paragraph with <em>italic</em> and <strong>bold</strong>.</p>
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
</ul>
```
**Expected**: Properly formatted heading, paragraph, and list

## Deployment

### Quick Deploy
```bash
cd announcement_banner
./deploy_content_fix.sh
```

### Manual Steps
```bash
# 1. Clean cache
bash clean_cache.sh

# 2. Restart Odoo
docker-compose restart odoo

# 3. Update module
docker-compose exec odoo odoo --update=announcement_banner --stop-after-init

# 4. Start service
docker-compose up -d odoo

# 5. Test
# - Create announcement with HTML content
# - Save and view it
# - Verify HTML renders correctly
```

## Verification Steps

1. **Create Test Announcement**:
   - Go to Settings → Announcements → Announcements
   - Click "New"
   - Enter title: "HTML Test"
   - In message field, add formatted text:
     - Type some text
     - Make some text **bold**
     - Make some text *italic*
     - Add a heading using the toolbar
     - Add a bulleted list
   - Save

2. **View Announcement**:
   - Log out and log back in
   - Check if announcement appears
   - Verify formatting is correct (not HTML code)
   - Check bold, italic, headings display properly

3. **Check Browser Console**:
   - Open DevTools (F12)
   - Look for any JavaScript errors
   - Check Network tab for RPC response
   - Verify message content is proper HTML

## Troubleshooting

### Still Seeing HTML Code?

**Check 1: Field Type**
```python
# Verify in models/announcement_banner.py:
message = fields.Html(
    'Message', 
    required=True, 
    sanitize=False,  # MUST be False
    strip_style=False,  # MUST be False
    strip_classes=False,  # MUST be False
)
```

**Check 2: Template Rendering**
```xml
<!-- Verify in static/src/xml/announcement_banner.xml: -->
<div class="announcement-content" t-raw="currentAnnouncement.message"/>
<!-- MUST use t-raw, NOT t-esc -->
```

**Check 3: Browser Cache**
- Clear browser cache completely
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

**Check 4: Database Content**
```sql
-- Check what's actually stored:
SELECT id, name, message FROM announcement_banner LIMIT 1;
-- If message column shows &lt; instead of <, there's a database issue
```

### Escaped Content in Database?

If the database itself has escaped HTML, you need to fix the data:

```python
# Run in Odoo shell or create a script:
announcements = env['announcement.banner'].search([])
for announcement in announcements:
    if '&lt;' in announcement.message:
        announcement.message = html.unescape(announcement.message)
```

## Related Files Modified

- `models/announcement_banner.py` - Added HTML unescaping logic
- `CONTENT_FIX_SUMMARY.md` - Updated with escaping fix info
- `CHANGELOG.md` - Added v1.2.1 entry

## Version History

- **v1.2.0**: Initial content display improvements
- **v1.2.1**: Fixed HTML escaping issue (this fix)

## Security Note

The module uses `sanitize=False` for the HTML field because:
1. Only administrators can create announcements
2. We need full HTML support for rich formatting
3. Content is trusted (internal use)
4. XSS risk is minimal since only admins have access

If you need sanitization, change `sanitize=False` to `sanitize=True`, but this will strip some HTML features.

---

**Fix Applied**: November 13, 2025  
**Version**: 1.2.1  
**Status**: Production Ready  
**Risk Level**: Low (Logic fix only)
