import { useState, useEffect } from 'react'

interface Beer {
  id: string
  image_url: string
  note: string
  created_at: string
}

function MyBeers() {
  const [beers, setBeers] = useState<Beer[]>([])

  useEffect(() => {
    // TODO: Fetch user's beers from Supabase
    // Mock data for now
    setBeers([
      {
        id: '1',
        image_url: 'https://via.placeholder.com/80x80?text=🍺',
        note: 'Great IPA with citrus notes',
        created_at: '2023-12-31T12:00:00Z'
      }
    ])
  }, [])

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this beer entry?')) {
      // TODO: Delete from Supabase
      setBeers(beers.filter(beer => beer.id !== id))
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
  }

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>My Beers</h1>
      
      {beers.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '8px' }}>
          <p>No beers posted yet. <a href="/">Post your first beer!</a></p>
        </div>
      ) : (
        <div style={{ background: 'white', borderRadius: '8px', overflow: 'hidden' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Picture</th>
                <th>Note</th>
                <th>Date/Time</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {beers.map((beer) => (
                <tr key={beer.id}>
                  <td>
                    <img src={beer.image_url} alt="Beer" className="beer-image" />
                  </td>
                  <td>{beer.note}</td>
                  <td>{formatDate(beer.created_at)}</td>
                  <td>
                    <button 
                      onClick={() => handleDelete(beer.id)}
                      style={{ 
                        background: '#dc3545', 
                        color: 'white', 
                        border: 'none', 
                        padding: '0.5rem 1rem', 
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default MyBeers