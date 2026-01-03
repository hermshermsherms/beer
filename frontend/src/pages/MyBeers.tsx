import { useState, useEffect } from 'react'
import { useAuth } from '../components/AuthContext'
import { API_BASE } from '../config'

interface Beer {
  id: string
  image_url: string
  note: string
  created_at: string
}

function MyBeers() {
  const { isAuthenticated } = useAuth()
  const [beers, setBeers] = useState<Beer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMyBeers = async () => {
      if (!isAuthenticated) {
        setLoading(false)
        return
      }

      try {
        const token = localStorage.getItem('auth_token')
        const response = await fetch(`${API_BASE}/my-beers`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to fetch beers')
        }

        const beersData = await response.json()
        setBeers(beersData)
      } catch (error) {
        console.error('Error fetching beers:', error)
        setError('Failed to load your beers')
      } finally {
        setLoading(false)
      }
    }

    fetchMyBeers()
  }, [isAuthenticated])

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this beer entry?')) {
      try {
        const token = localStorage.getItem('auth_token')
        const response = await fetch(`${API_BASE}/delete-beer`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ beer_id: id })
        })

        if (!response.ok) {
          throw new Error('Failed to delete beer')
        }

        // Remove from local state
        setBeers(beers.filter(beer => beer.id !== id))
      } catch (error) {
        console.error('Error deleting beer:', error)
        alert('Failed to delete beer. Please try again.')
      }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading your beers...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '8px' }}>
        <p>Please log in to view your beers.</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '8px' }}>
        <p style={{ color: 'red' }}>{error}</p>
      </div>
    )
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