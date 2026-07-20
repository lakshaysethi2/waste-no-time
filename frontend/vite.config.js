import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: [
      'react-dom/client',
      'react-dom',
      'react',
      'react-router-dom',
      'react-bootstrap',
      'react-google-charts',
      'react-telegram-login',
      'bootstrap',
      'axios'
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true
    }
  }
})
