from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import uuid
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://rczatkqbmclnuwtanonj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjemF0a3FibWNsbnV3dGFub25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxOTU3ODksImV4cCI6MjA4Mjc3MTc4OX0.jkRHtatdUysh8DoLyjIX0tkEC69aEqPtEDGpJv_qOQE"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get authorization header
            authorization = self.headers.get('Authorization')
            if not authorization or not authorization.startswith('Bearer '):
                result = {"error": "Authentication required"}
                
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            # Extract user ID from token
            token = authorization[7:]  # Remove 'Bearer ' prefix
            if not token.startswith('token_'):
                result = {"error": "Invalid token format"}
                
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            user_id = token[6:]  # Remove 'token_' prefix
            
            # Parse form data (multipart for image upload)
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in content_type:
                # For now, handle as JSON until we implement image upload
                # In real implementation, we'd parse multipart data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # For demo, create a beer post with placeholder image
                note = "Demo beer post"  # Would extract from form data
                
            elif 'application/json' in content_type:
                # Handle JSON data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                note = data.get('note', '')
                
            else:
                result = {"error": "Unsupported content type"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            if not note or len(note.strip()) == 0:
                result = {"error": "Note is required"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Insert beer into Supabase beers table
            try:
                beer_id = str(uuid.uuid4())
                image_url = "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=🍺"  # Placeholder for now
                
                beer_data = {
                    "id": beer_id,
                    "user_id": user_id,
                    "image_url": image_url,
                    "note": note,
                    "created_at": datetime.now().isoformat()
                }
                
                req = urllib.request.Request(
                    f"{SUPABASE_URL}/rest/v1/beers",
                    data=json.dumps(beer_data).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                        'Prefer': 'return=representation'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    result_data = json.loads(response.read().decode('utf-8'))
                
                result = {
                    "message": "Beer posted successfully",
                    "beer_id": beer_id,
                    "image_url": image_url
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            except Exception as e:
                print(f"Database error: {e}")
                result = {"error": "Failed to save beer post"}
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
        except Exception as e:
            result = {"error": f"Internal server error: {str(e)}"}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()