import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  userId: string | null
  login: (token: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [userId, setUserId] = useState<string | null>(null)

  const extractUserIdFromToken = (token: string) => {
    try {
      // Parse JWT token to extract user ID and check expiration
      const payload = JSON.parse(atob(token.split('.')[1]))
      
      // Check if token is expired
      const currentTime = Math.floor(Date.now() / 1000)
      if (payload.exp && payload.exp < currentTime) {
        console.log('Token has expired')
        return null // Token expired
      }
      
      return payload.sub || null // 'sub' is the user ID in Supabase JWTs
    } catch (error) {
      console.error('Failed to parse JWT token:', error)
      return null
    }
  }

  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return payload.exp && payload.exp < currentTime
    } catch (error) {
      return true // If we can't parse it, consider it expired
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      if (isTokenExpired(token)) {
        // Token is expired, clear it
        console.log('Stored token has expired, logging out')
        localStorage.removeItem('auth_token')
        setIsAuthenticated(false)
        setUserId(null)
      } else {
        const extractedUserId = extractUserIdFromToken(token)
        if (extractedUserId) {
          setIsAuthenticated(true)
          setUserId(extractedUserId)
        } else {
          localStorage.removeItem('auth_token')
          setIsAuthenticated(false)
          setUserId(null)
        }
      }
    } else {
      setIsAuthenticated(false)
      setUserId(null)
    }
    setIsLoading(false)
  }, [])

  const login = (token: string) => {
    localStorage.setItem('auth_token', token)
    const extractedUserId = extractUserIdFromToken(token)
    setIsAuthenticated(true)
    setUserId(extractedUserId)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setIsAuthenticated(false)
    setUserId(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, userId, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}