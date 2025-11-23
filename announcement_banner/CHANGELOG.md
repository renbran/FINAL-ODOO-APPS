# Changelog - Announcement Banner Module

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2025-11-13 - CRITICAL HTML ESCAPING FIX 🔧

### Fixed
- **CRITICAL**: HTML content now renders properly instead of displaying as escaped code
- Fixed issue where HTML tags were shown as text (e.g., `<p style="...">` visible in popup)
- Added automatic HTML unescaping for content that comes pre-escaped from database
- Resolved double-escaping issue during RPC JSON serialization

### Changed
- Updated `process_message_content()` to detect and unescape HTML entities
- Added `html` module import for proper HTML entity handling
- Changed return type from `Markup` to plain string for better JSON compatibility

### Technical Details
- Detects escaped HTML entities (`&lt;`, `&gt;`, `&amp;`)
- Uses `html.unescape()` to convert entities back to proper HTML tags
- Maintains all other processing (responsive classes, table wrapping)
- Ensures proper rendering with `t-raw` in OWL template

---

## [1.2.0] - 2025-11-13 - ENHANCED CONTENT DISPLAY 🎨

### Added
- **NEW**: `process_message_content()` method for intelligent HTML processing
- Enhanced image display with proper centering, sizing, and responsive behavior
- Full table support with responsive wrapping and Bootstrap styling
- Video and iframe embed support with responsive aspect ratios (16:9, 4:3)
- Text alignment support (left, center, right, justify)
- Support for figure elements with captions
- Odoo-specific CSS classes support (`.o_image`, `.o_image_inline`)
- Empty content protection with placeholder message
- Enhanced mobile typography with optimized font sizes

### Fixed
- **CRITICAL**: Message content box now properly displays formatted text and images
- Images now center correctly and resize responsively on all devices
- Tables properly wrap and display on mobile screens
- Content spacing and margins corrected for all block elements
- Proper handling of inline images within text
- Video/iframe elements now display with correct aspect ratios
- Content overflow issues resolved on small screens

### Changed
- Improved `.announcement-content` CSS with better layout control
- Enhanced mobile responsiveness for 768px and 480px breakpoints
- Added `min-height: 150px` to content body for consistent layout
- Changed `overflow-y` from `auto` to `visible` for proper content flow
- Updated heading sizes for better mobile readability
- Version bumped to 17.0.1.2.0

### Technical Details
- Added regex-based HTML processing for automatic class injection
- Tables automatically wrapped in responsive divs
- Images get `img-fluid` class for Bootstrap responsiveness
- Markup objects properly converted to strings before display
- Whitespace cleaning while preserving intentional spacing

### Documentation
- Created `MESSAGE_CONTENT_DISPLAY_FIX.md` - Complete implementation guide
- Created `CONTENT_FIX_SUMMARY.md` - Quick reference guide
- Created `TEST_CONTENT.html` - Comprehensive test content
- Added deployment scripts: `deploy_content_fix.sh` and `deploy_content_fix.bat`

---

## [1.1.0] - 2025-11-07 - PRODUCTION READY 🚀

### Added
- Professional SVG module icon with OSUSAPPS brand colors
- Comprehensive HTML documentation page for Odoo Apps store
- Footer branding with "Powered by OSUSAPPS" attribution
- Enhanced image styling with borders, shadows, and responsive behavior
- Detailed manifest descriptions with emojis and feature highlights
- Production-ready metadata and support information

### Fixed
- **CRITICAL**: Text rendering now uses `word-break: normal` instead of `break-all`
  - Previous version broke words mid-character making text unreadable
  - Now respects natural word boundaries for professional appearance
- Image display in announcement content with proper responsive styling
- CSS optimization for better readability across all device sizes

### Changed
- Updated module name to "Announcement Banner - OSUSAPPS"
- Enhanced version to 17.0.1.1.0 (production release)
- Updated category to "Productivity/Communications"
- Improved CSS branding with OSUSAPPS color scheme
- Optimized manifest description with structured formatting

### Improved
- Overall professional appearance and polish
- Mobile responsive styling
- Documentation clarity and completeness
- Security and validation measures

---

## [1.0.4] - 2025-11-06

### Fixed
- HTML content now displays properly instead of showing raw HTML code
- Images inserted via WYSIWYG editor render correctly in banner
- Formatted text (bold, italic, lists) displays as intended

### Changed
- Disabled over-aggressive HTML sanitization (`sanitize=False`)
- Updated WYSIWYG editor configuration for better content handling

---

## [1.0.3] - 2025-11-05

### Fixed
- Text overflow handling for very long strings and URLs
- Content breaking outside of modal boundaries

### Added
- Word-break support for long text strings
- Automatic hyphenation for better text flow
- CSS overflow handling

### Note
- `word-break: break-all` implementation was too aggressive
- Revised in version 1.1.0 to use `word-break: normal`

---

## [1.0.2] - 2025-11-04

### Improved
- Title readability with bolder fonts (800 weight)
- Text shadow on title for better contrast
- WYSIWYG editor toolbar configuration
- Visual hierarchy in announcement header

### Changed
- Title font size from 20px to 22px
- Added letter spacing for improved legibility

---

## [1.0.1] - 2025-11-03

### Fixed
- Minor CSS compatibility issues
- JavaScript loading order

### Added
- Additional browser compatibility checks

---

## [1.0.0] - 2025-11-01 - Initial Release

### Added
- Core announcement banner functionality
- Popup modal display on user login
- Rich HTML content support with WYSIWYG editor
- Scheduling system with start/end dates
- User targeting capabilities
- "Show once per user" option
- Priority-based announcement ordering
- View tracking and logging system
- Multi-announcement navigation with prev/next buttons
- Mobile responsive design
- Professional gradient styling
- Archive/active status management
- Search and filter capabilities
- Access control via security groups

### Models
- `announcement.banner` - Main announcement model
- `announcement.banner.log` - View tracking log

### Views
- Form view with WYSIWYG HTML editor
- Tree view with toggle controls
- Search view with filters and grouping
- Log tree view for tracking

### Frontend
- OWL component for modern JavaScript framework
- XML template for modal structure
- CSS with gradient styling and animations
- Smooth fade-in and slide-up animations

### Security
- Access rights configuration
- System administrator group restrictions
- User log access controls

---

## Upgrade Path

### From 1.0.x to 1.1.0
- **No database migration required**
- **Backward compatible**
- Simply update the module via Odoo Apps
- Clear browser cache for CSS updates
- All existing announcements will continue working
- Enhanced styling applies automatically

### Steps:
1. Backup your database (recommended)
2. Update module files in addons directory
3. Go to Apps → Update Apps List
4. Find "Announcement Banner" and click "Upgrade"
5. Clear browser cache (Ctrl + Shift + R)
6. Test announcements display correctly

---

## Known Issues

### Resolved
- ✅ HTML code showing instead of formatted content (Fixed in 1.0.4)
- ✅ Words breaking mid-character (Fixed in 1.1.0)
- ✅ Images not displaying properly (Fixed in 1.0.4, Enhanced in 1.1.0)

### Active
- None reported

---

## Roadmap

### Version 1.2.0 (Planned)
- [ ] Email notification integration
- [ ] Announcement templates library
- [ ] Read receipts and acknowledgment tracking
- [ ] Dashboard widget for announcement management
- [ ] Export announcement logs to CSV/Excel
- [ ] Multiple language support for announcements

### Version 1.3.0 (Planned)
- [ ] Announcement categories/tags
- [ ] Group targeting (not just users)
- [ ] Company targeting for multi-company setups
- [ ] Recurring announcements (daily, weekly, monthly)
- [ ] Announcement preview before publishing
- [ ] A/B testing for announcements

---

## Support & Contributing

### Getting Help
- Email: support@osusapps.com
- Website: https://www.osusapps.com
- Documentation: See README.md

### Reporting Issues
When reporting issues, please include:
1. Odoo version
2. Module version
3. Browser and version
4. Steps to reproduce
5. Expected vs actual behavior
6. Screenshots if applicable

### Contributing
We welcome contributions! Please contact us for guidelines.

---

## Credits

**Author**: OSUSAPPS - Enterprise Odoo Solutions
**Maintainer**: OSUSAPPS
**Website**: https://www.osusapps.com
**License**: LGPL-3

---

*Last Updated: November 7, 2025*
