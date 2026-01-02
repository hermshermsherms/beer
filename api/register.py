from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

# Supabase configuration
SUPABASE_URL = "https://rczatkqbmclnuwtanonj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjemF0a3FibWNsbnV3dGFub25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxOTU3ODksImV4cCI6MjA4Mjc3MTc4OX0.jkRHtatdUysh8DoLyjIX0tkEC69aEqPtEDGpJv_qOQE"

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
            
            # Register with Supabase Auth
            try:
                # Sign up user
                auth_data = {
                    "email": email,
                    "password": password,
                    "data": {"name": name}
                }
                
                auth_req = urllib.request.Request(
                    f"{SUPABASE_URL}/auth/v1/signup",
                    data=json.dumps(auth_data).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
                    }
                )
                
                with urllib.request.urlopen(auth_req) as response:
                    auth_result = json.loads(response.read().decode('utf-8'))
                    
                if 'user' in auth_result and auth_result['user']:
                    user_id = auth_result['user']['id']
                    access_token = auth_result['access_token'] if 'access_token' in auth_result else f"supabase_{user_id}"
                    
                    # Insert user profile into users table
                    profile_data = {
                        "id": user_id,
                        "email": email,
                        "name": name
                    }
                    
                    profile_req = urllib.request.Request(
                        f"{SUPABASE_URL}/rest/v1/users",
                        data=json.dumps(profile_data).encode('utf-8'),
                        headers={
                            'Content-Type': 'application/json',
                            'apikey': SUPABASE_ANON_KEY,
                            'Authorization': f'Bearer {access_token}',
                            'Prefer': 'return=representation'
                        }
                    )
                    
                    with urllib.request.urlopen(profile_req) as profile_response:
                        profile_result = json.loads(profile_response.read().decode('utf-8'))
                    
                    result = {
                        "message": "User registered successfully",
                        "user_id": user_id,
                        "access_token": access_token
                    }
                else:
                    self.send_error(400, "Registration failed")
                    return
                    
            except Exception as e:
                print(f"Supabase registration failed: {e}")
                # Fallback to mock
                import hashlib
                user_id = hashlib.md5(email.encode()).hexdigest()[:8]
                token = f"mock_token_{user_id}"
                
                result = {
                    "message": "User registered successfully (mock)",
                    "user_id": user_id,
                    "access_token": token
                }
            
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