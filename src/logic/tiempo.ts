/** Utilidades de tiempo para las franjas "HH:MM". */

export function aMinutos(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

/** true si dos rangos [aIni,aFin) y [bIni,bFin) se solapan (bordes que se tocan NO). */
export function rangosSeSolapan(
  aIni: string,
  aFin: string,
  bIni: string,
  bFin: string,
): boolean {
  return aMinutos(aIni) < aMinutos(bFin) && aMinutos(bIni) < aMinutos(aFin);
}

export const maxHora = (a: string, b: string): string =>
  aMinutos(a) >= aMinutos(b) ? a : b;

export const minHora = (a: string, b: string): string =>
  aMinutos(a) <= aMinutos(b) ? a : b;
