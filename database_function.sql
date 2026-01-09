-- Function to get user name from auth.users metadata
-- Run this in your Supabase SQL Editor

CREATE OR REPLACE FUNCTION get_user_name(user_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    user_name text;
BEGIN
    -- Get the user name from auth.users metadata
    SELECT (raw_user_meta_data->>'name')::text
    INTO user_name
    FROM auth.users
    WHERE id = user_id;
    
    -- Return the name or a fallback
    IF user_name IS NOT NULL AND user_name != '' THEN
        RETURN user_name;
    ELSE
        RETURN 'User ' || SUBSTRING(user_id::text, 1, 8) || '...';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'User ' || SUBSTRING(user_id::text, 1, 8) || '...';
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_user_name(uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_name(uuid) TO anon;