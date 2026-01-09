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
    def do_POST(self):
        try:
            # Validate authentication
            authorization = self.headers.get('Authorization')
            user_id, supabase = validate_token(authorization)
            
            # For now, let's handle JSON input instead of multipart
            # Parse request body as JSON
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return
                
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Get note from JSON
            note = data.get('note', '').strip()
            if not note:
                error_result = {"error": "Please add a description for your beer"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
                return
                
            if len(note) > 250:
                error_result = {"error": "Description must be 250 characters or less"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
                return
            
            # Use a reliable beer placeholder image
            image_url = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300&h=200&fit=crop&q=80"
            
            # Skip image upload for now - using placeholder
            
            # Insert beer record (using auth.uid() from Supabase JWT)
            try:
                beer_response = supabase.table("beers").insert({
                    "user_id": user_id,
                    "image_url": image_url,
                    "note": note
                }).execute()
                
                if beer_response.data:
                    result = {
                        "message": "Beer posted successfully",
                        "beer_id": beer_response.data[0]["id"]
                    }
                else:
                    raise Exception("Failed to insert beer record")
                
            except Exception as e:
                print(f"Database insert error: {e}")
                self.send_error(400, f"Failed to save beer: {str(e)}")
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()