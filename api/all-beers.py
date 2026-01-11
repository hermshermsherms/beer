from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get Supabase credentials from environment
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                error_result = {"error": "Supabase configuration missing"}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
                return
            
            # Initialize Supabase client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            try:
                # Get all beers - we'll get user names separately since we can't join auth.users
                response = supabase.table("beers").select(
                    "id, image_url, note, created_at, user_id"
                ).order("created_at", desc=True).execute()
                
                # Get user names using RPC function
                beers = []
                for beer in response.data:
                    user_name = "Unknown User"
                    
                    try:
                        # Use RPC function to get user name from auth metadata
                        user_info = supabase.rpc('get_user_name', {'user_id': beer["user_id"]}).execute()
                        if user_info.data:
                            user_name = user_info.data
                    except Exception as rpc_error:
                        print(f"RPC error for user {beer['user_id']}: {rpc_error}")
                        # Keep default "Unknown User"
                    
                    beers.append({
                        "id": beer["id"],
                        "image_url": beer["image_url"],
                        "note": beer["note"],
                        "created_at": beer["created_at"],
                        "user_id": beer["user_id"],
                        "user_name": user_name
                    })
                
                result = beers
                
            except Exception as e:
                print(f"Database query error: {e}")
                error_result = {"error": f"Failed to fetch beers: {str(e)}"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode())
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
            error_result = {"error": f"Internal server error: {str(e)}"}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()