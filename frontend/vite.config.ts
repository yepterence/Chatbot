import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'

// https://vite.dev/config/
export default defineConfig({
  base: './', // needed for electron to work
  plugins: [react(), electron({
      entry: "electron/main.ts",
    }),
  ],
});
