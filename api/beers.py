from http.server import BaseHTTPRequestHandler
import json
import os
import cgi
from auth_utils import validate_token

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Validate authentication
            authorization = self.headers.get('Authorization')
            user_id, supabase = validate_token(authorization)
            
            # Parse multipart form data (for image upload)
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Content-Type must be multipart/form-data")
                return
            
            # Parse form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                }
            )
            
            # Get note from form
            if 'note' not in form:
                self.send_error(400, "Missing note field")
                return
            
            note = form['note'].value
            if len(note) > 250:
                self.send_error(400, "Note too long (max 250 characters)")
                return
            
            # Get image from form
            if 'image' not in form:
                self.send_error(400, "Missing image field")
                return
            
            image_field = form['image']
            if not image_field.filename:
                self.send_error(400, "No image file provided")
                return
            
            # Upload image to Supabase storage
            try:
                import datetime
                file_ext = image_field.filename.split('.')[-1] if '.' in image_field.filename else 'jpg'
                file_name = f"{user_id}/{datetime.datetime.now().isoformat()}.{file_ext}"
                
                storage_response = supabase.storage.from_("beer-images").upload(
                    file_name, 
                    image_field.file.read()
                )
                
                if storage_response.data:
                    # Get public URL
                    public_url = supabase.storage.from_("beer-images").get_public_url(file_name)
                    image_url = public_url.data.get("publicUrl")
                else:
                    raise Exception(f"Storage upload failed: {storage_response}")
                
            except Exception as e:
                print(f"Image upload error: {e}")
                self.send_error(400, f"Image upload failed: {str(e)}")
                return
            
            # Insert beer record (using auth.uid() from Supabase JWT)
            try:
                beer_response = supabase.table("beers").insert({
                    "user_id": user_id,
                    "image_url": image_url,
                    "note": note
                }).execute()
                
                if beer_response.data:
                    result = {
                        "message": "Beer posted successfully",
                        "beer_id": beer_response.data[0]["id"]
                    }
                else:
                    raise Exception("Failed to insert beer record")
                
            except Exception as e:
                print(f"Database insert error: {e}")
                self.send_error(400, f"Failed to save beer: {str(e)}")
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            if "Token validation failed" in str(e) or "Invalid token" in str(e):
                self.send_error(401, str(e))
            else:
                self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()