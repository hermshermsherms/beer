import { API_BASE } from '../config'

export interface User {
  email: string
  password: string
  name?: string
}

export interface Beer {
  id: string
  user_id: string
  image_url: string
  note: string
  created_at: string
  user_name?: string
}

class ApiService {
  private token: string | null = null
  private refreshToken: string | null = null
  private isRefreshing: boolean = false
  private refreshPromise: Promise<string> | null = null

  setTokens(accessToken: string, refreshToken: string) {
    this.token = accessToken
    this.refreshToken = refreshToken
    localStorage.setItem('auth_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token')
    }
    return this.token
  }

  getRefreshToken(): string | null {
    if (!this.refreshToken) {
      this.refreshToken = localStorage.getItem('refresh_token')
    }
    return this.refreshToken
  }

  clearTokens() {
    this.token = null
    this.refreshToken = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
  }

  // Legacy method for backward compatibility
  setToken(token: string) {
    this.token = token
    localStorage.setItem('auth_token', token)
  }

  // Legacy method for backward compatibility  
  clearToken() {
    this.clearTokens()
  }

  private async refreshAccessToken(): Promise<string> {
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise
    }

    this.isRefreshing = true
    this.refreshPromise = this.performTokenRefresh()

    try {
      const newToken = await this.refreshPromise
      this.isRefreshing = false
      this.refreshPromise = null
      return newToken
    } catch (error) {
      this.isRefreshing = false
      this.refreshPromise = null
      throw error
    }
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await fetch(`${API_BASE}/refresh-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    })

    if (!response.ok) {
      const errorText = await response.text()
      try {
        const errorJson = JSON.parse(errorText)
        throw new Error(errorJson.error || 'Token refresh failed')
      } catch {
        throw new Error('Token refresh failed')
      }
    }

    const data = await response.json()
    this.setTokens(data.access_token, data.refresh_token)
    return data.access_token
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    return this.makeRequest(endpoint, options, false)
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}, isRetry: boolean = false): Promise<any> {
    const url = `${API_BASE}${endpoint}`
    const token = this.getToken()
    
    const headers: HeadersInit = {
      ...options.headers,
    }
    
    // Always add Authorization header if we have a token
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    // Only add Content-Type for JSON, not for FormData
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(options.body)
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorText = await response.text()
      
      // Try to parse as JSON first
      try {
        const errorJson = JSON.parse(errorText)
        
        // If token expired and we haven't already retried, try to refresh
        if ((errorJson.code === 'TOKEN_EXPIRED' || response.status === 401) && !isRetry) {
          try {
            await this.refreshAccessToken()
            // Retry the request with new token
            return this.makeRequest(endpoint, options, true)
          } catch (refreshError) {
            // Refresh failed, clear tokens and throw auth error
            this.clearTokens()
            throw new Error('Your session has expired. Please log in again.')
          }
        }
        
        throw new Error(errorJson.error || `API Error: ${response.status}`)
      } catch (parseError) {
        // If not JSON, check if it's an HTML error page mentioning JWT expired
        if (errorText.includes('JWT expired') && !isRetry) {
          try {
            await this.refreshAccessToken()
            return this.makeRequest(endpoint, options, true)
          } catch (refreshError) {
            this.clearTokens()
            throw new Error('Your session has expired. Please log in again.')
          }
        }
        throw new Error(`API Error: ${errorText}`)
      }
    }

    return response.json()
  }

  async register(user: User) {
    const response = await this.request('/register', {
      method: 'POST',
      body: user,
    })
    
    if (response.access_token && response.refresh_token) {
      this.setTokens(response.access_token, response.refresh_token)
    }
    
    return response
  }

  async login(user: Omit<User, 'name'>) {
    const response = await this.request('/login', {
      method: 'POST',
      body: user,
    })
    
    if (response.access_token && response.refresh_token) {
      this.setTokens(response.access_token, response.refresh_token)
    }
    
    return response
  }

  async postBeer(note: string, image: File) {
    const formData = new FormData()
    formData.append('note', note)
    formData.append('image', image)

    return this.request('/beers', {
      method: 'POST',
      body: formData,
    })
  }

  async getMyBeers(): Promise<Beer[]> {
    return this.request('/my-beers')
  }

  async getAllBeers(): Promise<Beer[]> {
    return this.request('/all-beers')
  }

  async deleteBeer(beerId: string) {
    return this.request(`/delete-beer?beer_id=${encodeURIComponent(beerId)}`, {
      method: 'DELETE'
    })
  }

  async getLeaderboard() {
    return this.request('/leaderboard')
  }
}

export const api = new ApiService()