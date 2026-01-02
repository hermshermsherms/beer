from http.server import BaseHTTPRequestHandler
import json
import os

# Mock data storage (shared with register.py in practice this would use a database)
users_db = {}
sessions = {}

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
            
            # Simple mock authentication (will add Supabase later)
            for uid, user in users_db.items():
                if user.get("email") == email and user["password"] == password:
                    token = f"mock_token_{uid}"
                    sessions[token] = uid
                    
                    result = {
                        "access_token": token,
                        "user_id": uid,
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