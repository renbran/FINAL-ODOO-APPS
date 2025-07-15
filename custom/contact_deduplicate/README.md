# Contact Deduplicate Module

## Overview
The Contact Deduplicate module provides advanced tools for identifying and merging duplicate contacts in Odoo 17. It uses intelligent algorithms to detect potential duplicates based on multiple criteria and provides a streamlined workflow for reviewing and merging contacts.

## Features

### 🔍 Intelligent Duplicate Detection
- **Fuzzy matching** for names and addresses using SequenceMatcher
- **Multiple criteria matching**: name, email, phone, VAT, address
- **Configurable similarity thresholds**
- **Weighted scoring system** for accurate duplicate detection

### 🔄 Flexible Merge Options
- **Three merge strategies**:
  - Keep Master Contact Data
  - Merge All Data (intelligent field consolidation)
  - Manual Selection (full control)
- **Preview before merge** to review changes
- **Related records migration** (sales orders, invoices, etc.)

### 📊 Comprehensive Management
- **Duplicate status tracking** (New, Reviewed, Merged, Ignored)
- **Merge history** with detailed change logs
- **Batch operations** for processing multiple contacts
- **User-friendly interface** integrated into contact forms

## Installation

1. Place the module in your Odoo addons directory
2. Update the app list: `Settings > Apps > Update Apps List`
3. Search for "Contact Deduplicate" and install

## Usage

### Finding Duplicates

#### Individual Contact
1. Open any contact form
2. Click the **"Find Duplicates"** button in the header
3. Review the potential duplicates in the "Duplicates" tab

#### Batch Processing
1. Go to `Contact Deduplication > Configuration > Batch Operations`
2. Use the server action "Find All Duplicates" on the contacts list

### Reviewing Duplicates

1. Navigate to `Contact Deduplication > Duplicates`
2. Review the list of potential duplicates
3. Use the action buttons:
   - **Merge**: Open the merge wizard
   - **Ignore**: Mark as false positive
   - **Review**: Mark as reviewed

### Merging Contacts

1. Click **"Merge"** on a duplicate record or use **"Merge Contact"** button on contact form
2. Select contacts to merge
3. Choose merge strategy:
   - **Keep Master**: Preserve master contact data
   - **Merge All**: Intelligently combine data from all contacts
   - **Manual**: Manually select field values
4. Review the merge preview
5. Click **"Merge Contacts"** to complete

## Configuration

### Similarity Thresholds
Configure detection sensitivity via system parameters:

- `contact_deduplicate.similarity_threshold`: Overall similarity threshold (default: 0.7)
- `contact_deduplicate.name_similarity_threshold`: Name matching threshold (default: 0.8)
- `contact_deduplicate.email_similarity_threshold`: Email matching threshold (default: 0.8)
- `contact_deduplicate.address_similarity_threshold`: Address matching threshold (default: 0.8)

### Field Weights
Adjust the importance of different fields:

- `contact_deduplicate.rule_name_exact_weight`: Name field weight (default: 3.0)
- `contact_deduplicate.rule_email_exact_weight`: Email field weight (default: 1.0)
- `contact_deduplicate.rule_phone_exact_weight`: Phone field weight (default: 1.0)
- `contact_deduplicate.rule_vat_exact_weight`: VAT field weight (default: 1.0)

## Technical Details

### Models

#### `contact.duplicate`
Stores potential duplicate relationships with similarity scores and matching fields.

#### `contact.merge.history`
Tracks merge operations with detailed change logs for audit purposes.

#### `contact.merge.wizard`
Transient model for the merge process with multiple merge strategies.

### Key Algorithms

#### Similarity Calculation
- Uses Python's `difflib.SequenceMatcher` for fuzzy string matching
- Implements weighted scoring based on field importance
- Normalizes phone numbers for accurate comparison
- Handles partial matches for addresses and names

#### Related Records Migration
Automatically moves related records to the master contact:
- Sales orders
- Purchase orders
- Invoices
- CRM leads
- Project assignments
- Helpdesk tickets
- Messages and followers

## Security

The module includes appropriate access rights:
- All users can view and manage duplicates
- Merge history is read-only for regular users
- Administrative functions require appropriate permissions

## Dependencies

- `base`: Core Odoo functionality
- `contacts`: Contact management

## Support

For support, customization, or feature requests, please contact the module maintainer.

## License

This module is licensed under LGPL-3.
