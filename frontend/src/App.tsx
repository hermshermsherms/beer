import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './components/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import PostBeer from './pages/PostBeer'
import MyBeers from './pages/MyBeers'
import AllBeers from './pages/AllBeers'
import Leaderboard from './pages/Leaderboard'

function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
        <Route path="/register" element={isAuthenticated ? <Navigate to="/" replace /> : <Register />} />
        
        {/* Protected routes */}
        {isAuthenticated ? (
          <Route path="/" element={<Layout />}>
            <Route index element={<PostBeer />} />
            <Route path="my-beers" element={<MyBeers />} />
            <Route path="all-beers" element={<AllBeers />} />
            <Route path="leaderboard" element={<Leaderboard />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App