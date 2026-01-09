import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG } from '../config'

export const supabase = createClient(
  SUPABASE_CONFIG.url,
  SUPABASE_CONFIG.anonKey
)

export const uploadBeerImage = async (file: File, userId: string) => {
  // Get the JWT token from localStorage
  const token = localStorage.getItem('auth_token')
  if (!token) {
    throw new Error('No authentication token found')
  }
  
  // Create a new Supabase client with the JWT token
  const authenticatedSupabase = createClient(
    SUPABASE_CONFIG.url,
    SUPABASE_CONFIG.anonKey
  )
  
  // Set the auth session with the JWT token
  await authenticatedSupabase.auth.setSession({
    access_token: token,
    refresh_token: ''
  })
  
  const fileExt = file.name.split('.').pop()
  const fileName = `${userId}/${Date.now()}.${fileExt}`
  
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