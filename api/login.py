from http.server import BaseHTTPRequestHandler
import json
import os

# Mock data storage (shared with register.py in practice this would use a database)
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
            
            if not all([email, password]):
                self.send_error(400, "Missing email or password")
                return
            
            # Try Supabase authentication
            if USE_SUPABASE:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if response.session:
                        user_id = response.user.id
                        token = response.session.access_token
                        
                        result = {
                            "access_token": token,
                            "user_id": user_id,
                            "message": "Logged in with Supabase"
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
                    print(f"Supabase login failed: {e}")
                    # Fall through to mock
            
            # Mock authentication fallback
            for uid, user in users_db.items():
                if user.get("email") == email and user["password"] == password:
                    token = f"mock_token_{uid}"
                    sessions[token] = uid
                    
                    result = {
                        "access_token": token,
                        "user_id": uid,
                        "message": "Logged in with mock data"
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
            
            # Invalid credentials
            self.send_error(401, "Invalid credentials")
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()