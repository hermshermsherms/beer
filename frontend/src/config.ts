// API Configuration
export const API_BASE = process.env.NODE_ENV === 'production' 
  ? '/api'  // Production: relative to current domain
  : 'http://localhost:8000/api'  // Development: local backend

export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL || '',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || ''
}