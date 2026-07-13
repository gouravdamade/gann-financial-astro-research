import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiTarget = process.env.GANN_ASTRO_API_TARGET || 'http://127.0.0.1:8788'

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: false,
      },
      '/codex-api': {
        target: 'http://127.0.0.1:8789',
        changeOrigin: false,
        rewrite: (path) => path.replace(/^\/codex-api/, ''),
      },
    },
  },
})
