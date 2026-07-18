import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // Solo los tests del proyecto; ignora el clon de referencia FIUBA-Plan.
    include: ["src/**/*.test.ts"],
  },
});
