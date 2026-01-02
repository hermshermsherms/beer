import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG } from '../config'

export const supabase = createClient(
  SUPABASE_CONFIG.url,
  SUPABASE_CONFIG.anonKey
)

export const uploadBeerImage = async (file: File, userId: string) => {
  const fileExt = file.name.split('.').pop()
  const fileName = `${userId}/${Date.now()}.${fileExt}`
  
  const { data, error } = await supabase.storage
    .from('beer-images')
    .upload(fileName, file)
    
  if (error) {
    throw error
  }
  
  const { data: { publicUrl } } = supabase.storage
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