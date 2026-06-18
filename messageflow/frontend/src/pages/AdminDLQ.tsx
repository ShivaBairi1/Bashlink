import React, { useEffect, useState } from 'react'
import api from '../api'

export default function AdminDLQ(){
  const [items, setItems] = useState<any[]>([])

  useEffect(()=>{ load() },[])

  async function load(){
    try{
      const res = await api.get('/admin/dlq')
      setItems(res.data)
    }catch(e){ }
  }

  async function retry(id:string){
    try{
      await api.post(`/admin/dlq/${id}/retry`)
      alert('Retry enqueued')
    }catch(e){ alert('Retry failed') }
  }

  async function clearAll(){
    try{ await api.delete('/admin/dlq'); setItems([]); alert('Cleared') }catch(e){ alert('Clear failed') }
  }

  return (
    <div className="bg-white p-6 rounded shadow">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Dead Letter Queue</h2>
        <button onClick={clearAll} className="px-3 py-1 bg-red-600 text-white rounded">Clear All</button>
      </div>
      <div className="mt-4">
        {items.map(i=>(
          <div key={i.id} className="p-3 border-b">
            <div className="font-medium">{i.channel} — {i.error}</div>
            <div className="text-sm">Payload: {JSON.stringify(i.payload)}</div>
            <div className="mt-2">
              <button onClick={()=>retry(i.id)} className="px-3 py-1 bg-yellow-500 text-white rounded">Retry</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
