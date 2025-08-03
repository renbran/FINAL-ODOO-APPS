# Webhook CRM Lead Handler

## Overview

This module provides a comprehensive webhook handler for creating CRM leads from external sources with advanced field mapping capabilities.

## Features

- **Flexible Field Mapping**: Configure how webhook data maps to CRM lead fields
- **Data Transformation**: Built-in transformations (uppercase, lowercase, format, etc.)
- **Multiple Sources**: Support for multiple webhook sources with different mappings
- **Validation**: Field validation and required field checking
- **Logging**: Comprehensive logging for debugging and monitoring
- **REST API**: RESTful endpoints for webhook integration

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Webhook CRM Lead Handler" module

## Configuration

### Setting up Webhook Mappings

1. Go to CRM  Configuration  Webhook Mappings
2. Create a new mapping with:
   - **Mapping Name**: Descriptive name for the mapping
   - **Source Name**: Identifier for the webhook source
   - **Field Mappings**: Map webhook fields to CRM lead fields
   - **Default Values**: Set default values for fields
   - **Transformation Rules**: Custom Python code for complex transformations

### Webhook Endpoints

- **Generic Webhook**: `POST /webhook/crm/lead`
- **Source-specific Webhook**: `POST /webhook/crm/lead/<source_name>`
- **Test Endpoint**: `GET /webhook/test`

### Example Webhook Payload

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "company": "Example Corp",
  "message": "Interested in your services",
  "source": "website_form"
}
```

## Field Mappings

### Available Target Fields

- Lead Name, Contact Name, Email, Phone, Mobile
- Address fields (Street, City, State, ZIP, Country)
- Company information (Company Name, Industry)
- CRM fields (Tags, Source, Medium, Campaign)
- Assignment (Salesperson, Sales Team)
- Priority and Type

### Transformation Types

- **Text Transformations**: uppercase, lowercase, capitalize, strip
- **Data Conversions**: boolean, float, integer
- **Custom Mappings**: JSON-based value mapping
- **String Formatting**: Python string formatting
- **Text Replacement**: Find and replace operations

## Usage Examples

### Basic Webhook Call

```bash
curl -X POST https://your-odoo-domain.com/webhook/crm/lead \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "555-0123",
    "company": "Tech Corp"
  }'
```

### With Source Header

```bash
curl -X POST https://your-odoo-domain.com/webhook/crm/lead \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Source: contact_form" \
  -d '{
    "name": "Mike Johnson",
    "email": "mike@example.com"
  }'
```

## Security

- Webhook endpoints use `auth='none'` for external access
- Internal processing uses `sudo()` with proper validation
- Access control configured for webhook mapping management

## Logging

All webhook activities are logged with appropriate levels:
- INFO: Successful lead creation
- WARNING: Data validation issues
- ERROR: Processing failures

## Troubleshooting

### Common Issues

1. **No mapping found**: Ensure a mapping exists for the source name
2. **Required fields missing**: Check field mappings and validation rules
3. **Transformation errors**: Verify transformation parameters and syntax

### Debug Mode

Enable debug logging to see detailed webhook processing information:

```python
_logger.setLevel(logging.DEBUG)
```

## Extension Points

### Custom Transformations

Add custom transformation types by extending the `_transform_value` method in `WebhookMapping`.

### Special Field Processing

Extend `_process_special_fields` in `CrmLead` for custom field handling.

### Validation Rules

Customize `_validate_required_fields` in `CrmLead` for custom validation logic.

## Support

For issues and feature requests, please contact your system administrator or development team.

## License

This module is licensed under LGPL-3.
