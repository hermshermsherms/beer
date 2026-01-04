from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse

# Supabase configuration
SUPABASE_URL = "https://rczatkqbmclnuwtanonj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjemF0a3FibWNsbnV3dGFub25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxOTU3ODksImV4cCI6MjA4Mjc3MTc4OX0.jkRHtatdUysh8DoLyjIX0tkEC69aEqPtEDGpJv_qOQE"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Use the SQL function we created in the database schema
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/rpc/get_monthly_beer_counts",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                monthly_data = json.loads(response.read().decode('utf-8'))
            
            # Transform the data to match the frontend's expected format
            # Group by user and create cumulative totals
            user_data = {}
            
            for row in monthly_data:
                user_name = row["user_name"]
                month = row["month"]
                total_drinks = row["total_drinks"]
                
                if user_name not in user_data:
                    user_data[user_name] = []
                
                user_data[user_name].append({
                    "month": month,
                    "total_drinks": total_drinks
                })
            
            # Convert to the format expected by frontend
            formatted_data = []
            for user_name, monthly_data in user_data.items():
                # Sort by month and calculate cumulative totals
                monthly_data.sort(key=lambda x: x["month"])
                
                cumulative_total = 0
                cumulative_data = []
                for month_data in monthly_data:
                    cumulative_total += month_data["total_drinks"]
                    cumulative_data.append({
                        "month": month_data["month"],
                        "total_drinks": cumulative_total
                    })
                
                formatted_data.append({
                    "user_name": user_name,
                    "monthly_data": cumulative_data
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(formatted_data).encode())
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Supabase HTTP error: {e.code} - {error_body}")
            
            # If the function doesn't exist, fall back to manual query
            try:
                # Manual query to get beer counts by user and month
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
                
                # Process the data to create weekly counts
                from collections import defaultdict
                from datetime import datetime, timedelta
                
                user_weekly_counts = defaultdict(lambda: defaultdict(int))
                
                for beer in beers_data:
                    user_id = beer.get('user_id', 'unknown')
                    created_at = beer['created_at']

                    # Extract week from created_at using ISO week format (Monday as start of week)
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                    # Use ISO week format (year-week)
                    iso_year, iso_week, _ = date.isocalendar()
                    week_key = f"{iso_year}-W{iso_week:02d}"

                    user_weekly_counts[user_id][week_key] += 1
                
                # Get all users from the first query to map user_id to names
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
                
                # Convert to frontend format with proper user names
                formatted_data = []
                for user_id, weekly_counts in user_weekly_counts.items():
                    user_name = users_map.get(user_id, f"User {user_id}")
                    weekly_data = []
                    cumulative_total = 0
                    
                    # Sort weeks and create cumulative data
                    for week in sorted(weekly_counts.keys()):
                        cumulative_total += weekly_counts[week]
                        weekly_data.append({
                            "month": week,  # Keep field name as "month" for frontend compatibility
                            "total_drinks": cumulative_total
                        })
                    
                    if weekly_data:  # Only add users who have data
                        formatted_data.append({
                            "user_name": user_name,
                            "monthly_data": weekly_data  # Keep field name for frontend compatibility
                        })
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(formatted_data).encode())
                
            except Exception as fallback_error:
                print(f"Fallback query also failed: {fallback_error}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Database error: {error_body}"}).encode())
            
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