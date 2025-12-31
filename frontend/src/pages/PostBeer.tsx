import { useState } from 'react'

function PostBeer() {
  const [image, setImage] = useState<File | null>(null)
  const [note, setNote] = useState('')

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0])
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!image) {
      alert('Please select an image')
      return
    }

    if (note.length > 250) {
      alert('Note must be 250 characters or less')
      return
    }

    // TODO: Implement beer posting with Supabase
    console.log('Post beer:', { image, note })
    
    // Reset form
    setImage(null)
    setNote('')
    const fileInput = document.getElementById('image') as HTMLInputElement
    if (fileInput) fileInput.value = ''
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
            placeholder="Tell us about this beer..."
          />
        </div>

        <button type="submit">Post Beer</button>
      </form>
    </div>
  )
}

export default PostBeer