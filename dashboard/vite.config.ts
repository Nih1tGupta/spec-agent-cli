import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

// Build static assets into the Python package so `spec-agent ui` serves them
// with no Node runtime dependency for end users.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: path.resolve(rootDir, "../src/spec_agent/ui_assets"),
    emptyOutDir: true,
    assetsDir: "assets",
    sourcemap: false,
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:53518",
      "/ui_assets": "http://127.0.0.1:53518",
    },
  },
});
