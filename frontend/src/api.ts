// Allt frontend vet om API:et. Typerna speglar backend/schemas.py och auth.py —
// ändras ett schema där, ändras typen här.

export type User = { username: string; name: string; roles: string[] }

export type Note = { id: string; text: string; created_by: string; created_at: string }

export type NoteCreate = { text: string }

// Backend svarar {"detail": "..."} vid fel; meddelandet går att visa som det är.
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `Fel ${response.status}`)
  }
  return response.status === 204 ? (undefined as T) : response.json()
}

export const getMe = () => request<User>('/me')
export const listNotes = () => request<Note[]>('/notes')
export const createNote = (data: NoteCreate) =>
  request<Note>('/notes', { method: 'POST', body: JSON.stringify(data) })
export const deleteNote = (id: string) => request<void>(`/notes/${id}`, { method: 'DELETE' })
