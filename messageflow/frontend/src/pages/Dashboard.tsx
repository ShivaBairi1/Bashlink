import React, { useEffect, useState } from 'react'
import api from '../api'

export default function Dashboard(){
  const [templates, setTemplates] = useState<any[]>([])
  const [inboxCount, setInboxCount] = useState(0)

  useEffect(()=>{
    async function load(){
      try{
        const t = await api.get('/templates')
        setTemplates(t.data)
      }catch(e){ }
      try{
        const m = await api.get('/inbox')
        setInboxCount(m.data.length)
      }catch(e){ }
    }
    load()
  },[])

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="col-span-2 bg-white p-6 rounded shadow">
        <h2 className="text-lg font-semibold">Overview</h2>
        <div className="mt-4">Templates: {templates.length}</div>
        <div>Inbox messages: {inboxCount}</div>
      </div>
      <div className="bg-white p-6 rounded shadow">
        <h3 className="font-semibold">Quick Actions</h3>
        <ul className="mt-3 space-y-2 text-sm">
          <li>• Create template</li>
          <li>• Upload dataset</li>
          <li>• Start campaign</li>
        </ul>
      </div>
    </div>
  )
}
