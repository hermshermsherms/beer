from http.server import BaseHTTPRequestHandler
import json
from auth_utils import validate_token

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Validate authentication
            authorization = self.headers.get('Authorization')
            user_id, supabase = validate_token(authorization)
            
            try:
                # Get user's beers
                response = supabase.table("beers").select(
                    "id, image_url, note, created_at"
                ).eq("user_id", user_id).order("created_at", desc=True).execute()
                
                result = response.data
                
            except Exception as e:
                print(f"Database query error: {e}")
                self.send_error(400, f"Failed to fetch beers: {str(e)}")
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            if "Token validation failed" in str(e) or "Invalid token" in str(e):
                self.send_error(401, str(e))
            else:
                self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()