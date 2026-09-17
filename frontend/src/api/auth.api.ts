import type {
  AuthResponse,
  LoginCredentials,
  RegisterCredentials,
  TokenRefreshResponse,
  User,
} from '@interfaces/auth.types'

import { http } from '@lib/http'

const AUTH_PREFIX = '/auth'

export function login(credentials: LoginCredentials): Promise<AuthResponse> {
  return http.post<AuthResponse>(`${AUTH_PREFIX}/login/`, credentials, { skipRefresh: true })
}

export function register(credentials: RegisterCredentials): Promise<AuthResponse> {
  return http.post<AuthResponse>(`${AUTH_PREFIX}/register/`, credentials, { skipRefresh: true })
}

export function refresh(): Promise<TokenRefreshResponse> {
  return http.post<TokenRefreshResponse>(`${AUTH_PREFIX}/token/refresh/`, undefined, {
    skipRefresh: true,
  })
}

export function logout(): Promise<void> {
  return http.post<void>(`${AUTH_PREFIX}/logout/`, undefined, { skipRefresh: true })
}

export function getCurrentUser(): Promise<User> {
  return http.get<User>(`${AUTH_PREFIX}/me/`)
}
