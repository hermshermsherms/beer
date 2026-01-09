import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG } from '../config'

export const supabase = createClient(
  SUPABASE_CONFIG.url,
  SUPABASE_CONFIG.anonKey
)

// Helper to ensure supabase client is authenticated
const getAuthenticatedSupabase = () => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    supabase.auth.setSession({
      access_token: token,
      refresh_token: '', // Not needed for our use case
    })
  }
  return supabase
}

export const uploadBeerImage = async (file: File, userId: string) => {
  const fileExt = file.name.split('.').pop()
  const fileName = `${userId}/${Date.now()}.${fileExt}`
  
  // Get authenticated supabase client
  const authenticatedSupabase = getAuthenticatedSupabase()
  
  const { data, error } = await authenticatedSupabase.storage
    .from('beer-images')
    .upload(fileName, file)
    
  if (error) {
    throw error
  }
  
  const { data: { publicUrl } } = authenticatedSupabase.storage
    .from('beer-images')
    .getPublicUrl(fileName)
    
  return publicUrl
}

export const createBeerPost = async (imageUrl: string, note: string, userId: string) => {
  const { data, error } = await supabase
    .from('beers')
    .insert({
      user_id: userId,
      image_url: imageUrl,
      note: note
    })
    .select()
    
  if (error) {
    throw error
  }
  
  return data[0]
}