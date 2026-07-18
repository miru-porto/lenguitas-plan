// ============================================================================
// Modelo de dominio de Lenguitas-Plan
// ============================================================================
// Dos fuentes de datos se combinan acá:
//   - Horarios (PDFs TM/TV): cuándo y con quién se cursa cada comisión.
//   - Correlativas (PDF plan): qué hace falta para cursar/aprobar cada materia.
// La unidad que casa ambas fuentes es la MATERIA, identificada por un `id` slug.

export type Turno = "mañana" | "vespertino";

/** 1 = Lunes … 5 = Viernes */
export type DiaSemana = 1 | 2 | 3 | 4 | 5;

/**
 * Modalidad de una clase. Importa para superposiciones:
 * dos clases `asincronico` en la misma franja NO se pisan.
 */
export type Modalidad =
  | "presencial"
  | "sincronico"
  | "asincronico"
  | "bimodal";

/** Régimen de cursada de la materia. */
export type Regimen = "anual" | "cuatrimestral";

/** Campo de formación (según el plan de estudios). */
export type Campo = "CFE" | "CFPP" | "CFG" | "LE";

// ---------------------------------------------------------------------------
// Horarios
// ---------------------------------------------------------------------------

/** Un bloque de clase concreto (día + franja) dentro de una cátedra. */
export interface Clase {
  dia: DiaSemana;
  /** "HH:MM" */
  inicio: string;
  /** "HH:MM" */
  fin: string;
  modalidad: Modalidad;
  /** Texto crudo del paréntesis del grid, ej. "(25% sincrónico 25% asincrónico)". */
  nota?: string;
}

/**
 * Una cátedra = la unidad seleccionable: una materia dictada por un docente en un
 * turno/año/comisión, con sus clases. Dos cátedras de la MISMA materia son
 * alternativas (el estudiante elige una) y no se superponen entre sí.
 * Alinea con el concepto "cátedra = materia + profe" del proyecto rate-my-prof.
 */
export interface Catedra {
  id: string;
  materiaId: string;
  turno: Turno;
  /** 1..5 */
  anio: number;
  /** Grupo/cohorte del grid: "A" | "B" (o el espacio, en Trabajo de Campo). */
  comision?: string;
  docente?: string;
  clases: Clase[];
}

// ---------------------------------------------------------------------------
// Correlativas
// ---------------------------------------------------------------------------

/** Un requisito puede exigir la materia "en condición de final" o "aprobada". */
export type NivelCorrelativa = "final" | "aprobada";

export interface OpcionCorrelativa {
  materiaId: string;
  nivel: NivelCorrelativa;
}

/** Cláusula = OR de opciones ("Gramática 1 o Fonología 1"). */
export type Clausula = OpcionCorrelativa[];

/** Requisitos = AND de cláusulas. Lista vacía = sin requerimientos. */
export type Requisitos = Clausula[];

// ---------------------------------------------------------------------------
// Materia
// ---------------------------------------------------------------------------

export interface Materia {
  id: string;
  nombre: string;
  /** Año del plan de estudios (1..5). */
  anio: number;
  campo?: Campo;
  regimen?: Regimen;
  paraCursar: Requisitos;
  paraAprobar: Requisitos;
  /** Nota informativa (ej. cursada simultánea obligatoria). */
  nota?: string;
  /**
   * Id numérico de la materia en el proyecto "rate my prof" del profesorado.
   * Sirve para cruzar cátedras (materia + profe) entre ambos proyectos.
   */
  idExterno?: number;
}

// ---------------------------------------------------------------------------
// Estado del usuario (vive en localStorage / permalink, nunca en un servidor)
// ---------------------------------------------------------------------------

/**
 * Estado de una materia en el historial académico del estudiante.
 * El orden importa: "aprobada" satisface cualquier requisito de "final".
 */
export type EstadoMateria = "no-hecha" | "final" | "aprobada";
