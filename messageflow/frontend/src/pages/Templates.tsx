import React, { useEffect, useState } from 'react'
import api from '../api'
import { Link } from 'react-router-dom'

export default function Templates(){
  const [templates, setTemplates] = useState<any[]>([])

  useEffect(()=>{
    async function load(){
      try{
        const res = await api.get('/templates')
        setTemplates(res.data)
      }catch(e){ }
    }
    load()
  },[])

  return (
    <div className="bg-white p-6 rounded shadow">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Templates</h2>
        <Link to="/templates/new" className="text-sm text-blue-600">Create</Link>
      </div>
      <ul className="mt-4">
        {templates.map(t=>(
          <li key={t.id} className="p-3 border-b">
            <div className="font-medium">{t.template_name}</div>
            <div className="text-sm text-gray-600">{t.channel}</div>
            <pre className="text-xs mt-2 bg-gray-50 p-2 rounded">{t.template_content}</pre>
          </li>
        ))}
      </ul>
    </div>
  )
}
