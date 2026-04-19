import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    hmr: {
      clientPort: 5173
    },
    watch: {
      usePolling: true,
      interval: 100
    },
    proxy: {
      '/api': {
        target: 'http://api:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        // Добавьте эти настройки:
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,PATCH,OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
      },
      '/minio': {
        target: 'http://image-db:9000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/minio/, '')
      },
      '/user-': { 
        target: 'http://image-db:9000',
        changeOrigin: true
      }
    }
  },
  define: {
    __VUE_PROD_DEVTOOLS__: true,
    'process.env.VITE_MINIO_PUBLIC_URL': JSON.stringify(
      process.env.NODE_ENV === 'production' 
        ? 'https://your-production-domain.com/minio' 
        : process.env.VITE_MINIO_PUBLIC_URL
    )
  }
})