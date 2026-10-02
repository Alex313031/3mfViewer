import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import pkg from './package.json' with { type: 'json' }

// https://vite.dev/config/
export default defineConfig({
  // Relative base so the built viewer works under any subpath (e.g.
  // thorium.rocks/kirby_history/parts/vendor/3mfViewer/) as well as at the
  // domain root. Asset/worker/wasm URLs resolve relative to the viewer's own
  // folder via import.meta.url instead of the server root.
  base: './',
  plugins: [react(), tailwindcss()],
  worker: {
    format: 'es',
  },
  build: {
    chunkSizeWarningLimit: 2000,
  },
  logLevel: 'info',
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
})
