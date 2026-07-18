import { useCallback, useEffect, useState } from "react";
import type { EstadoMateria, Turno } from "./types";

export type FiltroTurno = Turno | "ambos";

export interface EstadoApp {
  /** Ids de cátedras elegidas para el plan. */
  seleccionadas: string[];
  /** Historial académico: materiaId -> estado. */
  historial: Record<string, EstadoMateria>;
  turno: FiltroTurno;
}

const CLAVE = "lenguitas-plan";
const VACIO: EstadoApp = { seleccionadas: [], historial: {}, turno: "ambos" };

function leerDeHash(): EstadoApp | null {
  if (!window.location.hash) return null;
  try {
    const json = decodeURIComponent(escape(atob(window.location.hash.slice(1))));
    return { ...VACIO, ...JSON.parse(json) };
  } catch {
    return null;
  }
}

function leerDeStorage(): EstadoApp | null {
  try {
    const raw = window.localStorage.getItem(CLAVE);
    return raw ? { ...VACIO, ...JSON.parse(raw) } : null;
  } catch {
    return null;
  }
}

function aHash(estado: EstadoApp): string {
  return btoa(unescape(encodeURIComponent(JSON.stringify(estado))));
}

export function useEstado() {
  const [estado, setEstado] = useState<EstadoApp>(
    () => leerDeHash() ?? leerDeStorage() ?? VACIO,
  );

  // Si venimos de un permalink, limpiamos el hash una vez leído.
  useEffect(() => {
    if (window.location.hash) {
      history.replaceState("", "", window.location.pathname + window.location.search);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(CLAVE, JSON.stringify(estado));
  }, [estado]);

  const toggleCatedra = useCallback((id: string) => {
    setEstado((e) => ({
      ...e,
      seleccionadas: e.seleccionadas.includes(id)
        ? e.seleccionadas.filter((x) => x !== id)
        : [...e.seleccionadas, id],
    }));
  }, []);

  const setEstadoMateria = useCallback(
    (materiaId: string, valor: EstadoMateria) => {
      setEstado((e) => {
        const historial = { ...e.historial };
        if (valor === "no-hecha") delete historial[materiaId];
        else historial[materiaId] = valor;
        return { ...e, historial };
      });
    },
    [],
  );

  const setTurno = useCallback((turno: FiltroTurno) => {
    setEstado((e) => ({ ...e, turno }));
  }, []);

  const limpiar = useCallback(() => setEstado(VACIO), []);

  const permalink = useCallback(
    () => `${window.location.origin}${window.location.pathname}#${aHash(estado)}`,
    [estado],
  );

  return {
    estado,
    toggleCatedra,
    setEstadoMateria,
    setTurno,
    limpiar,
    permalink,
  };
}
