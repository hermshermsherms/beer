import os
import json
import base64
from supabase import create_client, Client

def validate_token(authorization_header):
    """
    Validate Supabase JWT token and return user info
    Returns: (user_id, supabase_client) or raises Exception
    """
    if not authorization_header or not authorization_header.startswith('Bearer '):
        raise Exception("Missing or invalid authorization header")
    
    token = authorization_header[7:]  # Remove 'Bearer ' prefix
    
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise Exception("Supabase configuration missing")
    
    try:
        # Decode JWT token to get user ID
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            raise Exception("Invalid JWT format")
        
        # Decode the payload (second part)
        payload_encoded = parts[1]
        # Add padding if needed for base64 decoding
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += '=' * padding
            
        payload_bytes = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Extract user ID from JWT
        user_id = payload.get('sub')
        if not user_id:
            raise Exception("No user ID in token")
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Set auth headers for authenticated requests
        supabase.postgrest.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        
        return user_id, supabase
        
    except Exception as e:
        raise Exception(f"Token validation failed: {str(e)}")