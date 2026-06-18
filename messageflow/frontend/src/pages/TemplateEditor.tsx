import React, { useEffect, useState } from 'react'
import api from '../api'
import { useNavigate } from 'react-router-dom'

const STORAGE_KEY = 'mf_datasets'

export default function TemplateEditor(){
  const [name, setName] = useState('')
  const [channel, setChannel] = useState('whatsapp')
  const [content, setContent] = useState('')
  const [datasets] = useState(() => { try{ const raw = localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : [] }catch{ return [] } })
  const [columns, setColumns] = useState<string[]>([])
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(datasets?.[0]?.id || null)
  const nav = useNavigate()

  useEffect(()=>{ if(selectedDatasetId){ const ds = datasets.find((d:any)=>d.id===selectedDatasetId); setColumns(ds?.column_map?.map((c:any)=>c.orig) || []) } },[selectedDatasetId])

  function insertVariable(v:string){
    const token = `{{${v}}}`
    setContent(prev => prev + (prev && !prev.endsWith('\n') ? '\n' : '') + token)
  }

  async function save(){
    try{
      const res = await api.post('/templates', { template_name: name, channel, template_content: content })
      nav('/templates')
    }catch(err:any){ alert('Failed to save template') }
  }

  return (
    <div className="bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Create Template</h2>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-2">
          <div>
            <label className="block text-sm">Template Name</label>
            <input value={name} onChange={e=>setName(e.target.value)} className="w-full border p-2 rounded" />
          </div>
          <div className="mt-3">
            <label className="block text-sm">Channel</label>
            <select value={channel} onChange={e=>setChannel(e.target.value)} className="border p-2 rounded">
              <option value="whatsapp">WhatsApp</option>
              <option value="email">Email</option>
            </select>
          </div>
          <div className="mt-3">
            <label className="block text-sm">Content</label>
            <textarea value={content} onChange={e=>setContent(e.target.value)} rows={10} className="w-full border p-2 rounded" />
          </div>
          <div className="mt-3">
            <button onClick={save} className="px-4 py-2 bg-green-600 text-white rounded">Save Template</button>
          </div>
        </div>
        <div>
          <div>
            <label className="block text-sm">Select Dataset (for variables)</label>
            <select value={selectedDatasetId || ''} onChange={e=>setSelectedDatasetId(e.target.value || null)} className="w-full border p-2 rounded">
              <option value="">-- none --</option>
              {datasets.map((d:any)=> <option key={d.id} value={d.id}>{d.dataset_name}</option>)}
            </select>
          </div>
          <div className="mt-3">
            <h4 className="font-semibold">Available Variables</h4>
            <div className="mt-2 space-y-1 max-h-64 overflow-auto">
              {columns.map(c=> (
                <div key={c} className="text-sm flex justify-between items-center">
                  <span>{`{{${c}}}`}</span>
                  <button onClick={()=>insertVariable(c)} className="text-blue-600 text-xs">Insert</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
