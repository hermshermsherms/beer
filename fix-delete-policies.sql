-- Fix RLS policies for beer deletion by anonymous API calls

-- Allow anonymous users to delete beers (API handles authorization)
CREATE POLICY "Anonymous users can delete beers" ON beers
  FOR DELETE TO anon USING (true);