# 📢 Announcement Banner - OSUSAPPS

## Production-Ready Announcement System for Odoo 17

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/osusapps/announcement_banner)
[![Odoo](https://img.shields.io/badge/odoo-17.0-brightgreen.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/license-LGPL--3-orange.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![OSUSAPPS](https://img.shields.io/badge/by-OSUSAPPS-001f3f.svg)](https://www.osusapps.com)

## Overview
The **Announcement Banner** module is a professional, production-ready solution for displaying elegant popup announcement banners when users access Odoo. Perfect for communicating important updates, maintenance schedules, new features, or company-wide notifications with **advanced rich HTML content support** including properly formatted text, images, tables, videos, and multimedia.

## Features

### ✨ Key Features
- **Popup Announcement Display**: Announcements appear as elegant modal popups when users log in
- **Enhanced Rich HTML Content**: Support for formatted text, images, tables, videos, links, and advanced HTML styling
- **Proper Content Rendering**: Text, images, and multimedia display correctly with professional formatting
- **Responsive Images**: Images auto-size and center properly on all devices
- **Table Support**: Tables render with proper responsive wrapping and Bootstrap styling
- **Scheduled Announcements**: Set start and end dates for time-sensitive announcements
- **Target Specific Users**: Show announcements to all users or specific user groups
- **Show Once Option**: Choose whether users should see the announcement once or every time
- **Priority System**: Control the order in which multiple announcements are displayed
- **View Tracking**: Track how many times each announcement has been shown
- **Mobile Responsive**: Beautiful UI with optimized content display on all devices
- **Multi-Announcement Support**: Navigate between multiple announcements with prev/next buttons
- **Video & iFrame Support**: Embed YouTube videos, Vimeo, and other iframe content
- **Advanced Typography**: Full support for headings, lists, quotes, code blocks, and text formatting

### 🎯 Use Cases
- System maintenance notifications
- New feature announcements
- Policy updates
- Holiday schedules
- Emergency alerts
- Training reminders
- Company-wide communications

## Installation

### 1. Copy Module to Addons
```bash
# Copy the announcement_banner folder to your Odoo addons directory
cp -r announcement_banner /path/to/odoo/addons/
```

### 2. Update Apps List
- Go to **Apps** menu
- Click **Update Apps List**
- Search for "Announcement Banner"
- Click **Install**

### 3. Configure Permissions
Only users in the **Settings** group (System Administrator) can create and manage announcements.

## Usage

### Creating an Announcement

1. **Navigate to Announcements**
   - Go to **Announcements** → **Announcements** menu

2. **Create New Announcement**
   - Click **Create** button
   - Fill in the following fields:

#### Required Fields
- **Title**: Short, descriptive title for the announcement
- **Message**: Rich HTML content of your announcement

#### Optional Configuration
- **Priority**: Higher numbers display first (default: 10)
- **Active**: Toggle to enable/disable the announcement
- **Show Once Per User**: Check if users should only see this announcement once
- **Start Date**: When the announcement should start showing
- **End Date**: When the announcement should stop showing
- **Target Users**: Leave empty for all users, or select specific users

3. **Save** the announcement

### Managing Announcements

#### View Active Announcements
- All active announcements are shown by default
- Use filters to view archived, upcoming, or expired announcements

#### Edit Announcements
- Click on any announcement to edit
- Update content, dates, or targeting
- Save changes

#### Archive Announcements
- Click the **Archive** button on the form
- Or toggle the **Active** field in the list view

#### View Logs
- Go to **Announcements** → **Announcement Logs**
- See when and to whom announcements were shown

### Best Practices

#### Content Guidelines
- Keep titles short and clear (5-10 words)
- Use bullet points for easy scanning
- Include call-to-action buttons when needed
- Test HTML formatting before publishing

#### Scheduling
- Set start dates for future announcements
- Always set end dates for time-sensitive information
- Use priority to control display order

#### Targeting
- Leave user field empty for company-wide announcements
- Target specific departments or roles for relevant content
- Use "Show Once" for non-recurring information

## Technical Details

### Models

#### `announcement.banner`
Main model for storing announcements

**Fields:**
- `name`: Char - Title of announcement
- `message`: Html - HTML content
- `active`: Boolean - Active status
- `priority`: Integer - Display priority
- `start_date`: Datetime - Start date
- `end_date`: Datetime - End date
- `show_once`: Boolean - Show once flag
- `user_ids`: Many2many - Target users
- `shown_count`: Integer - Display count (computed)

**Methods:**
- `get_active_announcements()`: Returns active announcements for current user
- `mark_as_shown(announcement_id)`: Marks announcement as shown for current user

#### `announcement.banner.log`
Tracks when announcements are shown to users

**Fields:**
- `announcement_id`: Many2one - Related announcement
- `user_id`: Many2one - User who viewed
- `shown_date`: Datetime - When it was shown

### Frontend Components

#### JavaScript (OWL Component)
- File: `static/src/js/announcement_banner.js`
- Loads announcements on webclient start
- Handles navigation between multiple announcements
- Marks announcements as shown

#### XML Template
- File: `static/src/xml/announcement_banner.xml`
- Responsive modal design
- Navigation controls
- Close button

#### CSS Styling
- File: `static/src/css/announcement_banner.css`
- Modern gradient header
- Smooth animations
- Mobile-responsive
- Print-friendly

### Security

#### Access Rights
- **Users**: Can view their own announcement logs
- **System Administrators**: Full access to create, edit, and delete announcements

#### Files
- `security/ir.model.access.csv`: Defines model access rights

## Customization

### Styling
Edit `static/src/css/announcement_banner.css` to customize:
- Colors and gradients
- Font sizes
- Modal dimensions
- Animation effects

### Functionality
Extend the module by:
- Adding more targeting options (groups, companies)
- Implementing read receipts
- Adding dismissal reasons
- Creating announcement templates
- Adding email notifications

### Integration
Integrate with other modules:
- Send announcements via email
- Link to specific menu items or actions
- Create announcements from workflows
- Add announcement widgets to dashboards

## Troubleshooting

### Announcements Not Showing
1. Check if announcement is **Active**
2. Verify **Start Date** is in the past (or empty)
3. Verify **End Date** is in the future (or empty)
4. Check **Target Users** includes current user (or is empty)
5. If **Show Once** is checked, clear the log for the user

### Clear User Logs
```python
# Run in Odoo shell to clear logs for a user
user = env['res.users'].browse(USER_ID)
logs = env['announcement.banner.log'].search([('user_id', '=', user.id)])
logs.unlink()
```

### Reset All Logs
```python
# Run in Odoo shell to clear all logs
env['announcement.banner.log'].search([]).unlink()
```

## Upgrade Notes

### From Version 1.0.0
- No breaking changes
- New features are backward compatible

## Support

For issues, questions, or feature requests:
- Email: support@osusapps.com
- Website: https://www.osusapps.com

## License

LGPL-3

## Credits

**Author**: OSUSAPPS  
**Version**: 17.0.1.0.0  
**Odoo Version**: 17.0  

---

## Changelog

### Version 1.1.0 (2025-11-07) - PRODUCTION READY 🚀
- **PRODUCTION READY**: Comprehensive branding and professional polish
- **FIXED**: Text rendering with proper `word-break: normal` behavior
- **FIXED**: Removed aggressive `word-break: break-all` that was breaking words improperly
- **ENHANCED**: Image display with responsive styling, borders, and shadows
- **IMPROVED**: Footer branding with OSUSAPPS attribution
- **OPTIMIZED**: CSS for better readability and professional appearance
- **ADDED**: Professional SVG module icon with brand colors
- **ADDED**: Comprehensive HTML documentation for Odoo Apps store
- **UPDATED**: Manifest with production-ready metadata and detailed descriptions
- **SECURITY**: Enhanced access controls and validation

### Version 1.0.4 (2025-11-06)
- Fixed: Images and formatted content display properly (not as HTML code)
- Disabled over-aggressive HTML sanitization
- Images inserted via editor show correctly in banner

### Version 1.0.3 (2025-11-05)
- Fixed text overflow for very long strings and URLs
- Added word-break and hyphenation support (later revised in 1.1.0)

### Version 1.0.2 (2025-11-04)
- Enhanced title contrast with bolder fonts and better shadows
- Improved WYSIWYG editor configuration

### Version 1.0.0 (2025-11-01)
- Initial release
- Core announcement functionality
- User targeting
- Scheduling system
- View tracking
- Multi-announcement navigation
- Responsive design

---

## 📞 Contact & Support

**OSUSAPPS - Enterprise Odoo Solutions**

- 🌐 Website: [https://www.osusapps.com](https://www.osusapps.com)
- 📧 Email: [support@osusapps.com](mailto:support@osusapps.com)
- 💼 Enterprise Solutions & Custom Development Available

---

## 🏆 About OSUSAPPS

OSUSAPPS specializes in enterprise-grade Odoo solutions, delivering professional modules and custom development services for businesses worldwide. Our modules are production-tested, secure, and built following Odoo best practices.

**Our Expertise:**
- Custom Odoo Module Development
- Enterprise Integration Solutions
- Odoo Consulting & Implementation
- Production-Ready Applications
- Technical Support & Maintenance

---

*Powered by OSUSAPPS - Building Better Odoo Solutions*
