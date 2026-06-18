import React, { useState } from 'react'
import axios from 'axios'

export default function Login(){
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [msg,setMsg]=useState('')

  async function submit(e:any){
    e.preventDefault()
    try{
      const res = await axios.post('/api/auth/login', { email, password })
      setMsg('Logged in (token received)')
    }catch(err:any){
      setMsg(err?.response?.data?.detail || 'Error')
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button type="submit">Login</button>
      </form>
      <div>{msg}</div>
    </div>
  )
}
