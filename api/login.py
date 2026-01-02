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
            
            # Simple mock authentication - for demo, accept any email/password combo
            # In production this would check against a real database
            if email and password:
                # Generate consistent user ID from email
                import hashlib
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
            self.send_error(401, "Missing email or password")
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()