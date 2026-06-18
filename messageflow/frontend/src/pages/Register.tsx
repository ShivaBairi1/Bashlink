import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Register(){
  const { register } = useAuth()
  const [company,setCompany]=useState('')
  const [name,setName]=useState('')
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [msg,setMsg]=useState('')
  const nav = useNavigate()

  async function submit(e:any){
    e.preventDefault()
    try{
      await register(company,name,email,password)
      nav('/login')
    }catch(err:any){
      setMsg('Registration failed')
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Register</h2>
      <form onSubmit={submit} className="space-y-4 mt-4">
        <div>
          <label className="block text-sm">Company Name</label>
          <input value={company} onChange={e=>setCompany(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm">Your Name</label>
          <input value={name} onChange={e=>setName(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm">Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm">Password</label>
          <input value={password} onChange={e=>setPassword(e.target.value)} type="password" className="w-full border p-2 rounded" />
        </div>
        <div>
          <button className="px-4 py-2 bg-green-600 text-white rounded">Register</button>
        </div>
        <div className="text-red-600">{msg}</div>
      </form>
    </div>
  )
}
