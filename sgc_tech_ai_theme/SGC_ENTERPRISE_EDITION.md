# SGC Tech AI Theme - Enterprise Edition

## Overview

The SGC Tech AI Theme now includes **Enterprise-style sidebar menu** with toggle functionality, matching the look and feel of Odoo Enterprise Edition while maintaining the unique SGC Tech AI branding.

## Features Implemented

### 1. Enterprise-Style Sidebar Menu
- **Toggle Button**: Hamburger icon (☰) in the top-left navbar
- **Persistent State**: Sidebar visibility preference saved in browser localStorage
- **Smooth Animations**: 0.3s transitions for show/hide actions
- **SGC Branding**: Electric cyan, deep navy, and neon green color scheme

### 2. Sidebar Visibility Control
- **Default State**: Visible (160px width) on first load
- **Toggle Functionality**: Click button to show/hide sidebar
- **State Persistence**: Preference remembered across page refreshes and sessions
- **Responsive**: Auto-adjusts on tablet/mobile screens

### 3. Enhanced Navbar
- **Gradient Background**: Horizontal gradient (navy → blue → navy)
- **Electric Cyan Border**: 2px bottom border with glow effect
- **Toggle Button Styling**: Gradient background with hover effects

## File Structure

```
sgc_tech_ai_theme/
├── static/src/
│   ├── webclient/
│   │   ├── sgc_init.js                    # NEW - Initialization script
│   │   ├── navbar/
│   │   │   ├── sgc_navbar.js              # NEW - NavBar toggle patch
│   │   │   ├── sgc_navbar.xml             # NEW - Toggle button template
│   │   │   └── sgc_navbar.scss            # NEW - NavBar styling
│   │   ├── appsbar/
│   │   │   ├── sgc_appsbar.js             # Sidebar component
│   │   │   ├── sgc_appsbar.xml            # Sidebar template
│   │   │   ├── sgc_appsbar.scss           # Sidebar styling
│   │   │   └── sgc_appsbar_variables.scss # Sidebar variables
│   │   ├── menus/
│   │   │   └── app_menu_service.js        # App menu service
│   │   ├── sgc_webclient.js               # WebClient patch
│   │   ├── sgc_webclient.xml              # WebClient template
│   │   └── sgc_webclient.scss             # WebClient styling
│   └── scss/
│       ├── sgc_colors.scss                # Core color variables
│       ├── typography.scss                # Typography styles
│       └── [other theme files]
└── __manifest__.py                         # Version 17.0.1.0.4
```

## Design Specifications

### Colors (SGC Tech AI Palette)
- **Deep Navy**: `#0c1e34` - Primary background
- **Ocean Blue**: `#1e3a8a` - Secondary background
- **Electric Cyan**: `#00FFF0` - Primary accent (text, borders)
- **Neon Green**: `#00FF88` - Secondary accent (hover, active)

### Sidebar Dimensions
- **Large Width**: 160px (desktop, sidebar visible)
- **Small Width**: 50px (tablet, icons only)
- **Hidden**: 0px (mobile or toggled off)

### Animations
- **Transition Duration**: 0.3s
- **Easing Function**: `cubic-bezier(0.4, 0, 0.2, 1)`
- **Toggle Button**: 0.3s ease (all properties)

## Technical Implementation

### 1. Initialization Script (`sgc_init.js`)
**Purpose**: Sets default sidebar visibility on page load  
**Execution**: Prepended to assets (loads first)  
**Key Logic**:
```javascript
if (localStorage.getItem('sgc_sidebar_visible') === null) {
    localStorage.setItem('sgc_sidebar_visible', 'true');
}
```

### 2. NavBar Patch (`sgc_navbar.js`)
**Purpose**: Adds toggle functionality to NavBar component  
**Methods**:
- `setup()`: Initializes sidebar state from localStorage
- `toggleSidebar()`: Switches visibility and saves preference
- `updateSidebarClass()`: Applies body classes for CSS transitions

**localStorage Key**: `sgc_sidebar_visible`  
**Body Classes**:
- `sgc_sidebar_type_large` - Sidebar visible (160px)
- `sgc_sidebar_type_invisible` - Sidebar hidden (0px)

### 3. Toggle Button Template (`sgc_navbar.xml`)
**Position**: Before app switcher button  
**Icon**: Font Awesome bars (`fa-bars`)  
**Event**: `t-on-click="toggleSidebar"`

### 4. Styling (`sgc_navbar.scss`)
**Toggle Button**:
- Gradient background (navy → ocean blue)
- Electric cyan border with glow (box-shadow)
- Hover: Neon green border, enhanced glow, lift effect

**NavBar Enhancement**:
- Horizontal gradient background
- Electric cyan bottom border (2px)
- Subtle shadow for depth

**Body States**:
- `.sgc_sidebar_type_large`: Adds left margin to content area
- `.sgc_sidebar_type_invisible`: Removes margin, hides sidebar

## Responsive Behavior

### Desktop (≥992px)
- Sidebar: 160px width (large)
- Toggle button: Visible
- Content area: Margin-left 160px

### Tablet (768px - 991px)
- Sidebar: 50px width (icons only)
- Toggle button: Visible
- Content area: Margin-left 50px

### Mobile (<768px)
- Sidebar: Hidden completely
- Toggle button: Hidden
- Content area: Full width (margin-left 0)

## User Guide

### How to Use

1. **Toggle Sidebar**:
   - Click the ☰ button in the top-left navbar
   - Sidebar slides in/out with smooth animation

2. **Navigate Apps**:
   - Click app icons/names in the sidebar
   - Active app highlighted with gradient + cyan border
   - Hover shows neon green effect

3. **Persistent State**:
   - Your preference is automatically saved
   - Sidebar remembers visibility across page refreshes
   - State stored in browser localStorage

### Keyboard Shortcuts (Future Enhancement)
- `Alt + S`: Toggle sidebar (can be added if requested)

## Customization Options

### Change Default Visibility
Edit `sgc_init.js`:
```javascript
// Change 'true' to 'false' for hidden by default
localStorage.setItem('sgc_sidebar_visible', 'true');
```

### Adjust Sidebar Width
Edit `sgc_appsbar_variables.scss`:
```scss
$sgc-sidebar-large-width: 160px; // Change to desired width
$sgc-sidebar-small-width: 50px;  // Change icon-only width
```

### Modify Colors
Edit `sgc_appsbar_variables.scss` or `sgc_colors.scss`:
```scss
$sgc-appbar-color: $sgc-electric-cyan;      // Text color
$sgc-appbar-background: $sgc-deep-navy;     // Background color
$sgc-appbar-hover: $sgc-neon-green;         // Hover color
```

### Change Animation Speed
Edit `sgc_navbar.scss`:
```scss
.sgc_apps_sidebar_panel,
.o_action_manager {
    transition: all 0.3s ease; // Change 0.3s to desired duration
}
```

## Troubleshooting

### Toggle Button Not Appearing
**Check**:
1. Clear browser cache and hard refresh (Ctrl+Shift+R)
2. Verify assets compiled: Check Network tab in DevTools
3. Check console for JavaScript errors
4. Confirm module upgrade completed successfully

**Fix**:
```bash
# On server
rm -rf /var/odoo/.local/share/Odoo/filestore/scholarixv2/assets/*
systemctl restart odoo-scholarixv2
```

### Sidebar Not Persisting State
**Check**:
1. Browser localStorage enabled (check browser settings)
2. Console shows "SGC Init" and "SGC NavBar" messages
3. Application → Local Storage → `sgc_sidebar_visible` key exists

**Fix**:
```javascript
// In browser console
localStorage.setItem('sgc_sidebar_visible', 'true');
location.reload();
```

### Styling Not Applied
**Check**:
1. SCSS files compiled correctly (no errors in logs)
2. Asset loading order in manifest is correct
3. Browser DevTools → Elements → Computed styles

**Fix**:
```bash
# Restart Odoo to recompile assets
systemctl restart odoo-scholarixv2
```

### Sidebar Overlapping Content
**Check**:
1. Body class applied correctly (`sgc_sidebar_type_large`)
2. Content area has correct margin-left
3. Browser window width (responsive breakpoints)

**Fix**:
```scss
// Adjust margin in sgc_navbar.scss
body.sgc_sidebar_type_large .o_action_manager {
    margin-left: 160px; // Match sidebar width
}
```

## Version History

### v17.0.1.0.4 (Current)
- ✅ Added Enterprise-style navbar toggle button
- ✅ Implemented persistent sidebar state (localStorage)
- ✅ Created initialization script for default visibility
- ✅ Enhanced navbar with SGC gradient styling
- ✅ Added smooth animations and transitions
- ✅ Responsive behavior for tablet/mobile

### v17.0.1.0.3
- ✅ Adapted MuK appsbar with SGC branding
- ✅ Integrated app menu service
- ✅ Created SGC webclient patch

### v17.0.1.0.2
- ✅ Cleaned MuK residual data
- ✅ Fixed CSS compilation errors

### v17.0.1.0.1
- ✅ Initial SGC Tech AI theme release

## Comparison: Community vs Enterprise Edition

| Feature | Community (Standard) | Enterprise (SGC) |
|---------|---------------------|------------------|
| Sidebar Menu | ❌ No | ✅ Yes (SGC branded) |
| Toggle Button | ❌ No | ✅ Yes (☰ in navbar) |
| Persistent State | ❌ No | ✅ Yes (localStorage) |
| App Icons | ❌ Basic | ✅ Enhanced with glow |
| Hover Effects | ❌ Basic | ✅ Neon green glow |
| Active Indicator | ❌ Basic | ✅ Gradient + border |
| Responsive | ❌ Basic | ✅ Full (3 breakpoints) |
| Animations | ❌ No | ✅ Smooth 0.3s |
| Branding | ❌ Generic | ✅ SGC Tech AI |

## Color Reference Guide

### Primary Colors
```scss
$sgc-deep-navy: #0c1e34;      // Dark background
$sgc-ocean-blue: #1e3a8a;     // Medium background
$sgc-electric-cyan: #00FFF0;  // Primary accent
$sgc-neon-green: #00FF88;     // Secondary accent
```

### Gradients
```scss
// Vertical (sidebar background)
linear-gradient(180deg, #0c1e34, #1e3a8a)

// Horizontal (navbar background)
linear-gradient(90deg, #0c1e34 0%, #1e3a8a 50%, #0c1e34 100%)

// Button (toggle button)
linear-gradient(135deg, #0c1e34 0%, #1e3a8a 100%)

// Active app (highlight)
linear-gradient(135deg, #1e3a8a 0%, #00FFF0 100%)
```

### Shadow Effects
```scss
// Sidebar border glow
box-shadow: 2px 0 10px rgba(0, 255, 240, 0.3)

// Toggle button glow
box-shadow: 0 0 10px rgba(0, 255, 240, 0.3)

// Hover glow (enhanced)
box-shadow: 0 0 20px rgba(0, 255, 136, 0.5)

// Icon glow
filter: drop-shadow(0 0 3px rgba(0, 255, 240, 0.6))
```

## Testing Checklist

### Visual Testing
- [ ] Toggle button appears in top-left navbar
- [ ] Toggle button has SGC gradient styling
- [ ] Sidebar visible by default (160px width)
- [ ] Sidebar has electric cyan text on deep navy background
- [ ] App icons have glow effects
- [ ] Hover shows neon green color
- [ ] Active app has gradient highlight
- [ ] Navbar has horizontal gradient
- [ ] Electric cyan border at bottom of navbar

### Functional Testing
- [ ] Click toggle button hides sidebar
- [ ] Click again shows sidebar
- [ ] Animation is smooth (0.3s)
- [ ] Content area adjusts margin correctly
- [ ] Refresh page preserves state
- [ ] Close browser and reopen preserves state
- [ ] Click app icons navigates correctly
- [ ] Active app indicator updates
- [ ] Hover effects work on all apps

### Responsive Testing
- [ ] Desktop (≥992px): Sidebar 160px, toggle visible
- [ ] Tablet (768-991px): Sidebar 50px, toggle visible
- [ ] Mobile (<768px): Sidebar hidden, toggle hidden
- [ ] Resize window triggers responsive behavior
- [ ] No horizontal scrollbars appear

### Browser Compatibility
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (Chrome, Safari)

### Performance Testing
- [ ] Page load time normal (no degradation)
- [ ] Toggle animation smooth (60fps)
- [ ] No memory leaks (check DevTools)
- [ ] No console errors or warnings
- [ ] Assets load correctly (Network tab)

## Support & Maintenance

### Log Files
- **Odoo Logs**: `/var/odoo/scholarixv2/logs/odoo-server.log`
- **Browser Console**: F12 → Console tab
- **Network Activity**: F12 → Network tab

### Common Commands
```bash
# Restart Odoo service
systemctl restart odoo-scholarixv2

# Check service status
systemctl status odoo-scholarixv2

# Clear asset cache
rm -rf /var/odoo/.local/share/Odoo/filestore/scholarixv2/assets/*

# Upgrade module
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -u sgc_tech_ai_theme
```

### Browser DevTools Commands
```javascript
// Check sidebar state
localStorage.getItem('sgc_sidebar_visible')

// Force show sidebar
localStorage.setItem('sgc_sidebar_visible', 'true');
location.reload();

// Force hide sidebar
localStorage.setItem('sgc_sidebar_visible', 'false');
location.reload();

// Clear all SGC settings
Object.keys(localStorage).forEach(key => {
    if (key.startsWith('sgc_')) localStorage.removeItem(key);
});
```

## Future Enhancements (Optional)

1. **Keyboard Shortcuts**: Add Alt+S to toggle sidebar
2. **Sidebar Resizing**: Drag to resize sidebar width
3. **App Search**: Quick search box in sidebar
4. **Pinned Apps**: Pin favorite apps to top
5. **Custom Grouping**: Group apps by category
6. **Sidebar Themes**: Multiple color schemes
7. **Animation Options**: Slide, fade, or bounce effects
8. **Mobile Swipe**: Swipe gesture to toggle on mobile

---

## Quick Start Guide

1. **Login** to Odoo at https://stagingtry.cloudpepper.site/web/login
2. **Look** for the ☰ toggle button in the top-left navbar
3. **Click** the toggle button to hide/show the sidebar
4. **Navigate** by clicking app icons in the sidebar
5. **Enjoy** the Enterprise-style interface with SGC branding!

**Questions or Issues?** Check the Troubleshooting section or contact the development team.

---

**Version**: 17.0.1.0.4  
**Last Updated**: November 27, 2025  
**Author**: Scholarix Global Consultants  
**License**: LGPL-3
