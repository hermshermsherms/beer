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

  const getMonths = () => {
    const months = new Set<string>()
    userData.forEach(user => {
      user.monthly_data.forEach(data => months.add(data.month))
    })
    return Array.from(months).sort()
  }

  const getChartData = () => {
    const months = getMonths()
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    return {
      labels: months.map(month => {
        const date = new Date(month + '-01')
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
      }),
      datasets: userData.map((user, index) => ({
        label: user.user_name,
        data: months.map(month => {
          const monthData = user.monthly_data.find(d => d.month === month)
          return monthData ? monthData.total_drinks : 0
        }),
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length] + '20',
        tension: 0.4
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
        text: 'Cumulative Beers Over Time'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Total Drinks'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time (Months)'
        }
      }
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
        <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <Line data={getChartData()} options={options} />
        </div>
      )}
    </div>
  )
}

export default Leaderboard