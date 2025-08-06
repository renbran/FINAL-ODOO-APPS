#!/usr/bin/env python3
"""
JotForm to Odoo Webhook - CloudPepper Lightweight Version
Uses only Python standard library - no external dependencies required.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class JotFormWebhookHandler(BaseHTTPRequestHandler):
    """Handle JotForm webhook requests."""
    
    def do_POST(self):
        """Handle POST requests from JotForm."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the POST data
            post_data = self.rfile.read(content_length)
            
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract form submission data
            raw_request = form_data.get('rawRequest', [''])[0]
            
            if raw_request:
                # Parse the JSON submission data
                submission_data = json.loads(raw_request)
                
                # Log the submission
                logging.info(f"Received JotForm submission: {submission_data.get('formID', 'Unknown')}")
                
                # Process the submission
                result = self.process_jotform_submission(submission_data)
                
                if result:
                    # Success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = json.dumps({"status": "success", "message": "Submission processed"})
                    self.wfile.write(response.encode())
                else:
                    # Error response
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = json.dumps({"status": "error", "message": "Processing failed"})
                    self.wfile.write(response.encode())
            else:
                # No data received
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"status": "error", "message": "No data received"})
                self.wfile.write(response.encode())
                
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "error", "message": str(e)})
            self.wfile.write(response.encode())
    
    def do_GET(self):
        """Handle GET requests - health check."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "status": "healthy",
                "service": "JotForm Webhook",
                "timestamp": datetime.now().isoformat()
            })
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def process_jotform_submission(self, submission_data):
        """Process JotForm submission and send to Odoo."""
        try:
            # Extract form answers
            answers = submission_data.get('rawRequest', {}).get('answers', {})
            
            # Map JotForm fields to Odoo data
            odoo_data = self.map_jotform_to_odoo(answers)
            
            # Send to Odoo
            return self.send_to_odoo(odoo_data)
            
        except Exception as e:
            logging.error(f"Error processing submission: {str(e)}")
            return False
    
    def map_jotform_to_odoo(self, answers):
        """Map JotForm answers to Odoo data structure."""
        # Basic mapping - customize based on your form fields
        mapped_data = {}
        
        for field_id, answer in answers.items():
            if isinstance(answer, dict):
                # Handle complex fields (name, address, etc.)
                if 'first' in answer and 'last' in answer:
                    # Name field
                    mapped_data['name'] = f"{answer.get('first', '')} {answer.get('last', '')}".strip()
                elif 'text' in answer:
                    # Text field
                    mapped_data[f'field_{field_id}'] = answer['text']
            else:
                # Handle simple text fields
                mapped_data[f'field_{field_id}'] = str(answer)
        
        return mapped_data
    
    def send_to_odoo(self, data):
        """Send data to Odoo using standard library urllib."""
        try:
            # Get Odoo configuration from environment
            odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
            odoo_db = os.getenv('ODOO_DB', 'odoo')
            odoo_username = os.getenv('ODOO_USERNAME', 'admin')
            odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
            
            # Prepare authentication
            auth_string = f"{odoo_username}:{odoo_password}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            
            # Prepare the request
            url = f"{odoo_url}/web/dataset/call_kw"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        odoo_db,
                        1,  # user_id - will be replaced after authentication
                        odoo_password,
                        "res.partner",  # model - customize based on your needs
                        "create",
                        [data]
                    ]
                },
                "id": 1
            }
            
            # Convert to JSON
            json_data = json.dumps(payload).encode()
            
            # Create request
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {auth_bytes}'
                }
            )
            
            # Send request
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                
                if 'error' in result:
                    logging.error(f"Odoo error: {result['error']}")
                    return False
                else:
                    logging.info(f"Successfully created record in Odoo: {result.get('result')}")
                    return True
                    
        except Exception as e:
            logging.error(f"Error sending to Odoo: {str(e)}")
            return False

def load_environment():
    """Load environment variables from .env file if it exists."""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")

def main():
    """Main function to start the webhook server."""
    # Load environment variables
    load_environment()
    
    # Get configuration
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('WEBHOOK_PORT', '5000'))
    
    # Start server
    server = HTTPServer((host, port), JotFormWebhookHandler)
    
    print(f"🚀 JotForm Webhook Server starting on {host}:{port}")
    print(f"📍 Health check: http://{host}:{port}/health")
    print("🔗 Configure this URL in your JotForm webhook settings")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down webhook server...")
        server.shutdown()

if __name__ == "__main__":
    main()
