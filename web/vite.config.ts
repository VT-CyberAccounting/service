import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'https://cyberacc.discovery.cs.vt.edu',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})