import type { Catedra, Clase } from "../types";
import { maxHora, minHora, rangosSeSolapan } from "./tiempo";

/**
 * ¿Dos clases se pisan? Reglas:
 *  - Distinto día → no.
 *  - Alguna asincrónica → no (no ocupa una franja fija).
 *  - Mismo día y horarios solapados → sí.
 */
export function clasesSeSuperponen(a: Clase, b: Clase): boolean {
  if (a.dia !== b.dia) return false;
  if (a.modalidad === "asincronico" || b.modalidad === "asincronico") return false;
  return rangosSeSolapan(a.inicio, a.fin, b.inicio, b.fin);
}

export interface Conflicto {
  a: Catedra;
  b: Catedra;
  dia: Clase["dia"];
  /** Ventana efectivamente solapada. */
  inicio: string;
  fin: string;
}

/**
 * Detecta las superposiciones entre un conjunto de cátedras elegidas.
 * Dos cátedras de la MISMA materia son alternativas: nunca se consideran choque
 * entre sí (el estudiante elige una).
 */
export function detectarSuperposiciones(catedras: Catedra[]): Conflicto[] {
  const conflictos: Conflicto[] = [];
  for (let i = 0; i < catedras.length; i++) {
    for (let j = i + 1; j < catedras.length; j++) {
      const A = catedras[i];
      const B = catedras[j];
      if (A.materiaId === B.materiaId) continue; // alternativas de la misma materia
      for (const ca of A.clases) {
        for (const cb of B.clases) {
          if (clasesSeSuperponen(ca, cb)) {
            conflictos.push({
              a: A,
              b: B,
              dia: ca.dia,
              inicio: maxHora(ca.inicio, cb.inicio),
              fin: minHora(ca.fin, cb.fin),
            });
          }
        }
      }
    }
  }
  return conflictos;
}

/** Conflictos que una cátedra tendría contra un conjunto ya elegido. */
export function conflictosContra(
  catedra: Catedra,
  seleccionadas: Catedra[],
): Conflicto[] {
  return detectarSuperposiciones([catedra, ...seleccionadas]).filter(
    (c) => c.a.id === catedra.id || c.b.id === catedra.id,
  );
}
