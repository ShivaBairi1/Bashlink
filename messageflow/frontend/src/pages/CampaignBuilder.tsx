import React, { useEffect, useState } from 'react'
import api from '../api'

export default function CampaignBuilder(){
  const [templates, setTemplates] = useState<any[]>([])
  const [datasets] = useState(() => { try{ const raw = localStorage.getItem('mf_datasets'); return raw ? JSON.parse(raw) : [] }catch{ return [] } })
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [selectedDataset, setSelectedDataset] = useState<string | null>(datasets?.[0]?.id || null)
  const [campaignName, setCampaignName] = useState('')
  const [preview, setPreview] = useState<any[]>([])

  useEffect(()=>{
    async function load(){
      try{ const res = await api.get('/templates'); setTemplates(res.data) }catch{} }
    load()
  },[])

  async function create(){
    try{
      const res = await api.post('/campaigns', { campaign_name: campaignName, template_id: selectedTemplate, dataset_id: selectedDataset })
      alert('Campaign created')
    }catch(err:any){ alert('Create failed') }
  }

  async function previewCampaign(){
    try{
      // need a campaign to preview; create temp campaign
      const res = await api.post('/campaigns', { campaign_name: campaignName || 'preview', template_id: selectedTemplate, dataset_id: selectedDataset })
      const id = res.data.id
      const pre = await api.get(`/campaigns/${id}/preview`)
      setPreview(pre.data.preview)
    }catch(err:any){ alert('Preview failed') }
  }

  async function send(){
    try{
      // create campaign then send
      const res = await api.post('/campaigns', { campaign_name: campaignName || 'campaign', template_id: selectedTemplate, dataset_id: selectedDataset })
      const id = res.data.id
      await api.post(`/campaigns/${id}/send`)
      alert('Campaign sent (enqueued)')
    }catch(err:any){ alert('Send failed') }
  }

  return (
    <div className="bg-white p-6 rounded shadow">
      <h2 className="text-lg font-semibold">Campaign Builder</h2>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-2">
          <div>
            <label className="block text-sm">Campaign Name</label>
            <input value={campaignName} onChange={e=>setCampaignName(e.target.value)} className="w-full border p-2 rounded" />
          </div>
          <div className="mt-3">
            <label className="block text-sm">Template</label>
            <select className="w-full border p-2 rounded" value={selectedTemplate||''} onChange={e=>setSelectedTemplate(e.target.value||null)}>
              <option value="">-- select template --</option>
              {templates.map(t=>(<option key={t.id} value={t.id}>{t.template_name} ({t.channel})</option>))}
            </select>
          </div>
          <div className="mt-3">
            <label className="block text-sm">Dataset</label>
            <select className="w-full border p-2 rounded" value={selectedDataset||''} onChange={e=>setSelectedDataset(e.target.value||null)}>
              <option value="">-- select dataset --</option>
              {datasets.map((d:any)=> <option key={d.id} value={d.id}>{d.dataset_name}</option>)}
            </select>
          </div>
          <div className="mt-4 flex gap-3">
            <button onClick={previewCampaign} className="px-4 py-2 bg-yellow-500 text-white rounded">Preview</button>
            <button onClick={send} className="px-4 py-2 bg-green-600 text-white rounded">Send</button>
          </div>
        </div>
        <div>
          <h4 className="font-semibold">Preview</h4>
          <div className="mt-2 max-h-64 overflow-auto">
            {preview.map(p=>(
              <div key={p.customer_id} className="p-2 border-b">{p.message}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
