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

  setToken(token: string) {
    this.token = token
    localStorage.setItem('auth_token', token)
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token')
    }
    return this.token
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('auth_token')
  }

  private async request(endpoint: string, options: RequestInit = {}) {
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
      const error = await response.text()
      throw new Error(`API Error: ${error}`)
    }

    return response.json()
  }

  async register(user: User) {
    const response = await this.request('/register', {
      method: 'POST',
      body: user,
    })
    
    if (response.access_token) {
      this.setToken(response.access_token)
    }
    
    return response
  }

  async login(user: Omit<User, 'name'>) {
    const response = await this.request('/login', {
      method: 'POST',
      body: user,
    })
    
    if (response.access_token) {
      this.setToken(response.access_token)
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
    return this.request(`/beers/${beerId}`, {
      method: 'DELETE',
    })
  }

  async getLeaderboard() {
    return this.request('/leaderboard')
  }
}

export const api = new ApiService()