import type { EstadoMateria } from "../types";
import { materias } from "../data";
import { porcentajeCarrera } from "../progreso";

const OPCIONES: { valor: EstadoMateria; label: string }[] = [
  { valor: "final", label: "En final" },
  { valor: "aprobada", label: "Aprobada" },
];

interface Props {
  historial: Record<string, EstadoMateria>;
  onSet: (materiaId: string, valor: EstadoMateria) => void;
  onSetMuchas: (materiaIds: string[], valor: EstadoMateria) => void;
}

export function Historial({ historial, onSet, onSetMuchas }: Props) {
  const anios = [1, 2, 3, 4, 5];
  const pct = porcentajeCarrera(historial);
  return (
    <div className="historial">
      <div className="progreso">
        <div className="progreso-cab">
          <span>Porcentaje de la carrera:</span>
          <strong>{pct}%</strong>
        </div>
        <div className="progreso-barra">
          <div className="progreso-relleno" style={{ width: `${pct}%` }} />
        </div>
      </div>
      <p className="historial-ayuda">
        Marcá lo que ya cursaste o aprobaste. Eso habilita las materias que
        dependen de esas correlativas.
      </p>
      {anios.map((anio) => {
        const idsAnio = materias
          .filter((m) => m.anio === anio)
          .map((m) => m.id);
        const todasAprobadas = idsAnio.every(
          (id) => historial[id] === "aprobada",
        );
        return (
          <section key={anio} className="selector-anio">
            <div className="historial-anio-cab">
              <h3>{anio}º año</h3>
              <label className="historial-todas" title="Marcar todo el año como aprobado">
                <input
                  type="checkbox"
                  checked={todasAprobadas}
                  onChange={(e) =>
                    onSetMuchas(idsAnio, e.target.checked ? "aprobada" : "no-hecha")
                  }
                />
                Todas aprobadas
              </label>
            </div>
            {materias
              .filter((m) => m.anio === anio)
              .map((m) => {
                const actual = historial[m.id] ?? "no-hecha";
                return (
                  <div key={m.id} className="historial-fila">
                    <span className="historial-nombre">{m.nombre}</span>
                    <div className="historial-opciones">
                      {OPCIONES.map((op) => (
                        <button
                          key={op.valor}
                          className={`hist-btn${
                            actual === op.valor ? " hist-btn-activo" : ""
                          }`}
                          onClick={() =>
                            onSet(m.id, actual === op.valor ? "no-hecha" : op.valor)
                          }
                        >
                          {op.label}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
          </section>
        );
      })}
    </div>
  );
}
