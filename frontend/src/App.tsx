import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import PostBeer from './pages/PostBeer'
import MyBeers from './pages/MyBeers'
import AllBeers from './pages/AllBeers'
import Leaderboard from './pages/Leaderboard'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<PostBeer />} />
          <Route path="my-beers" element={<MyBeers />} />
          <Route path="all-beers" element={<AllBeers />} />
          <Route path="leaderboard" element={<Leaderboard />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App