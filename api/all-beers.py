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
    def do_GET(self):
        try:
            # First get all beers
            beers_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/beers?order=created_at.desc",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(beers_req) as response:
                beers_data = json.loads(response.read().decode('utf-8'))
            
            # Then get all users
            users_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/users?select=id,name",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(users_req) as response:
                users_data = json.loads(response.read().decode('utf-8'))
            
            # Create a user lookup map
            users_map = {user["id"]: user["name"] for user in users_data}
            
            # Format the response to match frontend expectations
            formatted_beers = []
            for beer in beers_data:
                formatted_beer = {
                    "id": beer["id"],
                    "user_id": beer["user_id"],
                    "image_url": beer["image_url"],
                    "note": beer["note"],
                    "created_at": beer["created_at"],
                    "user_name": users_map.get(beer["user_id"], "Unknown User")
                }
                formatted_beers.append(formatted_beer)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(formatted_beers).encode())
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Supabase HTTP error: {e.code} - {error_body}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Database error: {error_body}"}).encode())
            
        except Exception as e:
            print(f"Error fetching beers: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to fetch beers: {str(e)}"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()