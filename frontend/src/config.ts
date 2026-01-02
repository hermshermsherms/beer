// API Configuration
export const API_BASE = process.env.NODE_ENV === 'production' 
  ? '/api'  // Production: relative to current domain
  : 'http://localhost:8000/api'  // Development: local backend

export const SUPABASE_CONFIG = {
  url: 'https://rczatkqbmclnuwtanonj.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjemF0a3FibWNsbnV3dGFub25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxOTU3ODksImV4cCI6MjA4Mjc3MTc4OX0.jkRHtatdUysh8DoLyjIX0tkEC69aEqPtEDGpJv_qOQE'
}