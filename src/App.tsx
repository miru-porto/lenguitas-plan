import { useMemo, useState } from "react";
import "./App.css";
import { catedras, nombreDe } from "./data";
import { detectarSuperposiciones } from "./logic";
import { useEstado, type FiltroTurno } from "./useEstado";
import { Grilla } from "./components/Grilla";
import { SelectorMaterias } from "./components/SelectorMaterias";
import { Historial } from "./components/Historial";

const TURNOS: { valor: FiltroTurno; label: string }[] = [
  { valor: "ambos", label: "Ambos" },
  { valor: "mañana", label: "Mañana" },
  { valor: "vespertino", label: "Vespertino" },
];

export default function App() {
  const { estado, toggleCatedra, setEstadoMateria, setTurno, limpiar, permalink } =
    useEstado();
  const [tab, setTab] = useState<"materias" | "historial">("materias");
  const [copiado, setCopiado] = useState(false);

  const seleccionadas = useMemo(
    () => catedras.filter((c) => estado.seleccionadas.includes(c.id)),
    [estado.seleccionadas],
  );
  const conflictos = useMemo(
    () => detectarSuperposiciones(seleccionadas),
    [seleccionadas],
  );

  const copiarPermalink = async () => {
    await navigator.clipboard.writeText(permalink());
    setCopiado(true);
    setTimeout(() => setCopiado(false), 1500);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Lenguitas-Plan</h1>
          <p className="app-sub">
            Armá tu cuatrimestre en el Profesorado de Inglés sin superponer materias.
          </p>
        </div>
        <div className="app-acciones">
          <button onClick={copiarPermalink}>
            {copiado ? "¡Copiado!" : "Copiar link"}
          </button>
          <button onClick={limpiar} className="btn-secundario">
            Limpiar
          </button>
        </div>
      </header>

      {conflictos.length > 0 && (
        <div className="banner-conflicto">
          ⚠ Tenés {conflictos.length} superposición
          {conflictos.length > 1 ? "es" : ""}:{" "}
          {conflictos
            .slice(0, 3)
            .map(
              (c) => `${nombreDe(c.a.materiaId)} × ${nombreDe(c.b.materiaId)}`,
            )
            .join(", ")}
          {conflictos.length > 3 ? "…" : ""}
        </div>
      )}

      <div className="app-cuerpo">
        <aside className="panel">
          <div className="panel-tabs">
            <button
              className={tab === "materias" ? "tab-activo" : ""}
              onClick={() => setTab("materias")}
            >
              Materias
            </button>
            <button
              className={tab === "historial" ? "tab-activo" : ""}
              onClick={() => setTab("historial")}
            >
              Mi historial
            </button>
          </div>

          {tab === "materias" && (
            <div className="panel-filtros">
              {TURNOS.map((t) => (
                <button
                  key={t.valor}
                  className={estado.turno === t.valor ? "chip chip-activo" : "chip"}
                  onClick={() => setTurno(t.valor)}
                >
                  {t.label}
                </button>
              ))}
            </div>
          )}

          {tab === "materias" ? (
            <SelectorMaterias
              seleccionadas={estado.seleccionadas}
              historial={estado.historial}
              turno={estado.turno}
              onToggle={toggleCatedra}
            />
          ) : (
            <Historial historial={estado.historial} onSet={setEstadoMateria} />
          )}
        </aside>

        <main className="app-grilla">
          <Grilla
            seleccionadas={seleccionadas}
            conflictos={conflictos}
            onQuitar={toggleCatedra}
          />
        </main>
      </div>
    </div>
  );
}
