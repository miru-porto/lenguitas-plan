import { describe, expect, it } from "vitest";
import type { Catedra, Clase, Modalidad } from "../types";
import { conflictosContra, detectarSuperposiciones } from "./superposiciones";

const clase = (
  dia: Clase["dia"],
  inicio: string,
  fin: string,
  modalidad: Modalidad = "presencial",
): Clase => ({ dia, inicio, fin, modalidad });

const catedra = (
  id: string,
  materiaId: string,
  clases: Clase[],
): Catedra => ({
  id,
  materiaId,
  turno: "vespertino",
  anio: 1,
  clases,
});

describe("detectarSuperposiciones", () => {
  it("dos materias distintas en el mismo horario chocan", () => {
    const a = catedra("a", "mat-a", [clase(2, "18:00", "20:00")]);
    const b = catedra("b", "mat-b", [clase(2, "19:00", "21:00")]);
    const conf = detectarSuperposiciones([a, b]);
    expect(conf).toHaveLength(1);
    expect(conf[0]).toMatchObject({ dia: 2, inicio: "19:00", fin: "20:00" });
  });

  it("dos cátedras de la MISMA materia no chocan (son alternativas)", () => {
    const a = catedra("a", "fonologia-1", [clase(1, "19:20", "22:40")]);
    const b = catedra("b", "fonologia-1", [clase(1, "19:20", "22:40")]);
    expect(detectarSuperposiciones([a, b])).toHaveLength(0);
  });

  it("una clase asincrónica nunca choca", () => {
    const a = catedra("a", "mat-a", [clase(5, "20:00", "22:40", "asincronico")]);
    const b = catedra("b", "mat-b", [clase(5, "20:00", "22:40")]);
    expect(detectarSuperposiciones([a, b])).toHaveLength(0);
  });

  it("franjas que se tocan en el borde no chocan", () => {
    const a = catedra("a", "mat-a", [clase(3, "18:00", "18:40")]);
    const b = catedra("b", "mat-b", [clase(3, "18:40", "19:20")]);
    expect(detectarSuperposiciones([a, b])).toHaveLength(0);
  });

  it("distinto día no choca", () => {
    const a = catedra("a", "mat-a", [clase(1, "18:00", "20:00")]);
    const b = catedra("b", "mat-b", [clase(2, "18:00", "20:00")]);
    expect(detectarSuperposiciones([a, b])).toHaveLength(0);
  });

  it("conflictosContra reporta solo los choques de la cátedra candidata", () => {
    const elegidas = [
      catedra("a", "mat-a", [clase(2, "18:00", "20:00")]),
      catedra("b", "mat-b", [clase(4, "18:00", "20:00")]),
    ];
    const candidata = catedra("c", "mat-c", [clase(2, "19:00", "21:00")]);
    const conf = conflictosContra(candidata, elegidas);
    expect(conf).toHaveLength(1);
    expect(conf[0].b.id === "c" || conf[0].a.id === "c").toBe(true);
  });
});
