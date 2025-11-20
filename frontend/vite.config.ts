import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
//import { componentTagger } from "@devvai/devv-tagger-plugin"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],  //  componentTagger()
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Use Vite's built-in content hashing (no Date.now() to avoid Docker cache issues)
        entryFileNames: `assets/[name]-[hash].js`,
        chunkFileNames: `assets/[name]-[hash].js`,
        assetFileNames: `assets/[name]-[hash].[ext]`
      }
    }
  }
})