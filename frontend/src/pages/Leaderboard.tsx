import { useState, useEffect } from 'react'
import { API_BASE } from '../config'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface UserData {
  user_name: string
  monthly_data: { month: string; total_drinks: number }[]
}

function Leaderboard() {
  const [userData, setUserData] = useState<UserData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchLeaderboardData = async () => {
      try {
        const response = await fetch(`${API_BASE}/leaderboard`)

        if (!response.ok) {
          throw new Error('Failed to fetch leaderboard data')
        }

        const leaderboardData = await response.json()
        setUserData(leaderboardData)
      } catch (error) {
        console.error('Error fetching leaderboard data:', error)
        setError('Failed to load leaderboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboardData()
  }, [])

  const getDays = () => {
    const days = new Set<string>()
    userData.forEach(user => {
      user.monthly_data.forEach(data => days.add(data.month))
    })
    return Array.from(days).sort()
  }

  const getLeaderboardSummary = () => {
    return userData
      .map(user => ({
        user_name: user.user_name,
        total_beers: user.monthly_data.length > 0 
          ? user.monthly_data[user.monthly_data.length - 1].total_drinks 
          : 0
      }))
      .sort((a, b) => b.total_beers - a.total_beers)
  }

  const getChartData = () => {
    const days = getDays()
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    return {
      labels: days.map(day => {
        // Format YYYY-MM-DD to a more readable format
        const date = new Date(day + 'T12:00:00')
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }),
      datasets: userData.map((user, index) => ({
        label: user.user_name,
        data: days.map(day => {
          const dayData = user.monthly_data.find(d => d.month === day)
          return dayData ? dayData.total_drinks : 0
        }),
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length] + '20',
        tension: 0.1,
        pointRadius: 5,
        pointHoverRadius: 8,
        fill: false
      }))
    }
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Cumulative Beers Over Time (By Day)'
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
      annotation: {
        annotations: userData.reduce((acc, user, index) => {
          if (user.monthly_data.length > 0) {
            const lastDataPoint = user.monthly_data[user.monthly_data.length - 1]
            const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
            acc[`label${index}`] = {
              type: 'label',
              xValue: getDays().length - 1,
              yValue: lastDataPoint.total_drinks,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              borderColor: colors[index % colors.length],
              borderWidth: 1,
              borderRadius: 4,
              content: user.user_name,
              font: {
                size: 11,
                weight: 'bold'
              },
              textAlign: 'center',
              xAdjust: 20,
              yAdjust: index * 15 - (userData.length * 7.5) // Spread labels vertically
            }
          }
          return acc
        }, {} as any)
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Total Drinks'
        },
        ticks: {
          stepSize: 1
        }
      },
      x: {
        title: {
          display: true,
          text: 'Days'
        }
      }
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    hover: {
      mode: 'index' as const,
      intersect: false,
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading leaderboard data...</p>
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
      <h1 style={{ marginBottom: '2rem' }}>Leaderboard</h1>
      
      {userData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '8px' }}>
          <p>No data available yet.</p>
        </div>
      ) : (
        <>
          {/* Summary Table */}
          <div className="table-wrapper" style={{ marginBottom: '2rem' }}>
            <table className="table leaderboard-table">
              <thead>
                <tr>
                  <th style={{ textAlign: 'center', width: '20%', padding: '0.5rem 0.25rem' }}>#</th>
                  <th style={{ width: '55%', padding: '0.5rem 0.25rem' }}>Name</th>
                  <th style={{ textAlign: 'center', width: '25%', padding: '0.5rem 0.25rem' }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {getLeaderboardSummary().map((user, index) => (
                  <tr key={user.user_name}>
                    <td style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem', padding: '0.5rem 0.25rem' }}>
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                    </td>
                    <td style={{ fontWeight: index < 3 ? 'bold' : 'normal', padding: '0.5rem 0.25rem' }}>
                      {user.user_name}
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 'bold', color: '#667eea', padding: '0.5rem 0.25rem' }}>
                      {user.total_beers}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Chart */}
          <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            <Line data={getChartData()} options={options} />
          </div>
        </>
      )}
    </div>
  )
}

export default Leaderboard