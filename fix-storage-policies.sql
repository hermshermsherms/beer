-- Fix storage policies to allow anonymous uploads from our API
-- This allows the API to upload images using the anon key

-- Allow anonymous users to upload images
CREATE POLICY "Anonymous users can upload images" ON storage.objects
  FOR INSERT TO anon WITH CHECK (bucket_id = 'beer-images');

-- Allow anyone (including anon) to view images  
CREATE POLICY "Anyone can view images anon" ON storage.objects
  FOR SELECT TO anon USING (bucket_id = 'beer-images');