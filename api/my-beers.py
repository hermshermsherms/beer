from http.server import BaseHTTPRequestHandler
import json
import os
import base64
from supabase import create_client, Client

def validate_token(authorization_header):
    """Validate JWT token and return user_id, supabase_client"""
    if not authorization_header or not authorization_header.startswith('Bearer '):
        raise Exception("Missing or invalid authorization header")
    
    token = authorization_header[7:]  # Remove 'Bearer ' prefix
    
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise Exception("Supabase configuration missing")
    
    try:
        # Decode JWT token to get user ID
        parts = token.split('.')
        if len(parts) != 3:
            raise Exception("Invalid JWT format")
        
        # Decode payload
        payload_encoded = parts[1]
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += '=' * padding
            
        payload_bytes = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        user_id = payload.get('sub')
        if not user_id:
            raise Exception("No user ID in token")
        
        # Create authenticated Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        supabase.postgrest.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        
        return user_id, supabase
        
    except Exception as e:
        raise Exception(f"Token validation failed: {str(e)}")

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