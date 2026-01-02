import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../services/api'

function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      alert('Passwords do not match')
      return
    }

    try {
      const response = await api.register({ username, password, name })
      console.log('Registration successful:', response)
      navigate('/')
    } catch (error: any) {
      console.error('Registration failed:', error)
      alert('Registration failed: ' + (error?.message || 'Unknown error'))
    }
  }

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: '#333' }}>
          🍺 Create Account
        </h2>
        
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit">Create Account</button>

        <p style={{ textAlign: 'center', marginTop: '1rem' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#667eea' }}>Sign in</Link>
        </p>
      </form>
    </div>
  )
}

export default Register