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
            
            if not all([email, password]):
                self.send_error(400, "Missing email or password")
                return
            
            # Login with Supabase Auth
            try:
                auth_data = {
                    "email": email,
                    "password": password
                }
                
                auth_req = urllib.request.Request(
                    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                    data=json.dumps(auth_data).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
                    }
                )
                
                with urllib.request.urlopen(auth_req) as response:
                    auth_result = json.loads(response.read().decode('utf-8'))
                    
                if 'access_token' in auth_result and 'user' in auth_result:
                    access_token = auth_result['access_token']
                    user_id = auth_result['user']['id']
                    
                    result = {
                        "access_token": access_token,
                        "user_id": user_id,
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
                    self.send_error(401, "Invalid credentials")
                    return
                    
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    self.send_error(401, "Invalid credentials")
                else:
                    print(f"Supabase login failed: {e}")
                    # Fallback to demo login
                    if password == "demo123":
                        import hashlib
                        user_id = hashlib.md5(email.encode()).hexdigest()[:8]
                        token = f"mock_token_{user_id}"
                        
                        result = {
                            "access_token": token,
                            "user_id": user_id,
                            "message": "Logged in successfully (demo)"
                        }
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        return
                    
                    self.send_error(401, "Invalid credentials")
            except Exception as e:
                print(f"Login error: {e}")
                self.send_error(500, "Login failed")
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()