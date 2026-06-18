import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../api'

type User = { id: string, email: string, company_id?: string }

const AuthContext = createContext<any>(null)

export function AuthProvider({ children }: any){
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('mf_token'))
  const [user, setUser] = useState<User | null>(null)

  useEffect(()=>{
    if(token){
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // fetch me
      api.get('/auth/me').then(res=> setUser(res.data)).catch(()=>{
        setUser(null)
      })
    } else {
      delete api.defaults.headers.common['Authorization']
      setUser(null)
    }
  },[token])

  const login = async (email:string, password:string) => {
    const res = await api.post('/auth/login', { email, password })
    const t = res.data.access_token
    localStorage.setItem('mf_token', t)
    setToken(t)
    return res.data
  }

  const register = async (company_name:string, name:string, email:string, password:string) => {
    const res = await api.post('/auth/register', { company_name, name, email, password })
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('mf_token')
    setToken(null)
  }

  return <AuthContext.Provider value={{ token, user, login, register, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
export const useUser = () => useContext(AuthContext).user
