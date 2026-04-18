import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [username, setUsername] = useState('')
  const navigate = useNavigate()

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    const name = username.trim()
    if (!name) return
    navigate(`/user/${encodeURIComponent(name)}`)
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-neutral-50">
      <form
        onSubmit={submit}
        className="w-80 flex flex-col gap-4 p-8 rounded-lg border border-neutral-200 bg-white shadow-sm"
      >
        <h1 className="text-xl font-semibold text-neutral-900">Sign in</h1>
        <input
          autoFocus
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="px-3 py-2 rounded border border-neutral-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
        />
        <button
          type="submit"
          className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700 disabled:opacity-50"
          disabled={!username.trim()}
        >
          Continue
        </button>
      </form>
    </main>
  )
}