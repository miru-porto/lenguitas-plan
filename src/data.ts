import type { Catedra, Materia } from "./types";
import materiasJson from "../data/materias.json";
import horariosJson from "../data/horarios.json";

export const materias = (materiasJson as unknown as { materias: Materia[] }).materias;
export const catedras = (horariosJson as unknown as { catedras: Catedra[] }).catedras;

const porId = new Map(materias.map((m) => [m.id, m]));
export const materiaPorId = (id: string): Materia | undefined => porId.get(id);
export const nombreDe = (id: string): string => porId.get(id)?.nombre ?? id;

/** Cátedras de una materia (sus alternativas de docente/comisión). */
export function catedrasDeMateria(materiaId: string): Catedra[] {
  return catedras.filter((c) => c.materiaId === materiaId);
}

/** Ids de materias que tienen al menos una cátedra ofrecida. */
export const materiasOfrecidas = new Set(catedras.map((c) => c.materiaId));
