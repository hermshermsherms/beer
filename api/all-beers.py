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
                self.send_error(500, "Supabase configuration missing")
                return
            
            # Initialize Supabase client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            try:
                # Get all beers - we'll get user names separately since we can't join auth.users
                response = supabase.table("beers").select(
                    "id, image_url, note, created_at, user_id"
                ).order("created_at", desc=True).execute()
                
                # Get user names from auth.users for each beer
                beers = []
                for beer in response.data:
                    user_name = "Unknown User"
                    
                    try:
                        # Try to get user info from auth.users
                        user_response = supabase.auth.admin.get_user_by_id(beer["user_id"])
                        if user_response.user and user_response.user.user_metadata:
                            user_name = user_response.user.user_metadata.get("name", "Unknown User")
                    except:
                        # If we can't get user info, keep default
                        pass
                    
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
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()