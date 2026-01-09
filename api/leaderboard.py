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
                # Get leaderboard data directly instead of using RPC
                # First get all beers with their creation dates and user_ids
                beers_response = supabase.table("beers").select(
                    "user_id, created_at"
                ).execute()
                
                # Get user names from auth.users for each unique user_id
                user_ids = set(beer["user_id"] for beer in beers_response.data)
                user_names = {}
                
                for user_id in user_ids:
                    try:
                        # Get user info from Supabase auth
                        user_response = supabase.auth.admin.get_user_by_id(user_id)
                        if user_response.user and user_response.user.user_metadata:
                            name = user_response.user.user_metadata.get("name", f"User {user_id[:8]}...")
                            user_names[user_id] = name
                        else:
                            user_names[user_id] = f"User {user_id[:8]}..."
                    except Exception as e:
                        print(f"Error getting user {user_id}: {e}")
                        user_names[user_id] = f"User {user_id[:8]}..."
                
                # Process the data to create monthly counts
                monthly_counts = {}
                for beer in beers_response.data:
                    user_id = beer["user_id"]
                    user_name = user_names.get(user_id, f"User {user_id[:8]}...")
                    created_at = beer["created_at"]
                    
                    # Extract year-month from created_at
                    if created_at:
                        try:
                            from datetime import datetime
                            # Parse the timestamp and extract month
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            month_key = dt.strftime('%Y-%m')
                            
                            if month_key not in monthly_counts:
                                monthly_counts[month_key] = {}
                            
                            if user_name not in monthly_counts[month_key]:
                                monthly_counts[month_key][user_name] = 0
                            
                            monthly_counts[month_key][user_name] += 1
                            
                        except Exception as date_error:
                            print(f"Date parsing error: {date_error}")
                            continue
                
                # Format the result to match the expected frontend structure
                # Group by user_name and create monthly_data arrays
                user_groups = {}
                for month, users in monthly_counts.items():
                    for user_name, count in users.items():
                        if user_name not in user_groups:
                            user_groups[user_name] = []
                        
                        user_groups[user_name].append({
                            "month": month,
                            "total_drinks": count
                        })
                
                # Convert to expected format: array of users with monthly_data
                result = []
                for user_name, monthly_data in user_groups.items():
                    # Sort monthly_data by month
                    monthly_data.sort(key=lambda x: x["month"], reverse=True)
                    result.append({
                        "user_name": user_name,
                        "monthly_data": monthly_data
                    })
                
                # Sort users by total drinks (sum of all months)
                result.sort(key=lambda x: sum(m["total_drinks"] for m in x["monthly_data"]), reverse=True)
                
            except Exception as e:
                print(f"Database query error: {e}")
                # Return JSON error instead of HTML
                error_result = {"error": f"Failed to fetch leaderboard: {str(e)}"}
                self.send_response(500)
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
            # Return JSON error instead of HTML
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