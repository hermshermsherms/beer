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
            # Get all beers with user data
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/beers?select=user_id,created_at,users(name)",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                beers_data = json.loads(response.read().decode('utf-8'))
            
            # Process the data to create daily counts
            from collections import defaultdict
            from datetime import datetime
            
            user_daily_counts = defaultdict(lambda: defaultdict(int))
            
            for beer in beers_data:
                user_id = beer.get('user_id', 'unknown')
                created_at = beer['created_at']

                # Extract date from created_at
                # Parse the ISO string and just extract the date part
                if 'T' in created_at:
                    # Split on 'T' to get just the date part before time
                    day_key = created_at.split('T')[0]
                else:
                    # Fallback: parse as datetime and extract date
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    day_key = date.strftime('%Y-%m-%d')

                user_daily_counts[user_id][day_key] += 1
            
            # Get all users to map user_id to names
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
            
            users_map = {user["id"]: user["name"] for user in users_data}
            
            # Get all unique days across all users for complete date range
            all_days = set()
            for daily_counts in user_daily_counts.values():
                all_days.update(daily_counts.keys())
            
            # Convert to frontend format with proper user names
            formatted_data = []
            for user_id, daily_counts in user_daily_counts.items():
                user_name = users_map.get(user_id, f"User {user_id}")
                daily_data = []
                cumulative_total = 0
                
                # Sort all days and create cumulative data (include days with 0 beers)
                for day in sorted(all_days):
                    beers_today = daily_counts.get(day, 0)  # 0 if no beers this day
                    cumulative_total += beers_today
                    daily_data.append({
                        "month": day,  # Keep field name as "month" for frontend compatibility
                        "total_drinks": cumulative_total
                    })
                
                if daily_data:  # Only add users who have data
                    formatted_data.append({
                        "user_name": user_name,
                        "monthly_data": daily_data  # Keep field name for frontend compatibility
                    })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(formatted_data).encode())
                
        except Exception as e:
            print(f"Error fetching leaderboard data: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to fetch leaderboard data: {str(e)}"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()