#!/usr/bin/env python3
"""
JotForm to Odoo Contact Webhook Integration
Receives JotForm webhook data and creates/updates contacts in Odoo via REST API
"""

import json
import requests
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Odoo Configuration
ODOO_CONFIG = {
    'url': 'https://testerp.cloudpepper.site',
    'db': 'testerp',
    'username': 'salescompliance@osusproperties.com',
    'password': '8586583'
}

app = Flask(__name__)

class OdooAPI:
    def __init__(self, url, db, username, password):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session_id = None
        
    def authenticate(self):
        """Authenticate with Odoo and get user ID"""
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
            
            response = requests.post(auth_url, json=auth_data, 
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            
            result = response.json()
            if 'error' in result:
                logger.error(f"Authentication error: {result['error']}")
                return False
                
            if result['result'].get('uid'):
                self.uid = result['result']['uid']
                # Extract session ID from cookies
                self.session_id = response.cookies.get('session_id')
                logger.info("Successfully authenticated with Odoo")
                return True
            else:
                logger.error("Authentication failed: No UID returned")
                return False
                
        except Exception as e:
            logger.error(f"Authentication exception: {e}")
            return False
    
    def call_odoo_method(self, model, method, args=None, kwargs=None):
        """Make a call to Odoo's web/dataset/call_kw endpoint"""
        if not self.uid:
            if not self.authenticate():
                return None
        
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
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add session cookie if available
        cookies = {}
        if self.session_id:
            cookies['session_id'] = self.session_id
            
        try:
            response = requests.post(call_url, json=call_data, 
                                   headers=headers, cookies=cookies)
            response.raise_for_status()
            
            result = response.json()
            if 'error' in result:
                logger.error(f"Odoo API error: {result['error']}")
                return None
                
            return result.get('result')
            
        except Exception as e:
            logger.error(f"API call exception: {e}")
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

def map_jotform_to_odoo(form_data):
    """
    Map JotForm submission data to Odoo contact fields
    
    Common JotForm field patterns to map:
    - Name fields: q1_name, q2_fullName, etc.
    - Email fields: q3_email, q4_emailAddress, etc.
    - Phone fields: q5_phone, q6_phoneNumber, etc.
    - Address fields: q7_address, q8_streetAddress, etc.
    - Company fields: q9_company, q10_companyName, etc.
    """
    
    odoo_data = {
        'active': True,
        'customer_rank': 1,  # Mark as customer
    }
    
    # Map form fields to Odoo fields
    for field_key, field_value in form_data.items():
        field_key_lower = field_key.lower()
        
        # Skip empty values
        if not field_value or field_value == '':
            continue
            
        # Name mapping
        if 'name' in field_key_lower:
            if isinstance(field_value, dict):
                # Handle name object {first: "John", last: "Doe"}
                first = field_value.get('first', '')
                last = field_value.get('last', '')
                if first or last:
                    odoo_data['name'] = f"{first} {last}".strip()
            else:
                odoo_data['name'] = str(field_value)
        
        # Email mapping
        elif 'email' in field_key_lower:
            odoo_data['email'] = str(field_value)
        
        # Phone mapping
        elif 'phone' in field_key_lower:
            if 'mobile' in field_key_lower or 'cell' in field_key_lower:
                odoo_data['mobile'] = str(field_value)
            else:
                odoo_data['phone'] = str(field_value)
        
        # Address mapping
        elif 'address' in field_key_lower or 'street' in field_key_lower:
            if isinstance(field_value, dict):
                # Handle address object
                if 'addr_line1' in field_value:
                    odoo_data['street'] = field_value['addr_line1']
                if 'addr_line2' in field_value:
                    odoo_data['street2'] = field_value['addr_line2']
                if 'city' in field_value:
                    odoo_data['city'] = field_value['city']
                if 'state' in field_value:
                    # Note: state_id needs to be looked up in Odoo
                    odoo_data['_state_name'] = field_value['state']  # Store for lookup
                if 'postal' in field_value or 'zip' in field_value:
                    odoo_data['zip'] = field_value.get('postal') or field_value.get('zip')
            else:
                odoo_data['street'] = str(field_value)
        
        # City mapping
        elif 'city' in field_key_lower:
            odoo_data['city'] = str(field_value)
        
        # ZIP/Postal code mapping
        elif 'zip' in field_key_lower or 'postal' in field_key_lower:
            odoo_data['zip'] = str(field_value)
        
        # State mapping
        elif 'state' in field_key_lower:
            odoo_data['_state_name'] = str(field_value)  # Store for lookup
        
        # Country mapping
        elif 'country' in field_key_lower:
            odoo_data['_country_name'] = str(field_value)  # Store for lookup
        
        # Company mapping
        elif 'company' in field_key_lower or 'organization' in field_key_lower:
            odoo_data['company_name'] = str(field_value)
        
        # Job title mapping
        elif 'title' in field_key_lower or 'position' in field_key_lower or 'job' in field_key_lower:
            odoo_data['function'] = str(field_value)
        
        # Website mapping
        elif 'website' in field_key_lower or 'url' in field_key_lower:
            odoo_data['website'] = str(field_value)
        
        # Comments/Message mapping
        elif 'message' in field_key_lower or 'comment' in field_key_lower or 'note' in field_key_lower:
            odoo_data['comment'] = str(field_value)
        
        # VAT/Tax ID mapping
        elif 'vat' in field_key_lower or 'tax' in field_key_lower:
            odoo_data['vat'] = str(field_value)
    
    return odoo_data

def lookup_related_fields(odoo_api, contact_data):
    """
    Lookup related fields like state_id, country_id, etc.
    """
    # Lookup state
    if '_state_name' in contact_data:
        state_name = contact_data.pop('_state_name')
        states = odoo_api.call_odoo_method('res.country.state', 'search_read', 
                                          [['name', 'ilike', state_name]], 
                                          {'fields': ['id', 'name'], 'limit': 1})
        if states:
            contact_data['state_id'] = states[0]['id']
    
    # Lookup country
    if '_country_name' in contact_data:
        country_name = contact_data.pop('_country_name')
        countries = odoo_api.call_odoo_method('res.country', 'search_read', 
                                             [['name', 'ilike', country_name]], 
                                             {'fields': ['id', 'name'], 'limit': 1})
        if countries:
            contact_data['country_id'] = countries[0]['id']
    
    return contact_data

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming JotForm webhook"""
    try:
        # Get the raw request data
        raw_request = request.get_data(as_text=True)
        logger.info(f"Received webhook: {raw_request[:500]}...")  # Log first 500 chars
        
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
                logger.info(f"Parsed form data: {json.dumps(parsed_data, indent=2)}")
            except json.JSONDecodeError:
                logger.error("Failed to parse rawRequest JSON")
                parsed_data = form_data
        else:
            parsed_data = form_data
        
        # Map JotForm data to Odoo format
        odoo_contact_data = map_jotform_to_odoo(parsed_data)
        
        if not odoo_contact_data.get('name') and not odoo_contact_data.get('email'):
            logger.error("No name or email found in form data")
            return jsonify({'error': 'No name or email provided'}), 400
        
        # Initialize Odoo API
        odoo_api = OdooAPI(**ODOO_CONFIG)
        
        # Lookup related fields
        odoo_contact_data = lookup_related_fields(odoo_api, odoo_contact_data)
        
        # Check if contact already exists (by email)
        existing_contact_id = None
        if odoo_contact_data.get('email'):
            existing_contacts = odoo_api.search_contact([['email', '=', odoo_contact_data['email']]])
            if existing_contacts:
                existing_contact_id = existing_contacts[0]
        
        # Create or update contact
        if existing_contact_id:
            # Update existing contact
            result = odoo_api.update_contact(existing_contact_id, odoo_contact_data)
            if result is not None:
                logger.info(f"Updated existing contact ID: {existing_contact_id}")
                return jsonify({
                    'status': 'success',
                    'action': 'updated',
                    'contact_id': existing_contact_id,
                    'submission_id': submission_id
                })
            else:
                logger.error("Failed to update existing contact")
                return jsonify({'error': 'Failed to update contact'}), 500
        else:
            # Create new contact
            contact_id = odoo_api.create_contact(odoo_contact_data)
            if contact_id:
                logger.info(f"Created new contact ID: {contact_id}")
                return jsonify({
                    'status': 'success',
                    'action': 'created',
                    'contact_id': contact_id,
                    'submission_id': submission_id
                })
            else:
                logger.error("Failed to create new contact")
                return jsonify({'error': 'Failed to create contact'}), 500
                
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test_connection():
    """Test endpoint to verify Odoo connection"""
    try:
        odoo_api = OdooAPI(**ODOO_CONFIG)
        if odoo_api.authenticate():
            return jsonify({'status': 'success', 'message': 'Connected to Odoo'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to connect to Odoo'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # For production, use a WSGI server like Gunicorn
    # gunicorn -w 4 -b 0.0.0.0:5000 webhook:app
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)