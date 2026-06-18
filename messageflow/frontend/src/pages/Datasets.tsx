import React, { useEffect, useState } from 'react'
import api from '../api'

type Dataset = { id:string, dataset_name:string, uploaded_file_name?:string, column_map?: any }

const STORAGE_KEY = 'mf_datasets'

export default function Datasets(){
  const [datasets, setDatasets] = useState<Dataset[]>(() => {
    try{ const raw = localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : [] }catch{ return [] }
  })
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [uploading, setUploading] = useState(false)

  useEffect(()=>{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(datasets))
  },[datasets])

  async function upload(e:any){
    e.preventDefault()
    if(!file) return
    const fd = new FormData()
    fd.append('file', file)
    fd.append('dataset_name', name || file.name)
    setUploading(true)
    try{
      const res = await api.post('/datasets/upload', fd, { headers: {'Content-Type':'multipart/form-data'} })
      const ds = res.data
      setDatasets(prev => [ds, ...prev])
    }catch(err:any){
      alert(err?.response?.data?.detail || 'Upload failed')
    }finally{ setUploading(false) }
  }

  async function loadColumns(ds:Dataset){
    try{
      const res = await api.get(`/datasets/${ds.id}/columns`)
      alert('Columns: '+ res.data.columns.join(', '))
    }catch(err:any){ alert('Failed to load columns') }
  }

  return (
    <div className="bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Datasets</h2>
      <form onSubmit={upload} className="mt-4 space-y-3">
        <div>
          <label className="block text-sm">Dataset Name</label>
          <input value={name} onChange={e=>setName(e.target.value)} className="border p-2 rounded w-full" />
        </div>
        <div>
          <input type="file" onChange={e=> setFile(e.target.files?.[0] || null)} />
        </div>
        <div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded" disabled={uploading}>{uploading? 'Uploading...' : 'Upload'}</button>
        </div>
      </form>

      <div className="mt-6">
        <h3 className="font-semibold">My Uploaded Datasets</h3>
        <ul className="mt-3">
          {datasets.map(ds=> (
            <li key={ds.id} className="p-2 border-b flex justify-between items-center">
              <div>
                <div className="font-medium">{ds.dataset_name}</div>
                <div className="text-sm text-gray-500">{ds.uploaded_file_name}</div>
              </div>
              <div>
                <button onClick={()=>loadColumns(ds)} className="text-sm text-blue-600">View Columns</button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
