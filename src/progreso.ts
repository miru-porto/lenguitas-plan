import type { EstadoMateria, Materia } from "./types";
import { materias as todasLasMaterias } from "./data";

/**
 * Porcentaje de la carrera aprobado. Cada año pesa igual (5 años → 20% c/u); dentro
 * de cada año cuenta la fracción de materias aprobadas. Así, todo 1º año = 20% y
 * toda la carrera = 100%. Solo cuenta "aprobada" (no "en final").
 */
export function porcentajeCarrera(
  historial: Record<string, EstadoMateria>,
  lista: Materia[] = todasLasMaterias,
): number {
  const anios = [...new Set(lista.map((m) => m.anio))];
  const fraccion = anios.reduce((acc, anio) => {
    const delAnio = lista.filter((m) => m.anio === anio);
    if (delAnio.length === 0) return acc;
    const aprobadas = delAnio.filter(
      (m) => historial[m.id] === "aprobada",
    ).length;
    return acc + aprobadas / delAnio.length / anios.length;
  }, 0);
  return Math.round(fraccion * 100);
}
