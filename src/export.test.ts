import { describe, expect, it } from "vitest";
import type { Catedra } from "./types";
import { rangoHorario } from "./export";

const cat = (over: Partial<Catedra>): Catedra => ({
  id: "x",
  materiaId: "lengua-inglesa-1",
  turno: "mañana",
  anio: 1,
  clases: [],
  ...over,
});

describe("rangoHorario", () => {
  it("null cuando no hay clases", () => {
    expect(rangoHorario([])).toBeNull();
  });

  it("redondea a la hora el inicio más temprano y el fin más tardío", () => {
    const catedras = [
      cat({ clases: [{ dia: 1, inicio: "07:45", fin: "09:45", modalidad: "presencial" }] }),
      cat({ clases: [{ dia: 3, inicio: "20:00", fin: "22:40", modalidad: "asincronico" }] }),
    ];
    // 07:45 -> 07:00 (420) ; 22:40 -> 23:00 (1380)
    expect(rangoHorario(catedras)).toEqual({ min: 420, max: 1380 });
  });
});
