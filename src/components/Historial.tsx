import type { EstadoMateria } from "../types";
import { materias } from "../data";

const OPCIONES: { valor: EstadoMateria; label: string }[] = [
  { valor: "no-hecha", label: "—" },
  { valor: "final", label: "En final" },
  { valor: "aprobada", label: "Aprobada" },
];

interface Props {
  historial: Record<string, EstadoMateria>;
  onSet: (materiaId: string, valor: EstadoMateria) => void;
}

export function Historial({ historial, onSet }: Props) {
  const anios = [1, 2, 3, 4, 5];
  return (
    <div className="historial">
      <p className="historial-ayuda">
        Marcá lo que ya cursaste o aprobaste. Eso habilita las materias que
        dependen de esas correlativas.
      </p>
      {anios.map((anio) => (
        <section key={anio} className="selector-anio">
          <h3>{anio}º año</h3>
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
                        onClick={() => onSet(m.id, op.valor)}
                      >
                        {op.label}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
        </section>
      ))}
    </div>
  );
}
