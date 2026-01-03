import { useState, useEffect } from 'react'
import { API_BASE } from '../config'

interface Beer {
  id: string
  image_url: string
  note: string
  created_at: string
  user_name: string
}

function AllBeers() {
  const [beers, setBeers] = useState<Beer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAllBeers = async () => {
      try {
        const response = await fetch(`${API_BASE}/all-beers`)

        if (!response.ok) {
          throw new Error('Failed to fetch beers')
        }

        const beersData = await response.json()
        setBeers(beersData)
      } catch (error) {
        console.error('Error fetching beers:', error)
        setError('Failed to load beers')
      } finally {
        setLoading(false)
      }
    }

    fetchAllBeers()
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading all beers...</p>
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
      <h1 style={{ marginBottom: '2rem' }}>All Beers</h1>
      
      {beers.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '8px' }}>
          <p>No beers have been posted yet.</p>
        </div>
      ) : (
        <div style={{ background: 'white', borderRadius: '8px', overflow: 'hidden' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Picture</th>
                <th>Note</th>
                <th>Date/Time</th>
                <th>Posted By</th>
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
                  <td>{beer.user_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default AllBeers