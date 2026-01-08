import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Оптимизация размера бандла
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'antd-vendor': ['antd', '@ant-design/icons'],
          'three-vendor': ['three'],
        },
      },
    },
    // Увеличение лимита предупреждений о размере чанка для production
    chunkSizeWarningLimit: 1000,
    // Минификация
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Удаление console.log в production
      },
    },
  },
  // Оптимизация зависимостей
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'antd'],
  },
})
