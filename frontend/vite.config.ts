import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const apiBase = env.VITE_API_BASE_URL || '';
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': 'http://127.0.0.1:8000',
      },
    },
    define: {
      __API_BASE__: JSON.stringify(apiBase),
    },
  };
});
