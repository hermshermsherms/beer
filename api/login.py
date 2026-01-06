from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

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
            
            if not all([email, password]):
                result = {"error": "Email and password are required"}
                
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Check credentials against Supabase users table
            try:
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Query users table for matching email and password
                req = urllib.request.Request(
                    f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}&password_hash=eq.{password_hash}&select=id,email,name",
                    headers={
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    users = json.loads(response.read().decode('utf-8'))
                    
                if users and len(users) > 0:
                    # User found - login successful
                    user = users[0]
                    result = {
                        "access_token": f"token_{user['id']}",
                        "user_id": user['id'],
                        "message": "Logged in successfully"
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
                else:
                    # No user found - invalid credentials
                    result = {"error": "Wrong email or password"}
                    
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
                    
            except Exception as e:
                print(f"Login error: {e}")
                result = {"error": "Wrong email or password"}
                
                self.send_response(401)
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