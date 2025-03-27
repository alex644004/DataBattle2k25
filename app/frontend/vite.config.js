import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // Permet d'écouter sur toutes les interfaces
    port: 5173,       // Assure que le port 5173 est utilisé
    strictPort: true, // Empêche Vite de changer le port s'il est déjà pris
    watch: {
      usePolling: true, // Nécessaire dans Docker pour détecter les changements de fichiers
    }
  }
})
