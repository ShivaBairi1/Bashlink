import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Datasets from './pages/Datasets'
import Templates from './pages/Templates'
import TemplateEditor from './pages/TemplateEditor'
import CampaignBuilder from './pages/CampaignBuilder'
import Inbox from './pages/Inbox'
import { AuthProvider } from './auth/AuthContext'
import Header from './components/Header'

export default function App(){
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100">
          <Header />
          <div className="container mx-auto p-4">
            <Routes>
              <Route path="/" element={<Dashboard/>} />
              <Route path="/login" element={<Login/>} />
              <Route path="/register" element={<Register/>} />
              <Route path="/datasets" element={<Datasets/>} />
              <Route path="/templates" element={<Templates/>} />
              <Route path="/templates/new" element={<TemplateEditor/>} />
              <Route path="/campaigns/new" element={<CampaignBuilder/>} />
              <Route path="/inbox" element={<Inbox/>} />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}
