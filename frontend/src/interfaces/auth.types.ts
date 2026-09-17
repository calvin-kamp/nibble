export interface User {
  id: number
  email: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials extends LoginCredentials {
  passwordConfirm: string
  tosAccepted: boolean
}

export interface AuthResponse {
  access: string
  user: User
}

export interface TokenRefreshResponse {
  access: string
}

export type AuthNotice = 'session-expired' | 'logged-out'
