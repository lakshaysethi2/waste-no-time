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
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
