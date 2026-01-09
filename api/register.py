from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get Supabase credentials from environment
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                self.send_error(500, "Supabase configuration missing")
                return
            
            # Initialize Supabase client
            try:
                supabase: Client = create_client(supabase_url, supabase_key)
            except Exception as client_error:
                print(f"Supabase client creation failed: {client_error}")
                self.send_error(500, f"Supabase connection failed: {str(client_error)}")
                return
            
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
            
            # Use Supabase Auth for registration
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "name": name
                        }
                    }
                })
                
                if response.user and response.session:
                    result = {
                        "message": "User registered successfully",
                        "user_id": response.user.id,
                        "access_token": response.session.access_token
                    }
                else:
                    raise Exception("Registration failed - no user created")
                    
            except Exception as e:
                print(f"Supabase registration error: {e}")
                self.send_error(400, f"Registration failed: {str(e)}")
                return
            
            # Send successful response
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