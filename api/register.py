from http.server import BaseHTTPRequestHandler
import json
import os

# Mock data storage 
users_db = {}
sessions = {}

# Environment variables for Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Try to import Supabase
try:
    from supabase import create_client, Client
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        USE_SUPABASE = True
    else:
        supabase = None
        USE_SUPABASE = False
except ImportError:
    supabase = None
    USE_SUPABASE = False

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
            
            # Try Supabase registration
            if USE_SUPABASE:
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                "email": email,
                                "name": name
                            }
                        }
                    })
                    
                    if response.user:
                        # Insert user profile
                        supabase.table("users").insert({
                            "id": response.user.id,
                            "email": email,
                            "name": name
                        }).execute()
                        
                        user_id = response.user.id
                        token = response.session.access_token if response.session else f"supabase_token_{user_id}"
                        
                        result = {
                            "message": "User registered successfully",
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
                        return
                        
                except Exception as e:
                    print(f"Supabase registration failed: {e}")
                    # Fall through to mock
            
            # Mock fallback
            user_id = f"user_{len(users_db) + 1}"
            users_db[user_id] = {
                "id": user_id,
                "email": email,
                "name": name,
                "password": password
            }
            token = f"mock_token_{user_id}"
            sessions[token] = user_id
            
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