import React, { useEffect, useState } from 'react'
import api from '../api'

export default function AdminProviders(){
  const [phoneId, setPhoneId] = useState('')
  const [token, setToken] = useState('')
  const [existing, setExisting] = useState('')

  useEffect(()=>{
    async function load(){
      try{
        const res = await api.get('/admin/providers')
        setExisting(res.data.phone_number_id || '')
      }catch(e){ }
    }
    load()
  },[])

  async function save(){
    try{
      await api.post('/admin/providers', { phone_number_id: phoneId, access_token: token })
      alert('Saved')
    }catch(e){ alert('Save failed') }
  }

  async function remove(){
    try{ await api.delete('/admin/providers'); setExisting(''); alert('Deleted') }catch(e){ alert('Delete failed') }
  }

  return (
    <div className="bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Provider Configs</h2>
      <div className="mt-4">
        <div className="text-sm">Current phone_number_id: {existing || 'none'}</div>
      </div>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm">Phone Number ID</label>
          <input value={phoneId} onChange={e=>setPhoneId(e.target.value)} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm">Access Token</label>
          <input value={token} onChange={e=>setToken(e.target.value)} className="w-full border p-2 rounded" />
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <button onClick={save} className="px-4 py-2 bg-green-600 text-white rounded">Save</button>
        <button onClick={remove} className="px-4 py-2 bg-red-600 text-white rounded">Delete</button>
      </div>
    </div>
  )
}
