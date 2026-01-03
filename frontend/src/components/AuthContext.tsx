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
      // Our token format is "token_<user_id>"
      if (token.startsWith('token_')) {
        return token.substring(6) // Remove "token_" prefix
      }
      return null
    } catch (error) {
      return null
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      const extractedUserId = extractUserIdFromToken(token)
      if (extractedUserId) {
        setIsAuthenticated(true)
        setUserId(extractedUserId)
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