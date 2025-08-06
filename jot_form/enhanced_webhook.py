#!/usr/bin/env python3
"""
Enhanced JotForm to Odoo Contact Webhook Integration
With improved error handling, validation, and security features
"""

import json
import requests
import logging
import hashlib
import hmac
import time
from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
ODOO_CONFIG = {
    'url': os.getenv('ODOO_URL', 'https://testerp.cloudpepper.site'),
    'db': os.getenv('ODOO_DB', 'testerp'),
    'username': os.getenv('ODOO_USERNAME', 'salescompliance@osusproperties.com'),
    'password': os.getenv('ODOO_PASSWORD', '8586583')
}

# Security settings
WEBHOOK_SECRET = os.getenv('JOTFORM_WEBHOOK_SECRET', '')  # Optional webhook secret
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))

app = Flask(__name__)

# Rate limiting storage (in production, use Redis)
request_counts = {}

def rate_limit(max_requests=MAX_REQUESTS_PER_MINUTE):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            minute_key = f"{client_ip}:{int(current_time // 60)}"
            
            # Clean old entries
            old_keys = [k for k in request_counts.keys() if int(k.split(':')[1]) < int(current_time // 60) - 1]
            for key in old_keys:
                request_counts.pop(key, None)
            
            # Check current minute requests
            current_requests = request_counts.get(minute_key, 0)
            if current_requests >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            request_counts[minute_key] = current_requests + 1
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_webhook_signature(data, signature):
    """Validate JotForm webhook signature (if configured)"""
    if not WEBHOOK_SECRET:
        return True  # Skip validation if no secret configured
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class OdooAPIError(Exception):
    """Custom Odoo API error"""
    pass

class OdooAPI:
    def __init__(self, url, db, username, password):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session_id = None
        self.last_auth_time = 0
        
    def authenticate(self):
        """Authenticate with Odoo with retry logic"""
        current_time = time.time()
        # Re-authenticate every hour
        if self.uid and current_time - self.last_auth_time < 3600:
            return True
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                auth_url = f"{self.url}/web/session/authenticate"
                auth_data = {
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'db': self.db,
                        'login': self.username,
                        'password': self.password
                    },
                    'id': 1
                }
                
                response = requests.post(
                    auth_url, 
                    json=auth_data, 
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if 'error' in result:
                    raise OdooAPIError(f"Authentication error: {result['error']}")
                    
                if result['result'].get('uid'):
                    self.uid = result['result']['uid']
                    self.session_id = response.cookies.get('session_id')
                    self.last_auth_time = current_time
                    logger.info("Successfully authenticated with Odoo")
                    return True
                else:
                    raise OdooAPIError("Authentication failed: No UID returned")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Authentication timeout, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise OdooAPIError("Authentication timeout after all retries")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Authentication exception: {e}")
                if attempt == max_retries - 1:
                    raise OdooAPIError(f"Authentication failed: {e}")
                time.sleep(2 ** attempt)
                
        return False
    
    def call_odoo_method(self, model, method, args=None, kwargs=None):
        """Make a call to Odoo's API with retry logic"""
        if not self.authenticate():
            raise OdooAPIError("Failed to authenticate")
        
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
            
        call_url = f"{self.url}/web/dataset/call_kw"
        call_data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': model,
                'method': method,
                'args': args,
                'kwargs': kwargs
            },
            'id': 1
        }
        
        headers = {'Content-Type': 'application/json'}
        cookies = {}
        if self.session_id:
            cookies['session_id'] = self.session_id
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    call_url, 
                    json=call_data, 
                    headers=headers, 
                    cookies=cookies,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if 'error' in result:
                    raise OdooAPIError(f"API error: {result['error']}")
                    
                return result.get('result')
                
            except requests.exceptions.Timeout:
                logger.warning(f"API call timeout, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise OdooAPIError("API call timeout after all retries")
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"API call exception: {e}")
                if attempt == max_retries - 1:
                    raise OdooAPIError(f"API call failed: {e}")
                time.sleep(2 ** attempt)
        
        return None
    
    def create_contact(self, contact_data):
        """Create a new contact in Odoo"""
        return self.call_odoo_method('res.partner', 'create', [contact_data])
    
    def update_contact(self, contact_id, contact_data):
        """Update an existing contact in Odoo"""
        return self.call_odoo_method('res.partner', 'write', [[contact_id], contact_data])
    
    def search_contact(self, domain):
        """Search for contacts based on domain criteria"""
        return self.call_odoo_method('res.partner', 'search', [domain])
    
    def read_contact(self, contact_ids, fields=None):
        """Read contact data"""
        if fields is None:
            fields = ['id', 'name', 'email', 'phone', 'mobile']
        return self.call_odoo_method('res.partner', 'read', [contact_ids], {'fields': fields})

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(value):
    """Sanitize input data"""
    if isinstance(value, str):
        # Remove potential XSS and injection attempts
        value = value.strip()
        # Remove any script tags
        value = re.sub(r'<script.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        # Remove any SQL injection attempts
        dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
        for pattern in dangerous_patterns:
            value = value.replace(pattern, '')
    return value

def validate_contact_data(contact_data):
    """Validate contact data before sending to Odoo"""
    errors = []
    
    # Name validation
    if not contact_data.get('name'):
        errors.append("Name is required")
    elif len(contact_data['name']) > 100:
        errors.append("Name too long (max 100 characters)")
    
    # Email validation
    if contact_data.get('email'):
        if not validate_email(contact_data['email']):
            errors.append("Invalid email format")
        elif len(contact_data['email']) > 100:
            errors.append("Email too long (max 100 characters)")
    
    # Phone validation
    for phone_field in ['phone', 'mobile']:
        if contact_data.get(phone_field):
            phone = re.sub(r'[^\d+\-\s\(\)]', '', contact_data[phone_field])
            if len(phone) < 7 or len(phone) > 20:
                errors.append(f"Invalid {phone_field} format")
    
    # Required field check
    if not contact_data.get('name') and not contact_data.get('email'):
        errors.append("Either name or email must be provided")
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return True

def map_jotform_to_odoo(form_data):
    """Enhanced mapping with better field detection and validation"""
    odoo_data = {
        'active': True,
        'customer_rank': 1,
    }
    
    # Track which fields we've mapped
    mapped_fields = set()
    
    for field_key, field_value in form_data.items():
        # Skip system fields
        if field_key in ['submissionID', 'rawRequest']:
            continue
            
        field_key_lower = field_key.lower()
        
        # Skip empty values
        if not field_value or field_value == '':
            continue
            
        # Sanitize input
        if isinstance(field_value, str):
            field_value = sanitize_input(field_value)
        elif isinstance(field_value, dict):
            field_value = {k: sanitize_input(v) if isinstance(v, str) else v 
                         for k, v in field_value.items()}
        
        # Enhanced name mapping
        if any(pattern in field_key_lower for pattern in ['name', 'fullname', 'firstname', 'lastname']):
            if 'name' not in mapped_fields:
                if isinstance(field_value, dict):
                    # Handle structured name object
                    first = field_value.get('first', '').strip()
                    last = field_value.get('last', '').strip()
                    if first or last:
                        odoo_data['name'] = f"{first} {last}".strip()
                        mapped_fields.add('name')
                else:
                    odoo_data['name'] = str(field_value).strip()
                    mapped_fields.add('name')
        
        # Enhanced email mapping
        elif any(pattern in field_key_lower for pattern in ['email', 'mail']):
            if 'email' not in mapped_fields:
                email = str(field_value).strip().lower()
                if validate_email(email):
                    odoo_data['email'] = email
                    mapped_fields.add('email')
        
        # Enhanced phone mapping
        elif any(pattern in field_key_lower for pattern in ['phone', 'tel']):
            phone_clean = re.sub(r'[^\d+\-\s\(\)]', '', str(field_value))
            if 'mobile' in field_key_lower or 'cell' in field_key_lower:
                if 'mobile' not in mapped_fields:
                    odoo_data['mobile'] = phone_clean
                    mapped_fields.add('mobile')
            else:
                if 'phone' not in mapped_fields:
                    odoo_data['phone'] = phone_clean
                    mapped_fields.add('phone')
        
        # Enhanced address mapping
        elif any(pattern in field_key_lower for pattern in ['address', 'street']):
            if isinstance(field_value, dict):
                # Handle structured address
                for addr_key, addr_value in field_value.items():
                    if not addr_value:
                        continue
                    if addr_key in ['addr_line1', 'street']:
                        odoo_data['street'] = str(addr_value)
                    elif addr_key in ['addr_line2', 'street2']:
                        odoo_data['street2'] = str(addr_value)
                    elif addr_key == 'city':
                        odoo_data['city'] = str(addr_value)
                    elif addr_key == 'state':
                        odoo_data['_state_name'] = str(addr_value)
                    elif addr_key in ['postal', 'zip']:
                        odoo_data['zip'] = str(addr_value)
            else:
                if 'street' not in odoo_data:
                    odoo_data['street'] = str(field_value)
        
        # City mapping
        elif 'city' in field_key_lower:
            odoo_data['city'] = str(field_value)
        
        # ZIP/Postal code mapping
        elif any(pattern in field_key_lower for pattern in ['zip', 'postal']):
            odoo_data['zip'] = str(field_value)
        
        # State mapping
        elif 'state' in field_key_lower:
            odoo_data['_state_name'] = str(field_value)
        
        # Country mapping
        elif 'country' in field_key_lower:
            odoo_data['_country_name'] = str(field_value)
        
        # Company mapping
        elif any(pattern in field_key_lower for pattern in ['company', 'organization', 'org']):
            odoo_data['company_name'] = str(field_value)
        
        # Job title mapping
        elif any(pattern in field_key_lower for pattern in ['title', 'position', 'job', 'role']):
            odoo_data['function'] = str(field_value)
        
        # Website mapping
        elif any(pattern in field_key_lower for pattern in ['website', 'url', 'web']):
            website = str(field_value).strip()
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            odoo_data['website'] = website
        
        # Comments/Message mapping
        elif any(pattern in field_key_lower for pattern in ['message', 'comment', 'note', 'description']):
            odoo_data['comment'] = str(field_value)
        
        # VAT/Tax ID mapping
        elif any(pattern in field_key_lower for pattern in ['vat', 'tax']):
            odoo_data['vat'] = str(field_value)
    
    return odoo_data

def lookup_related_fields(odoo_api, contact_data):
    """Enhanced lookup for related fields with error handling"""
    try:
        # Lookup state
        if '_state_name' in contact_data:
            state_name = contact_data.pop('_state_name')
            try:
                states = odoo_api.call_odoo_method(
                    'res.country.state', 
                    'search_read', 
                    [['name', 'ilike', state_name]], 
                    {'fields': ['id', 'name'], 'limit': 1}
                )
                if states:
                    contact_data['state_id'] = states[0]['id']
                    logger.info(f"Mapped state '{state_name}' to ID {states[0]['id']}")
                else:
                    logger.warning(f"State '{state_name}' not found in Odoo")
            except Exception as e:
                logger.error(f"Error looking up state '{state_name}': {e}")
        
        # Lookup country
        if '_country_name' in contact_data:
            country_name = contact_data.pop('_country_name')
            try:
                countries = odoo_api.call_odoo_method(
                    'res.country', 
                    'search_read', 
                    [['name', 'ilike', country_name]], 
                    {'fields': ['id', 'name'], 'limit': 1}
                )
                if countries:
                    contact_data['country_id'] = countries[0]['id']
                    logger.info(f"Mapped country '{country_name}' to ID {countries[0]['id']}")
                else:
                    logger.warning(f"Country '{country_name}' not found in Odoo")
            except Exception as e:
                logger.error(f"Error looking up country '{country_name}': {e}")
        
    except Exception as e:
        logger.error(f"Error in lookup_related_fields: {e}")
    
    return contact_data

@app.route('/webhook', methods=['POST'])
@rate_limit()
def handle_webhook():
    """Enhanced webhook handler with comprehensive error handling"""
    start_time = time.time()
    
    try:
        # Get the raw request data
        raw_request = request.get_data(as_text=True)
        
        # Validate webhook signature if configured
        if WEBHOOK_SECRET:
            signature = request.headers.get('X-JotForm-Signature', '')
            if not validate_webhook_signature(raw_request, signature):
                logger.warning("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        logger.info(f"Received webhook: {raw_request[:500]}...")
        
        # Parse form data
        form_data = request.form.to_dict()
        
        # Get submission ID
        submission_id = form_data.get('submissionID')
        if not submission_id:
            logger.error("No submission ID found")
            return jsonify({'error': 'No submission ID'}), 400
        
        # Parse the rawRequest JSON data
        raw_request_data = form_data.get('rawRequest')
        if raw_request_data:
            try:
                parsed_data = json.loads(raw_request_data)
                logger.info(f"Form submission {submission_id}: {len(parsed_data)} fields")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse rawRequest JSON: {e}")
                parsed_data = form_data
        else:
            parsed_data = form_data
        
        # Map JotForm data to Odoo format
        odoo_contact_data = map_jotform_to_odoo(parsed_data)
        
        # Validate the mapped data
        try:
            validate_contact_data(odoo_contact_data)
        except ValidationError as e:
            logger.error(f"Validation error for submission {submission_id}: {e}")
            return jsonify({'error': f'Validation failed: {e}'}), 400
        
        # Initialize Odoo API
        odoo_api = OdooAPI(**ODOO_CONFIG)
        
        # Lookup related fields
        odoo_contact_data = lookup_related_fields(odoo_api, odoo_contact_data)
        
        # Check if contact already exists (by email)
        existing_contact_id = None
        if odoo_contact_data.get('email'):
            try:
                existing_contacts = odoo_api.search_contact([['email', '=', odoo_contact_data['email']]])
                if existing_contacts:
                    existing_contact_id = existing_contacts[0]
                    logger.info(f"Found existing contact with email {odoo_contact_data['email']}: ID {existing_contact_id}")
            except Exception as e:
                logger.error(f"Error searching for existing contact: {e}")
                # Continue with creation if search fails
        
        # Create or update contact
        try:
            if existing_contact_id:
                # Update existing contact
                result = odoo_api.update_contact(existing_contact_id, odoo_contact_data)
                if result is not None:
                    processing_time = time.time() - start_time
                    logger.info(f"Updated contact ID {existing_contact_id} in {processing_time:.2f}s")
                    return jsonify({
                        'status': 'success',
                        'action': 'updated',
                        'contact_id': existing_contact_id,
                        'submission_id': submission_id,
                        'processing_time': f"{processing_time:.2f}s"
                    })
                else:
                    raise OdooAPIError("Update operation returned None")
            else:
                # Create new contact
                contact_id = odoo_api.create_contact(odoo_contact_data)
                if contact_id:
                    processing_time = time.time() - start_time
                    logger.info(f"Created new contact ID {contact_id} in {processing_time:.2f}s")
                    return jsonify({
                        'status': 'success',
                        'action': 'created',
                        'contact_id': contact_id,
                        'submission_id': submission_id,
                        'processing_time': f"{processing_time:.2f}s"
                    })
                else:
                    raise OdooAPIError("Create operation returned None")
                    
        except OdooAPIError as e:
            logger.error(f"Odoo API error for submission {submission_id}: {e}")
            return jsonify({'error': f'Odoo API error: {e}'}), 500
                
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected webhook processing error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/test', methods=['GET'])
def test_connection():
    """Enhanced test endpoint with detailed diagnostics"""
    try:
        start_time = time.time()
        odoo_api = OdooAPI(**ODOO_CONFIG)
        
        if odoo_api.authenticate():
            # Test a simple API call
            try:
                partners = odoo_api.call_odoo_method('res.partner', 'search', [[]], {'limit': 1})
                connection_time = time.time() - start_time
                
                return jsonify({
                    'status': 'success',
                    'message': 'Connected to Odoo successfully',
                    'odoo_url': ODOO_CONFIG['url'],
                    'database': ODOO_CONFIG['db'],
                    'connection_time': f"{connection_time:.2f}s",
                    'partner_count': len(partners) if partners else 0
                })
            except Exception as e:
                return jsonify({
                    'status': 'partial',
                    'message': 'Authentication successful but API test failed',
                    'error': str(e)
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to authenticate with Odoo',
                'odoo_url': ODOO_CONFIG['url'],
                'database': ODOO_CONFIG['db']
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection test failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get webhook statistics"""
    return jsonify({
        'active_rate_limits': len(request_counts),
        'current_time': datetime.now().isoformat(),
        'max_requests_per_minute': MAX_REQUESTS_PER_MINUTE
    })

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(500)
def internal_error_handler(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Record start time for uptime calculation
    app.start_time = time.time()
    
    # For production, use a WSGI server like Gunicorn
    # gunicorn -w 4 -b 0.0.0.0:5000 enhanced_webhook:app
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting JotForm to Odoo webhook on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Odoo URL: {ODOO_CONFIG['url']}")
    logger.info(f"Rate limit: {MAX_REQUESTS_PER_MINUTE} requests/minute")
    
    app.run(host='0.0.0.0', port=port, debug=debug)