import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Header(){
  const { user, logout } = useAuth()
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-xl font-bold">MessageFlow</Link>
          <nav className="hidden md:flex gap-3 text-sm text-gray-600">
            <Link to="/datasets" className="hover:underline">Datasets</Link>
            <Link to="/templates" className="hover:underline">Templates</Link>
            <Link to="/campaigns/new" className="hover:underline">Campaigns</Link>
            <Link to="/inbox" className="hover:underline">Inbox</Link>
          </nav>
        </div>
        <div>
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700">{user.email}</span>
              <button onClick={logout} className="text-sm text-red-600">Logout</button>
            </div>
          ) : (
            <div className="flex gap-3">
              <Link to="/login" className="text-sm text-blue-600">Login</Link>
              <Link to="/register" className="text-sm text-gray-600">Register</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
