import { Link, Outlet } from 'react-router-dom'

function Layout() {
  return (
    <>
      <nav className="nav">
        <div className="container nav-container">
          <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 'bold', textDecoration: 'none', color: '#667eea' }}>
            🍺 Beer App
          </Link>
          <ul className="nav-links">
            <li><Link to="/">Post Beer</Link></li>
            <li><Link to="/my-beers">My Beers</Link></li>
            <li><Link to="/all-beers">All Beers</Link></li>
            <li><Link to="/leaderboard">Leaderboard</Link></li>
            <li><Link to="/login">Logout</Link></li>
          </ul>
        </div>
      </nav>
      <main className="container" style={{ padding: '2rem 20px' }}>
        <Outlet />
      </main>
    </>
  )
}

export default Layout