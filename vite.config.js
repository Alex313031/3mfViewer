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
    // same stable naming for the worker bundle, so it doesn't emit hashed
    // duplicates of lib3mf / the wasm alongside the main bundle's stable copies
    rollupOptions: {
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 2000,
    // Stable asset filenames (no content hash) so the vendored build doesn't churn
    // git on every rebuild: the committed parts/vendor/assets/ keeps the same names
    // and git shows content diffs instead of add/delete of hashed files. Trade-off:
    // no hash-based cache-busting - fine for a self-hosted, version-controlled viewer.
    rollupOptions: {
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
  logLevel: 'info',
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
})
