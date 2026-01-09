import os
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
    
    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        # Validate token and get user
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise Exception("Invalid token")
        
        return user_response.user.id, supabase
        
    except Exception as e:
        raise Exception(f"Token validation failed: {str(e)}")