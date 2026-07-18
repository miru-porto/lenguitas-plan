import type { EstadoMateria, Materia } from "./types";
import { materias as todasLasMaterias } from "./data";

/**
 * Porcentaje de la carrera aprobado, por cantidad de materias:
 * materias aprobadas ÷ total de materias. Solo cuenta "aprobada" (no "en final").
 */
export function porcentajeCarrera(
  historial: Record<string, EstadoMateria>,
  lista: Materia[] = todasLasMaterias,
): number {
  if (lista.length === 0) return 0;
  const aprobadas = lista.filter((m) => historial[m.id] === "aprobada").length;
  return Math.round((aprobadas / lista.length) * 100);
}
