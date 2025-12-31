import { useState, useEffect } from 'react'

interface Beer {
  id: string
  image_url: string
  note: string
  created_at: string
  user_name: string
}

function AllBeers() {
  const [beers, setBeers] = useState<Beer[]>([])

  useEffect(() => {
    // TODO: Fetch all beers from Supabase
    // Mock data for now
    setBeers([
      {
        id: '1',
        image_url: 'https://via.placeholder.com/80x80?text=🍺',
        note: 'Amazing craft beer from local brewery',
        created_at: '2023-12-31T12:00:00Z',
        user_name: 'John Doe'
      },
      {
        id: '2',
        image_url: 'https://via.placeholder.com/80x80?text=🍻',
        note: 'Perfect beer for a hot summer day',
        created_at: '2023-12-30T18:30:00Z',
        user_name: 'Jane Smith'
      }
    ])
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
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