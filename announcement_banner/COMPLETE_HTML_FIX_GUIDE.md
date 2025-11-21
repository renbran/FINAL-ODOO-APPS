# COMPLETE FIX: HTML Showing as Raw Text

## 🎯 The Real Problem

The HTML editor is working, but your **existing announcement already has escaped HTML stored in the database**. We need to:
1. Fix the display in the popup (use `t-raw` instead of `t-out`)
2. Fix the editor configuration
3. Clean up the existing announcement data

---

## ✅ Step-by-Step Solution

### Step 1: Update Module Files (Already Done ✓)

The following fixes have been applied:
- ✅ XML template now uses `t-raw` to render HTML properly
- ✅ Form view has better HTML editor configuration
- ✅ Model field uses correct sanitization

### Step 2: Apply Changes to Odoo

```bash
# Update the module
docker-compose exec odoo odoo -u announcement_banner -d osusproperties --stop-after-init

# Restart Odoo
docker-compose restart odoo
```

### Step 3: Fix Your Existing Announcement

**Option A: Delete and Recreate (Easiest)**

1. Go to **Announcements** → **Announcements**
2. Open the problematic announcement
3. Click **Delete** (or Archive)
4. Click **Create** new announcement
5. Enter:
   - **Title**: "Welcome Message" (or whatever you want)
   - **Message**: 
     - Type your text normally
     - Select text and use toolbar buttons for formatting
     - Click 📷 for images
     - Click 🔗 for links
6. **Save**
7. **Test**: Log out and log back in

**Option B: Clean the Existing Announcement**

1. Go to **Announcements** → **Announcements**
2. Open the announcement with HTML issues
3. Click **Edit**
4. In the Message field:
   - **Delete ALL the content** (Ctrl + A, then Delete)
   - Start fresh with the toolbar
5. Type your message and use formatting buttons
6. **Save**

### Step 4: Clear Browser Cache

```
Press: Ctrl + Shift + Delete
Select: Cached images and files
Click: Clear data
```

OR simply hard refresh:
```
Press: Ctrl + Shift + R
```

### Step 5: Test the Popup

1. Log out of Odoo
2. Log back in
3. The announcement should now show **properly formatted**! ✅

---

## 🎨 How to Use the Editor Properly

### Creating a New Announcement

1. **Title**: Type a simple title
   ```
   System Update Notice
   ```

2. **Message**: Use the toolbar (NOT manual HTML)
   
   **Example 1 - Simple Text**:
   ```
   Welcome to our new system!
   
   We're excited to have you here.
   ```
   - Select "Welcome" → Click **B** (Bold)
   - Select "new system" → Click **I** (Italic)

   **Example 2 - With Formatting**:
   ```
   Important Announcement
   
   Please note the following:
   • System will be down on Sunday
   • Save your work before 2 AM
   • Contact support if you have questions
   ```
   - Make "Important Announcement" bold and large (use font size)
   - Use bullet list button for the list

   **Example 3 - With Image**:
   - Type your text
   - Click 📷 (Image button)
   - Upload image or paste URL
   - Image appears inline

### What NOT to Do ❌

- ❌ Don't click "Source Code" button (< >)
- ❌ Don't paste HTML code manually
- ❌ Don't copy/paste from Word (paste as plain text first)
- ❌ Don't type HTML tags like `<p>` or `<span>`

### What TO Do ✅

- ✅ Type text normally
- ✅ Use toolbar buttons for formatting
- ✅ Use Bold (B), Italic (I), Underline (U) buttons
- ✅ Use font size dropdown
- ✅ Use list buttons (bullets/numbers)
- ✅ Use image upload button
- ✅ Keep it simple!

---

## 🔧 Quick Fix Command (Alternative)

If you prefer command line, run this in Odoo shell:

```bash
# Enter Odoo shell
docker-compose exec odoo odoo shell -d osusproperties

# Then paste this Python code:
import html
announcements = env['announcement.banner'].search([])
for ann in announcements:
    if ann.message and ('&lt;' in ann.message or '&gt;' in ann.message):
        ann.message = html.unescape(ann.message)
        print(f"Fixed: {ann.name}")
env.cr.commit()
print("Done!")

# Exit
exit()
```

---

## 🧪 Test Checklist

After applying the fix:

- [ ] Clear browser cache (Ctrl + Shift + R)
- [ ] Go to Announcements → Announcements
- [ ] Open or create announcement
- [ ] Message field shows proper editor (not HTML code)
- [ ] Type text and use toolbar buttons
- [ ] Save successfully
- [ ] Log out and log back in
- [ ] Popup shows formatted content (NO HTML code visible)
- [ ] Images display properly
- [ ] Bold/italic text appears formatted

---

## 💡 Example: Creating a Welcome Announcement

### Step-by-Step:

1. **Create New Announcement**
   - Click Create button

2. **Title**:
   ```
   Welcome to the Team!
   ```

3. **Message** (use toolbar):
   - Type: "Hello and welcome!"
   - Select "Hello" → Click **Bold** button
   - Press Enter twice
   - Type: "We're excited to have you join us."
   - Press Enter twice
   - Click **Bullet list** button
   - Type: "Complete your profile"
   - Press Enter
   - Type: "Review the training materials"
   - Press Enter
   - Type: "Meet your team members"
   - Press Enter twice to exit list
   - Press Enter
   - Type: "Have a great day!"
   - Select "great" → Click **Italic** button

4. **Priority**: 10

5. **Save**

6. **Result**: Announcement shows beautifully formatted text! ✅

---

## 🎯 Visual Guide

### WRONG Way (What You're Seeing Now) ❌:
```
<p style="margin: 0px...">
  <span style="box-sizing: border-box...">
    CREATE NOW!
  </span>
</p>
```

### RIGHT Way (What You Should See) ✅:
```
A proper text editor with toolbar:
[B] [I] [U] [Font ▼] [Color ▼] [📷] [🔗]
┌─────────────────────────────────────┐
│ CREATE NOW!                         │
│                                     │
│ Type your message here...           │
│                                     │
└─────────────────────────────────────┘
```

---

## 🆘 Still Showing HTML Code?

### Quick Checklist:

1. **Did you update the module?**
   ```bash
   docker-compose exec odoo odoo -u announcement_banner -d osusproperties --stop-after-init
   docker-compose restart odoo
   ```

2. **Did you clear browser cache?**
   ```
   Ctrl + Shift + R (hard refresh)
   ```

3. **Did you delete the old content?**
   - Open announcement
   - Select ALL (Ctrl + A)
   - Delete
   - Re-enter using toolbar

4. **Are you typing HTML manually?**
   - Don't type `<p>` or `<span>`
   - Use toolbar buttons only

5. **Check browser console**
   - Press F12
   - Look for errors in Console tab

---

## 📞 Summary

**Problem**: HTML code showing instead of formatted text  
**Root Cause**: 
  1. Template using `t-out` instead of `t-raw`
  2. Existing data has escaped HTML
  3. Editor not configured properly

**Solution**:
  1. ✅ Fixed template to use `t-raw`
  2. ✅ Fixed editor configuration
  3. ✅ Delete old content and recreate using toolbar

**Next Steps**:
  1. Update module
  2. Clear browser cache
  3. Delete and recreate announcement
  4. Use toolbar buttons only
  5. Test popup

---

**Status**: ✅ READY TO FIX  
**Time to Fix**: 5 minutes  
**Difficulty**: Easy
