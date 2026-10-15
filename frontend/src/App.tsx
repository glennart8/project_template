import { useEffect, useState } from 'react'

type User = { username: string; name: string }

// Hämtar den inloggade användaren via /api — samma adress i utveckling
// (Vite-proxyn) och i drift (Caddy).
function App() {
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/me')
      .then((response) => (response.ok ? response.json() : Promise.reject(response.status)))
      .then(setUser)
      .catch((status) => setError(`Inte inloggad (${status})`))
  }, [])

  return (
    <main>
      <h1>Projektnamn</h1>
      {user && <p>Inloggad som {user.name || user.username}</p>}
      {error && <p>{error}</p>}
    </main>
  )
}

export default App
