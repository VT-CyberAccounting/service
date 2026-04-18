import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/submission': {
        target: 'https://cyberacc.cs.vt.edu',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})