import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login(){
  const { login } = useAuth()
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [msg,setMsg]=useState('')
  const nav = useNavigate()

  async function submit(e:any){
    e.preventDefault()
    try{
      await login(email,password)
      nav('/')
    }catch(err:any){
      setMsg(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Login</h2>
      <form onSubmit={submit} className="space-y-4 mt-4">
        <div>
          <label className="block text-sm">Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm">Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded">Login</button>
        </div>
        <div className="text-red-600">{msg}</div>
      </form>
    </div>
  )
}
