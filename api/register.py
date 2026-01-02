from http.server import BaseHTTPRequestHandler
import json
import os
import uuid

# Mock data storage 
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
            name = data.get('name')
            
            if not all([email, password, name]):
                self.send_error(400, "Missing required fields")
                return
            
            # Simple mock registration (will add Supabase later)
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
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()