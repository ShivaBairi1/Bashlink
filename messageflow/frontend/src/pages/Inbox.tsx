import React, { useEffect, useState } from 'react'
import api from '../api'

export default function Inbox(){
  const [conversations, setConversations] = useState<any[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [reply, setReply] = useState('')

  useEffect(()=>{ loadInbox() },[])

  async function loadInbox(){
    try{ const res = await api.get('/inbox'); setConversations(res.data) }catch(e){ }
  }

  async function openConversation(customer_id:string){
    setSelected(customer_id)
    try{
      const res = await api.get(`/inbox/conversations/${customer_id}`)
      setMessages(res.data)
    }catch(e){ alert('Failed to load conversation') }
  }

  async function sendReply(){
    if(!selected) return
    try{
      await api.post('/inbox/reply', null, { params: { customer_id: selected, message_text: reply } })
      setReply('')
      openConversation(selected)
    }catch(e){ alert('Reply failed') }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="col-span-1 bg-white p-4 rounded shadow">
        <h3 className="font-semibold">Conversations</h3>
        <ul className="mt-3 space-y-2">
          {conversations.map(c=>(
            <li key={c.id} className="p-2 border-b cursor-pointer" onClick={()=>openConversation(c.customer_record_id)}>
              <div className="text-sm">{c.customer_record_id}</div>
              <div className="text-xs text-gray-500">{c.generated_message?.slice(0,60)}</div>
            </li>
          ))}
        </ul>
      </div>
      <div className="col-span-3 bg-white p-4 rounded shadow">
        <h3 className="font-semibold">Conversation</h3>
        <div className="mt-3 h-96 overflow-auto border p-2">
          {messages.map((m,i)=>(
            <div key={i} className={`p-2 my-2 ${m.type==='incoming' ? 'bg-gray-100 self-start':''}`}>
              <div className="text-sm">{m.text}</div>
              <div className="text-xs text-gray-400">{new Date(m.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
        <div className="mt-3 flex gap-2">
          <input value={reply} onChange={e=>setReply(e.target.value)} className="flex-1 border p-2 rounded" />
          <button onClick={sendReply} className="px-4 py-2 bg-blue-600 text-white rounded">Reply</button>
        </div>
      </div>
    </div>
  )
}
