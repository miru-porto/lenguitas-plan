import { describe, expect, it } from "vitest";
import type { Materia } from "../types";
import { esCursable, evaluarRequisitos } from "./correlativas";

const nombreDe = (id: string) => id;

const materia = (
  id: string,
  paraCursar: Materia["paraCursar"],
): Materia => ({
  id,
  nombre: id,
  anio: 2,
  paraCursar,
  paraAprobar: [],
});

// Lengua Inglesa 2: LI1 en final Y (Gramática 1 O Fonología 1) en final.
const lengua2 = materia("lengua-inglesa-2", [
  [{ materiaId: "lengua-inglesa-1", nivel: "final" }],
  [
    { materiaId: "gramatica-1", nivel: "final" },
    { materiaId: "fonologia-1", nivel: "final" },
  ],
]);

describe("esCursable", () => {
  it("sin requerimientos siempre es cursable", () => {
    const taller1 = materia("taller-1", []);
    expect(esCursable(taller1, {}, nombreDe).cursable).toBe(true);
  });

  it("no cursable si falta una cláusula, con motivo explicativo", () => {
    const r = esCursable(lengua2, { "lengua-inglesa-1": "final" }, nombreDe);
    expect(r.cursable).toBe(false);
    expect(r.motivo).toContain("gramatica-1 o fonologia-1");
    expect(r.motivo).toContain("en final");
  });

  it("cursable cuando se cumplen todas las cláusulas", () => {
    const h = { "lengua-inglesa-1": "final", "fonologia-1": "final" } as const;
    expect(esCursable(lengua2, h, nombreDe).cursable).toBe(true);
  });

  it("la cláusula OR se satisface con cualquiera de las opciones", () => {
    const h = { "lengua-inglesa-1": "final", "gramatica-1": "final" } as const;
    expect(esCursable(lengua2, h, nombreDe).cursable).toBe(true);
  });

  it("'aprobada' satisface un requisito de 'final'", () => {
    const h = { "lengua-inglesa-1": "aprobada", "fonologia-1": "aprobada" } as const;
    expect(esCursable(lengua2, h, nombreDe).cursable).toBe(true);
  });

  it("'final' NO satisface un requisito de 'aprobada'", () => {
    const m = materia("x", [[{ materiaId: "y", nivel: "aprobada" }]]);
    expect(evaluarRequisitos(m.paraCursar, { y: "final" }).cumple).toBe(false);
    expect(evaluarRequisitos(m.paraCursar, { y: "aprobada" }).cumple).toBe(true);
  });
});
