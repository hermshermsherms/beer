import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG } from '../config'

export const supabase = createClient(
  SUPABASE_CONFIG.url,
  SUPABASE_CONFIG.anonKey
)

export const uploadBeerImage = async (file: File, userId: string) => {
  const fileExt = file.name.split('.').pop()
  const fileName = `${userId}/${Date.now()}.${fileExt}`
  
  // Get the JWT token and set it directly on the request
  const token = localStorage.getItem('auth_token')
  if (!token) {
    throw new Error('No authentication token found')
  }
  
  // Create a new supabase client instance with the auth header
  const authenticatedSupabase = createClient(
    SUPABASE_CONFIG.url,
    SUPABASE_CONFIG.anonKey,
    {
      global: {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    }
  )
  
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