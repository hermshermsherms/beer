from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from auth_utils import validate_token

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
                self.send_error(400, "Missing beer_id parameter")
                return
            
            beer_id = query_params['beer_id'][0]
            
            try:
                # First verify the beer belongs to the user
                beer_check = supabase.table("beers").select("id, user_id").eq(
                    "id", beer_id
                ).eq("user_id", user_id).execute()
                
                if not beer_check.data:
                    self.send_error(404, "Beer not found or not owned by user")
                    return
                
                # Delete the beer
                delete_response = supabase.table("beers").delete().eq(
                    "id", beer_id
                ).execute()
                
                result = {"message": "Beer deleted successfully"}
                
            except Exception as e:
                print(f"Database delete error: {e}")
                self.send_error(400, f"Failed to delete beer: {str(e)}")
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
                self.send_error(401, str(e))
            else:
                self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()