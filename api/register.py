from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            
            if not all([email, password, name]):
                self.send_error(400, "Missing required fields")
                return
            
            # Store user directly in Supabase users table
            try:
                import uuid
                import hashlib
                
                # Generate user ID and hash password
                user_id = str(uuid.uuid4())
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Insert into users table
                user_data = {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "password_hash": password_hash
                }
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/users",
                    json=user_data,
                    headers={
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                        'Prefer': 'return=representation'
                    }
                )
                
                if response.status_code != 201:
                    raise Exception(f"Supabase error: {response.text}")
                
                result_data = response.json()
                    
                result = {
                    "message": "User registered successfully",
                    "user_id": user_id,
                    "access_token": f"token_{user_id}"
                }
                    
            except Exception as e:
                print(f"Registration failed: {e}")
                self.send_error(400, f"Registration failed: {str(e)}")
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()