-- Users table (simple auth without Supabase auth.users)
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Beers table
CREATE TABLE beers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) NOT NULL,
  image_url TEXT NOT NULL,
  note TEXT NOT NULL CHECK (length(note) <= 250),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE beers ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to view all beers
CREATE POLICY "Anyone can view beers" ON beers
  FOR SELECT TO anon USING (true);

-- Allow anonymous users to insert beers (API handles auth)
CREATE POLICY "Allow beer inserts" ON beers
  FOR INSERT TO anon WITH CHECK (true);

-- Users can only delete their own beers
CREATE POLICY "Users can delete own beers" ON beers
  FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Create storage bucket for beer images
INSERT INTO storage.buckets (id, name, public)
VALUES ('beer-images', 'beer-images', true);

-- Allow authenticated users to upload images
CREATE POLICY "Authenticated users can upload images" ON storage.objects
  FOR INSERT TO authenticated WITH CHECK (bucket_id = 'beer-images');

-- Allow anyone to view images
CREATE POLICY "Anyone can view images" ON storage.objects
  FOR SELECT TO authenticated USING (bucket_id = 'beer-images');

-- Allow users to delete their own images
CREATE POLICY "Users can delete own images" ON storage.objects
  FOR DELETE TO authenticated USING (bucket_id = 'beer-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Function to get monthly beer counts for leaderboard
CREATE OR REPLACE FUNCTION get_monthly_beer_counts()
RETURNS TABLE(
  user_name TEXT,
  month TEXT,
  total_drinks BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.name,
    TO_CHAR(DATE_TRUNC('month', b.created_at), 'YYYY-MM') as month,
    COUNT(*) as total_drinks
  FROM beers b
  JOIN users u ON b.user_id = u.id
  GROUP BY u.name, DATE_TRUNC('month', b.created_at)
  ORDER BY month, u.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;