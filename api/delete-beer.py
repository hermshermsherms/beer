from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
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
    def do_DELETE(self):
        try:
            # Validate authentication
            authorization = self.headers.get('Authorization')
            user_id, supabase = validate_token(authorization)
            
            # Parse URL to get beer ID
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'beer_id' not in query_params:
                error_result = {"error": "Missing beer_id parameter"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
                return
            
            beer_id = query_params['beer_id'][0]
            
            try:
                # First verify the beer belongs to the user
                beer_check = supabase.table("beers").select("id, user_id").eq(
                    "id", beer_id
                ).eq("user_id", user_id).execute()
                
                if not beer_check.data:
                    error_result = {"error": "Beer not found or not owned by user"}
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                    self.end_headers()
                    self.wfile.write(json.dumps(error_result).encode())
                    return
                
                # Delete the beer
                delete_response = supabase.table("beers").delete().eq(
                    "id", beer_id
                ).execute()
                
                result = {"message": "Beer deleted successfully"}
                
            except Exception as e:
                print(f"Database delete error: {e}")
                error_result = {"error": f"Failed to delete beer: {str(e)}"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            if "Token validation failed" in str(e) or "Invalid token" in str(e):
                error_result = {"error": str(e)}
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
            else:
                error_result = {"error": f"Internal server error: {str(e)}"}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()