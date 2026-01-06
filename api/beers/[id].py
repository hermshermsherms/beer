from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse

# Supabase configuration
import os
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

class handler(BaseHTTPRequestHandler):
    def do_DELETE(self):
        try:
            # Get authorization header
            authorization = self.headers.get('Authorization')
            if not authorization or not authorization.startswith('Bearer '):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
                
            # Extract user ID from token
            token = authorization[7:]  # Remove 'Bearer ' prefix
            if not token.startswith('token_'):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid token format"}).encode())
                return
                
            user_id = token[6:]  # Remove 'token_' prefix
            
            # Get beer ID from URL path
            path_parts = self.path.split('/')
            beer_id = None
            
            # Find beer ID in path - could be /api/beers/{id} or /beers/{id}
            for i, part in enumerate(path_parts):
                if part == 'beers' and i + 1 < len(path_parts):
                    beer_id = path_parts[i + 1]
                    # Remove query parameters if present
                    if '?' in beer_id:
                        beer_id = beer_id.split('?')[0]
                    break
            
            if not beer_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Beer ID is required"}).encode())
                return
            
            # First, verify the beer exists and belongs to the user
            verify_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/beers?id=eq.{beer_id}&user_id=eq.{user_id}",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(verify_req) as response:
                beer_check = json.loads(response.read().decode('utf-8'))
            
            if not beer_check:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Beer not found or access denied"}).encode())
                return
            
            # Delete the beer from Supabase
            delete_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/beers?id=eq.{beer_id}",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                method='DELETE'
            )
            
            print(f"Attempting to delete beer {beer_id} for user {user_id}")
            print(f"Delete URL: {SUPABASE_URL}/rest/v1/beers?id=eq.{beer_id}")
            
            with urllib.request.urlopen(delete_req) as response:
                response_code = response.getcode()
                print(f"Delete response code: {response_code}")
                
                if response_code == 204:
                    print("Delete successful - beer removed")
                else:
                    print(f"Unexpected response code: {response_code}")
            
            # Verify the beer was actually deleted
            verify_deleted_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/beers?id=eq.{beer_id}",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(verify_deleted_req) as response:
                remaining_beers = json.loads(response.read().decode('utf-8'))
                print(f"Verification check - remaining beers with ID {beer_id}: {len(remaining_beers)}")
                
                if len(remaining_beers) > 0:
                    print(f"WARNING: Beer {beer_id} still exists after delete operation!")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Beer deletion failed - item still exists"}).encode())
                    return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Beer deleted successfully"}).encode())
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Supabase HTTP error: {e.code} - {error_body}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Database error: {error_body}"}).encode())
            
        except Exception as e:
            print(f"Error deleting beer: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to delete beer: {str(e)}"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()