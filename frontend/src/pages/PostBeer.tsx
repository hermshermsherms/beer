import { useState } from 'react'
import { useAuth } from '../components/AuthContext'
import { API_BASE } from '../config'

function PostBeer() {
  const { userId } = useAuth()
  const [image, setImage] = useState<File | null>(null)
  const [note, setNote] = useState('')
  const [uploading, setUploading] = useState(false)

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!image) {
      alert('Please select an image')
      return
    }

    if (note.length > 250) {
      alert('Note must be 250 characters or less')
      return
    }

    if (!userId) {
      alert('You must be logged in to post')
      return
    }

    setUploading(true)
    
    try {
      // For now, send JSON instead of FormData (skip image upload)
      const token = localStorage.getItem('auth_token')
      
      const response = await fetch(`${API_BASE}/beers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ note })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to post beer')
      }
      
      const result = await response.json()
      alert('Beer posted successfully!')
      
      // Reset form
      setImage(null)
      setNote('')
      const fileInput = document.getElementById('image') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (error: any) {
      console.error('Error posting beer:', error)
      alert('Failed to post beer: ' + (error.message || 'Please try again.'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem', textAlign: 'center' }}>🍺 Post a Beer</h1>
      
      <form onSubmit={handleSubmit} style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <div className="form-group">
          <label htmlFor="image">Beer Picture</label>
          <input
            type="file"
            id="image"
            accept="image/jpeg,image/png"
            onChange={handleImageChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="note">Description ({note.length}/250)</label>
          <textarea
            id="note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={250}
            rows={4}
            placeholder="Tasting Notes"
          />
        </div>

        <button type="submit" disabled={uploading}>
          {uploading ? 'Posting...' : 'Post Beer'}
        </button>
      </form>
    </div>
  )
}

export default PostBeer