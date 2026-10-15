import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /api skickas till backend, precis som nginx gör i drift. Samma adress för
// frontend och API gör att ingen CORS behövs.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
