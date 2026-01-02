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

  const decodeToken = (token: string) => {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      return JSON.parse(jsonPayload)
    } catch (error) {
      return null
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      const decoded = decodeToken(token)
      if (decoded && decoded.sub) {
        setIsAuthenticated(true)
        setUserId(decoded.sub)
      } else {
        localStorage.removeItem('auth_token')
        setIsAuthenticated(false)
        setUserId(null)
      }
    } else {
      setIsAuthenticated(false)
      setUserId(null)
    }
    setIsLoading(false)
  }, [])

  const login = (token: string) => {
    localStorage.setItem('auth_token', token)
    const decoded = decodeToken(token)
    setIsAuthenticated(true)
    setUserId(decoded?.sub || null)
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