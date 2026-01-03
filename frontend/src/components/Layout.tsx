import { Link, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

function Layout() {
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    // Navigation will be handled automatically by the auth routing
  }

  return (
    <>
      <nav className="nav">
        <div className="container nav-container">
          <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 'bold', textDecoration: 'none', color: '#667eea' }}>
            🍺 MegaBeer
          </Link>
          <ul className="nav-links">
            <li><Link to="/">Post Beer</Link></li>
            <li><Link to="/my-beers">My Beers</Link></li>
            <li><Link to="/all-beers">All Beers</Link></li>
            <li><Link to="/leaderboard">Leaderboard</Link></li>
            <li>
              <button 
                onClick={handleLogout}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: '#333', 
                  fontWeight: '500',
                  cursor: 'pointer',
                  fontSize: 'inherit'
                }}
              >
                Logout
              </button>
            </li>
          </ul>
        </div>
      </nav>
      <main className="container main-content" style={{ padding: '2rem 20px', borderRadius: '20px 20px 0 0', marginTop: '1rem' }}>
        <Outlet />
      </main>
    </>
  )
}

export default Layout