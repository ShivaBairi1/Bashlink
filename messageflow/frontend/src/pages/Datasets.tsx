import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function Datasets(){
  const [datasets, setDatasets] = useState<any[]>([])

  useEffect(()=>{
    async function load(){
      try{
        const res = await axios.get('/api/datasets')
        setDatasets(res.data)
      }catch(e){
        // ignore
      }
    }
    load()
  },[])

  return (
    <div style={{padding:20}}>
      <h2>Datasets</h2>
      <ul>
        {datasets.map(ds=>(<li key={ds.id}>{ds.dataset_name}</li>))}
      </ul>
    </div>
  )
}
