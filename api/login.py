from http.server import BaseHTTPRequestHandler
import json
import os

# Mock data storage - for demo purposes, pre-populate with test user
# In production this would be a real database
users_db = {
    "user_1": {
        "id": "user_1", 
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123"
    }
}
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
            
            # For demo purposes, accept specific test credentials OR any email with password "demo123"
            # In production this would check against a real database
            import hashlib
            
            # Allow test credentials or password "demo123" for any email  
            if (email and password and 
                (password == "demo123" or 
                 (email in users_db and users_db[email].get("password") == password))):
                
                user_id = hashlib.md5(email.encode()).hexdigest()[:8]
                token = f"mock_token_{user_id}"
                
                result = {
                    "access_token": token,
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