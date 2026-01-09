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
                # Get all beers with their creation dates and user_ids
                beers_response = supabase.table("beers").select(
                    "user_id, created_at"
                ).execute()
                
                # Get user names using RPC function to access auth.users metadata
                user_ids = set(beer["user_id"] for beer in beers_response.data)
                user_names = {}
                
                # Try to get user names via RPC function first
                try:
                    for user_id in user_ids:
                        try:
                            # Call RPC function to get user name from auth metadata
                            user_info = supabase.rpc('get_user_name', {'user_id': user_id}).execute()
                            if user_info.data:
                                user_names[user_id] = user_info.data
                            else:
                                user_names[user_id] = f"User {user_id[:8]}..."
                        except Exception as rpc_error:
                            print(f"RPC error for user {user_id}: {rpc_error}")
                            user_names[user_id] = f"User {user_id[:8]}..."
                except Exception as e:
                    print(f"RPC function not available: {e}")
                    # Fallback to user ID display
                    for user_id in user_ids:
                        user_names[user_id] = f"User {user_id[:8]}..."
                
                # Process the data to create daily counts
                daily_counts = {}
                for beer in beers_response.data:
                    user_id = beer["user_id"]
                    user_name = user_names.get(user_id, f"User {user_id[:8]}...")
                    created_at = beer["created_at"]
                    
                    # Extract year-month-day from created_at
                    if created_at:
                        try:
                            from datetime import datetime
                            # Parse the timestamp and extract day
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            day_key = dt.strftime('%Y-%m-%d')
                            
                            if day_key not in daily_counts:
                                daily_counts[day_key] = {}
                            
                            if user_name not in daily_counts[day_key]:
                                daily_counts[day_key][user_name] = 0
                            
                            daily_counts[day_key][user_name] += 1
                            
                        except Exception as date_error:
                            print(f"Date parsing error: {date_error}")
                            continue
                
                # Format the result to match the expected frontend structure
                # Group by user_name and create daily data arrays with cumulative counts
                user_groups = {}
                for day, users in daily_counts.items():
                    for user_name, count in users.items():
                        if user_name not in user_groups:
                            user_groups[user_name] = []
                        
                        user_groups[user_name].append({
                            "month": day,  # Frontend expects this field name
                            "daily_count": count
                        })
                
                # Convert to expected format with cumulative totals
                result = []
                for user_name, daily_data in user_groups.items():
                    # Sort daily_data by date
                    daily_data.sort(key=lambda x: x["month"])
                    
                    # Calculate cumulative totals
                    cumulative_total = 0
                    monthly_data = []
                    for day_data in daily_data:
                        cumulative_total += day_data["daily_count"]
                        monthly_data.append({
                            "month": day_data["month"],
                            "total_drinks": cumulative_total
                        })
                    
                    result.append({
                        "user_name": user_name,
                        "monthly_data": monthly_data
                    })
                
                # Sort users by total drinks (final cumulative count)
                result.sort(key=lambda x: x["monthly_data"][-1]["total_drinks"] if x["monthly_data"] else 0, reverse=True)
                
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