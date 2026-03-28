import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const workspaceRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "..");

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      allow: [workspaceRoot],
    },
    proxy: {
      "/api": "http://127.0.0.1:5000",
      "/run-job": "http://127.0.0.1:5000",
    },
  },
});
