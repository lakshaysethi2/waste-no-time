import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      include: '**/*.{jsx,js}',
    }),
  ],
  base: '/static/',
  build: {
    outDir: 'dist',
    assetsDir: '',
  },
  optimizeDeps: {
    include: [
      'react-dom/client',
      'react-dom',
      'react',
      'react-router-dom',
      'react-bootstrap',
      'react-google-charts',
      'bootstrap',
      'axios'
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
    watch: {
      usePolling: true
    }
  }
})
