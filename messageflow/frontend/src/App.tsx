import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Datasets from './pages/Datasets'

export default function App(){
  return (
    <BrowserRouter>
      <div>
        <nav style={{padding:12}}>
          <Link to="/">Dashboard</Link> | <Link to="/datasets">Datasets</Link> | <Link to="/login">Login</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard/>} />
          <Route path="/datasets" element={<Datasets/>} />
          <Route path="/login" element={<Login/>} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
