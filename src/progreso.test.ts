import { describe, expect, it } from "vitest";
import type { EstadoMateria, Materia } from "./types";
import { porcentajeCarrera } from "./progreso";

// Plan de prueba: 2 años, con distinta cantidad de materias por año.
const lista: Materia[] = [
  { id: "a1", nombre: "A1", anio: 1, paraCursar: [], paraAprobar: [] },
  { id: "a2", nombre: "A2", anio: 1, paraCursar: [], paraAprobar: [] },
  { id: "b1", nombre: "B1", anio: 2, paraCursar: [], paraAprobar: [] },
];

const ap = (...ids: string[]): Record<string, EstadoMateria> =>
  Object.fromEntries(ids.map((id) => [id, "aprobada"]));

describe("porcentajeCarrera", () => {
  it("0% sin nada aprobado", () => {
    expect(porcentajeCarrera({}, lista)).toBe(0);
  });

  it("cada año pesa igual: todo 1º año = 50% (con 2 años)", () => {
    expect(porcentajeCarrera(ap("a1", "a2"), lista)).toBe(50);
  });

  it("toda la carrera aprobada = 100%", () => {
    expect(porcentajeCarrera(ap("a1", "a2", "b1"), lista)).toBe(100);
  });

  it("'en final' no cuenta, solo 'aprobada'", () => {
    expect(porcentajeCarrera({ a1: "final", a2: "final" }, lista)).toBe(0);
  });
});
