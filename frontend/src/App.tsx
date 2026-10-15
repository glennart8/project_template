import { useEffect, useState, type FormEvent } from 'react'
import { createNote, deleteNote, getMe, listNotes, type Note, type User } from './api'

// Exemplet notes från gränssnittet: läsa, skapa och — för admin — ta bort.
// Alla regler finns i backend; här visas bara det backend svarar.
function App() {
  const [user, setUser] = useState<User | null>(null)
  const [notes, setNotes] = useState<Note[]>([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  const run = (action: () => Promise<void>) =>
    action()
      .then(() => setError(''))
      .catch((e: Error) => setError(e.message))

  const reload = () => listNotes().then(setNotes)

  useEffect(() => {
    run(() => getMe().then(setUser).then(reload))
  }, [])

  const add = (event: FormEvent) => {
    event.preventDefault()
    run(() => createNote({ text }).then(() => setText('')).then(reload))
  }

  const isAdmin = user?.roles.includes('admin') ?? false

  return (
    <main>
      <h1>Projektnamn</h1>
      {user && <p>Inloggad som {user.name || user.username}</p>}
      {error && <p role="alert">{error}</p>}

      <form onSubmit={add}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ny anteckning" />
        <button>Spara</button>
      </form>

      <ul>
        {notes.map((note) => (
          <li key={note.id}>
            {note.text} <small>— {note.created_by}</small>{' '}
            {isAdmin && <button onClick={() => run(() => deleteNote(note.id).then(reload))}>Ta bort</button>}
          </li>
        ))}
      </ul>
    </main>
  )
}

export default App
