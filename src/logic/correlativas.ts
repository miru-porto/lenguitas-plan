import type {
  Clausula,
  EstadoMateria,
  Materia,
  OpcionCorrelativa,
  Requisitos,
} from "../types";

/** Historial del estudiante: qué tiene hecho de cada materia (por id). */
export type Historial = Record<string, EstadoMateria>;

/** Orden de estados: aprobada satisface cualquier requisito de final. */
const RANK: Record<EstadoMateria, number> = {
  "no-hecha": 0,
  final: 1,
  aprobada: 2,
};
const RANK_REQUERIDO = { final: 1, aprobada: 2 } as const;

export function cumpleOpcion(op: OpcionCorrelativa, h: Historial): boolean {
  const estado = h[op.materiaId] ?? "no-hecha";
  return RANK[estado] >= RANK_REQUERIDO[op.nivel];
}

/** Una cláusula (OR de opciones) se cumple si alguna opción se cumple. */
export function cumpleClausula(cl: Clausula, h: Historial): boolean {
  return cl.some((op) => cumpleOpcion(op, h));
}

export interface ResultadoRequisitos {
  cumple: boolean;
  /** Cláusulas que faltan satisfacer (para explicar el bloqueo). */
  faltantes: Clausula[];
}

/** Evalúa un AND de cláusulas contra el historial. */
export function evaluarRequisitos(
  reqs: Requisitos,
  h: Historial,
): ResultadoRequisitos {
  const faltantes = reqs.filter((cl) => !cumpleClausula(cl, h));
  return { cumple: faltantes.length === 0, faltantes };
}

export interface Cursabilidad {
  cursable: boolean;
  faltantes: Clausula[];
  /** Texto para el tooltip cuando no es cursable. */
  motivo?: string;
}

/**
 * ¿La materia es cursable según el historial? Como seleccionar una materia para el
 * cuatrimestre actual NO la agrega al historial, su cadena de correlativas queda
 * bloqueada hasta marcarla como hecha (bloqueo transitivo, sin lógica extra).
 */
export function esCursable(
  materia: Materia,
  historial: Historial,
  nombreDe: (id: string) => string,
): Cursabilidad {
  const { cumple, faltantes } = evaluarRequisitos(materia.paraCursar, historial);
  if (cumple) return { cursable: true, faltantes: [] };
  return { cursable: false, faltantes, motivo: motivoTexto(faltantes, nombreDe) };
}

function motivoTexto(
  faltantes: Clausula[],
  nombreDe: (id: string) => string,
): string {
  const partes = faltantes.map((cl) => {
    const nivel = cl[0]?.nivel === "aprobada" ? "aprobada" : "en final";
    const nombres = cl.map((op) => nombreDe(op.materiaId)).join(" o ");
    return `${nombres} (${nivel})`;
  });
  return "Requiere: " + partes.join("; ");
}
