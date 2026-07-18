import { useState } from "react";
import type { Catedra } from "../types";
import { esCursable, type Historial } from "../logic";
import { catedras, materias, materiasOfrecidas, nombreDe } from "../data";
import { colorMateria } from "../color";
import type { FiltroTurno } from "../useEstado";

const DIAS_CORTO = ["", "Lun", "Mar", "Mié", "Jue", "Vie"];

function resumenHorario(c: Catedra): string {
  return c.clases
    .map((cl) => `${DIAS_CORTO[cl.dia]} ${cl.inicio}–${cl.fin}`)
    .join(" · ");
}

interface Props {
  seleccionadas: string[];
  historial: Historial;
  turno: FiltroTurno;
  onToggle: (catedraId: string) => void;
}

export function SelectorMaterias({
  seleccionadas,
  historial,
  turno,
  onToggle,
}: Props) {
  const [abierta, setAbierta] = useState<string | null>(null);

  const visibles = (materiaId: string) =>
    catedras.filter(
      (c) => c.materiaId === materiaId && (turno === "ambos" || c.turno === turno),
    );

  const anios = [1, 2, 3, 4, 5];

  return (
    <div className="selector">
      {anios.map((anio) => {
        const delAnio = materias.filter(
          (m) =>
            m.anio === anio &&
            materiasOfrecidas.has(m.id) &&
            visibles(m.id).length > 0,
        );
        if (delAnio.length === 0) return null;
        return (
          <section key={anio} className="selector-anio">
            <h3>{anio}º año</h3>
            {delAnio.map((m) => {
              const cur = esCursable(m, historial, nombreDe);
              const cats = visibles(m.id);
              const elegidasDeMateria = cats.filter((c) =>
                seleccionadas.includes(c.id),
              ).length;
              const expandida = abierta === m.id;
              return (
                <div
                  key={m.id}
                  className={`materia${cur.cursable ? "" : " materia-bloqueada"}`}
                >
                  <button
                    className="materia-cab"
                    title={cur.cursable ? "" : cur.motivo}
                    onClick={() => setAbierta(expandida ? null : m.id)}
                  >
                    <span
                      className="materia-color"
                      style={{ background: colorMateria(m.id) }}
                    />
                    <span className="materia-nombre">{m.nombre}</span>
                    {elegidasDeMateria > 0 && (
                      <span className="materia-badge">{elegidasDeMateria}</span>
                    )}
                    {!cur.cursable && <span className="materia-lock">🔒</span>}
                  </button>
                  {expandida && (
                    <ul className="catedras">
                      {!cur.cursable && (
                        <li className="catedra-aviso">{cur.motivo}</li>
                      )}
                      {cats.map((c) => {
                        const sel = seleccionadas.includes(c.id);
                        return (
                          <li key={c.id}>
                            <label className="catedra">
                              <input
                                type="checkbox"
                                checked={sel}
                                disabled={!cur.cursable && !sel}
                                onChange={() => onToggle(c.id)}
                              />
                              <span className="catedra-docente">
                                {c.docente ?? "—"}
                                {c.comision ? ` · ${c.comision}` : ""}
                                <span className="catedra-turno">{c.turno}</span>
                              </span>
                              <span className="catedra-horario">
                                {resumenHorario(c)}
                              </span>
                            </label>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              );
            })}
          </section>
        );
      })}
    </div>
  );
}
