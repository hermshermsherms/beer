from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import uuid
import base64
import mimetypes
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io

# Supabase configuration
SUPABASE_URL = "https://rczatkqbmclnuwtanonj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjemF0a3FibWNsbnV3dGFub25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxOTU3ODksImV4cCI6MjA4Mjc3MTc4OX0.jkRHtatdUysh8DoLyjIX0tkEC69aEqPtEDGpJv_qOQE"

def parse_multipart_form_data(body, content_type):
    """Parse multipart form data to extract files and form fields"""
    try:
        # Simple multipart parser - in production would use more robust solution
        boundary = content_type.split('boundary=')[1]
        parts = body.split(f'--{boundary}'.encode())
        
        form_data = {}
        files = {}
        
        for part in parts[1:-1]:  # Skip first empty part and last boundary
            if not part.strip():
                continue
                
            # Split headers and content
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue
                
            headers = part[:header_end].decode('utf-8')
            content = part[header_end + 4:]
            
            # Parse Content-Disposition header
            if 'Content-Disposition' in headers:
                if 'filename=' in headers:
                    # This is a file upload
                    name_start = headers.find('name="') + 6
                    name_end = headers.find('"', name_start)
                    field_name = headers[name_start:name_end]
                    
                    filename_start = headers.find('filename="') + 10
                    filename_end = headers.find('"', filename_start)
                    filename = headers[filename_start:filename_end]
                    
                    # Remove trailing CRLF
                    if content.endswith(b'\r\n'):
                        content = content[:-2]
                    
                    files[field_name] = {
                        'filename': filename,
                        'content': content
                    }
                else:
                    # This is a regular form field
                    name_start = headers.find('name="') + 6
                    name_end = headers.find('"', name_start)
                    field_name = headers[name_start:name_end]
                    
                    # Remove trailing CRLF
                    field_value = content.decode('utf-8')
                    if field_value.endswith('\r\n'):
                        field_value = field_value[:-2]
                    
                    form_data[field_name] = field_value
        
        return form_data, files
    except Exception as e:
        print(f"Error parsing multipart data: {e}")
        return {}, {}

def upload_image_to_supabase(image_content, filename, user_id):
    """Upload image to Supabase Storage and return public URL"""
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase Storage
        upload_req = urllib.request.Request(
            f"{SUPABASE_URL}/storage/v1/object/beer-images/{unique_filename}",
            data=image_content,
            headers={
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                'Content-Type': 'application/octet-stream',
                'apikey': SUPABASE_ANON_KEY
            },
            method='POST'
        )
        
        with urllib.request.urlopen(upload_req) as upload_response:
            upload_result = json.loads(upload_response.read().decode('utf-8'))
        
        # Get public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/beer-images/{unique_filename}"
        
        return public_url
        
    except Exception as e:
        print(f"Error uploading image: {e}")
        # Return placeholder if upload fails
        return "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=🍺"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get authorization header
            authorization = self.headers.get('Authorization')
            if not authorization or not authorization.startswith('Bearer '):
                result = {"error": "Authentication required"}
                
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            # Extract user ID from token
            token = authorization[7:]  # Remove 'Bearer ' prefix
            if not token.startswith('token_'):
                result = {"error": "Invalid token format"}
                
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            user_id = token[6:]  # Remove 'token_' prefix
            
            # Parse form data
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            image_url = None
            note = None
            
            if 'multipart/form-data' in content_type:
                # Parse multipart form data
                form_data, files = parse_multipart_form_data(post_data, content_type)
                
                # Extract note from form data
                note = form_data.get('note', '').strip()
                
                # Extract and upload image
                if 'image' in files:
                    image_file = files['image']
                    image_url = upload_image_to_supabase(
                        image_file['content'], 
                        image_file['filename'], 
                        user_id
                    )
                else:
                    result = {"error": "Image file is required"}
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
                    
            elif 'application/json' in content_type:
                # Handle JSON data (fallback)
                data = json.loads(post_data.decode('utf-8'))
                note = data.get('note', '').strip()
                image_url = "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=🍺"  # Placeholder
                
            else:
                result = {"error": "Content type must be multipart/form-data for image upload"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            if not note or len(note) == 0:
                result = {"error": "Note is required"}
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            if not image_url:
                result = {"error": "Image upload failed"}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Insert beer into Supabase beers table
            try:
                beer_id = str(uuid.uuid4())
                
                beer_data = {
                    "id": beer_id,
                    "user_id": user_id,
                    "image_url": image_url,
                    "note": note,
                    "created_at": datetime.now().isoformat()
                }
                
                req = urllib.request.Request(
                    f"{SUPABASE_URL}/rest/v1/beers",
                    data=json.dumps(beer_data).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                        'Prefer': 'return=representation'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    result_data = json.loads(response.read().decode('utf-8'))
                
                result = {
                    "message": "Beer posted successfully",
                    "beer_id": beer_id,
                    "image_url": image_url
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
                
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"Database HTTP error: {e.code} - {error_body}")
                result = {"error": f"Database error: {error_body}"}
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            except Exception as e:
                print(f"Database error: {e}")
                result = {"error": f"Failed to save beer post: {str(e)}"}
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
        except Exception as e:
            result = {"error": f"Internal server error: {str(e)}"}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()