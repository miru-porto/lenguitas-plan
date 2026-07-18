import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El base se ajusta para deploy en GitHub Pages (https://<user>.github.io/lenguitas-plan/).
// Para dev local ("serve"), "/" está bien.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === "build" ? "/lenguitas-plan/" : "/",
}));
