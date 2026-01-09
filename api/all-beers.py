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
                # Get all beers with user information
                # Note: This works with RLS because we're just reading public beer data
                response = supabase.table("beers").select("""
                    id,
                    image_url,
                    note,
                    created_at,
                    user_id,
                    users!beers_user_id_fkey(name, email)
                """).order("created_at", desc=True).execute()
                
                # Format the response to include user name
                beers = []
                for beer in response.data:
                    user_info = beer.get("users")
                    user_name = "Unknown User"
                    
                    if user_info:
                        # If we have user info from the join
                        user_name = user_info.get("name", "Unknown User")
                    
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