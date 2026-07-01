import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import Login from './routes/Login'
import Dashboard from './routes/Dashboard'
import { isAuthenticated } from './api'

function Root() {
  const [authenticated, setauthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    isAuthenticated()
      .then((ok) => {
        if (!cancelled) setauthenticated(ok)
      })
      .catch(() => {
        if (!cancelled) setauthenticated(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (authenticated === null) return null
  return authenticated ? <Dashboard /> : <Login />
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors closeButton />
      <Routes>
        <Route path="/" element={<Root />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}