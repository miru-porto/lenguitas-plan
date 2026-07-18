import type { Catedra } from "../types";
import type { Conflicto } from "../logic";
import { aMinutos } from "../logic";
import { colorMateria } from "../color";
import { nombreDe } from "../data";

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];
const PX_POR_MIN = 0.9;

interface Props {
  seleccionadas: Catedra[];
  conflictos: Conflicto[];
  onQuitar: (catedraId: string) => void;
}

export function Grilla({ seleccionadas, conflictos, onQuitar }: Props) {
  const clases = seleccionadas.flatMap((c) =>
    c.clases.map((cl) => ({ catedra: c, clase: cl })),
  );

  if (clases.length === 0) {
    return (
      <div className="grilla-vacia">
        Elegí materias de la lista para ver tu semana acá.
      </div>
    );
  }

  const inicios = clases.map((x) => aMinutos(x.clase.inicio));
  const fines = clases.map((x) => aMinutos(x.clase.fin));
  const min = Math.floor(Math.min(...inicios) / 60) * 60;
  const max = Math.ceil(Math.max(...fines) / 60) * 60;
  const altura = (max - min) * PX_POR_MIN;

  const horas: number[] = [];
  for (let h = min; h <= max; h += 60) horas.push(h);

  const enConflicto = (catedraId: string, dia: number) =>
    conflictos.some(
      (cf) =>
        cf.dia === dia && (cf.a.id === catedraId || cf.b.id === catedraId),
    );

  return (
    <div className="grilla" style={{ height: altura + 30 }}>
      <div className="grilla-horas">
        {horas.map((h) => (
          <div
            key={h}
            className="grilla-hora"
            style={{ top: (h - min) * PX_POR_MIN + 30 }}
          >
            {String(Math.floor(h / 60)).padStart(2, "0")}:00
          </div>
        ))}
      </div>
      {DIAS.map((nombre, i) => {
        const dia = i + 1;
        return (
          <div key={dia} className="grilla-dia">
            <div className="grilla-dia-titulo">{nombre}</div>
            <div className="grilla-dia-cuerpo" style={{ height: altura }}>
              {horas.map((h) => (
                <div
                  key={h}
                  className="grilla-linea"
                  style={{ top: (h - min) * PX_POR_MIN }}
                />
              ))}
              {clases
                .filter((x) => x.clase.dia === dia)
                .map((x, idx) => {
                  const top = (aMinutos(x.clase.inicio) - min) * PX_POR_MIN;
                  const alto =
                    (aMinutos(x.clase.fin) - aMinutos(x.clase.inicio)) *
                    PX_POR_MIN;
                  const choca = enConflicto(x.catedra.id, dia);
                  const async = x.clase.modalidad === "asincronico";
                  return (
                    <div
                      key={idx}
                      className={`clase${choca ? " clase-choca" : ""}${
                        async ? " clase-async" : ""
                      }`}
                      style={{
                        top,
                        height: Math.max(alto, 18),
                        background: colorMateria(x.catedra.materiaId),
                      }}
                      title={`${nombreDe(x.catedra.materiaId)}\n${
                        x.catedra.docente ?? ""
                      }\n${x.clase.inicio}–${x.clase.fin}${
                        x.clase.virtualidad ? ` (${x.clase.virtualidad})` : ""
                      }`}
                      onClick={() => onQuitar(x.catedra.id)}
                    >
                      <strong>{nombreDe(x.catedra.materiaId)}</strong>
                      <span>{x.catedra.docente}</span>
                      <span className="clase-hora">
                        {x.clase.inicio}–{x.clase.fin}
                      </span>
                      {x.clase.virtualidad && (
                        <span className="clase-virt">({x.clase.virtualidad})</span>
                      )}
                    </div>
                  );
                })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
