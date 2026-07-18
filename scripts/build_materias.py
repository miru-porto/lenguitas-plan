#!/usr/bin/env python3
"""
Catálogo canónico de materias del Profesorado de Inglés (rama Inglés) con sus
correlativas, transcripto del PDF "materias y sistema de correlativas".

Herramienta de AUTORÍA (offline). Emite data/materias.json.

Modelo de correlativas (ver src/types.ts):
    Requisitos = AND de cláusulas ; cada cláusula = OR de opciones {materiaId, nivel}
    nivel: "final" (en condición de final) < "aprobada"

DSL de este archivo:
    - "id:f"  -> opción {id, "final"}
    - "id:a"  -> opción {id, "aprobada"}
    - un str            = cláusula de una sola opción
    - una lista de str  = cláusula OR (basta con una)
Ej: cursar=["lengua-inglesa-1:f", ["gramatica-1:f", "fonologia-1:f"]]
    => LI1 en final Y (Gramática1 O Fonología1) en final
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_op(tok: str):
    mid, _, niv = tok.partition(":")
    nivel = {"f": "final", "a": "aprobada"}[niv]
    return {"materiaId": mid.strip(), "nivel": nivel}


def parse_reqs(reqs):
    out = []
    for clausula in reqs or []:
        if isinstance(clausula, str):
            out.append([parse_op(clausula)])
        else:
            out.append([parse_op(t) for t in clausula])
    return out


MATERIAS = []


def M(id, nombre, anio, campo, regimen, cursar=None, aprobar=None, nota=None):
    m = {
        "id": id,
        "nombre": nombre,
        "anio": anio,
        "campo": campo,
        "regimen": regimen,
        "paraCursar": parse_reqs(cursar),
        "paraAprobar": parse_reqs(aprobar),
    }
    if nota:
        m["nota"] = nota
    MATERIAS.append(m)


# ---------------------------------------------------------------------------
# 1er año
# ---------------------------------------------------------------------------
M("lengua-inglesa-1", "Lengua Inglesa 1", 1, "CFE", "anual")
M("gramatica-1", "Gramática Inglesa 1", 1, "CFE", "anual")
M("fonologia-1", "Fonología y Práctica de Laboratorio 1", 1, "CFE", "anual")
M("taller-1", "Taller 1", 1, "CFPP", "cuatrimestral")
M("taller-2", "Taller 2", 1, "CFPP", "cuatrimestral",
  cursar=["taller-1:a", ["didactica-general:a", "pedagogia:a"]],
  aprobar=["taller-1:a", ["didactica-general:a", "pedagogia:a"]])
M("pedagogia", "Pedagogía", 1, "CFG", "cuatrimestral")
M("didactica-general", "Didáctica General", 1, "CFG", "cuatrimestral")
M("psicologia-educacional", "Psicología Educacional", 1, "CFG", "cuatrimestral")
M("taller-nuevas-tecnologias", "Taller de Nuevas Tecnologías", 1, "CFG", "cuatrimestral")
M("tleo", "Taller de Lectura, Escritura y Oralidad (TLEO)", 1, "CFG", "cuatrimestral")

# ---------------------------------------------------------------------------
# 2do año
# ---------------------------------------------------------------------------
M("lengua-inglesa-2", "Lengua Inglesa 2", 2, "CFE", "anual",
  cursar=["lengua-inglesa-1:f", ["gramatica-1:f", "fonologia-1:f"]],
  aprobar=["lengua-inglesa-1:a", ["gramatica-1:f", "fonologia-1:f"]])
M("gramatica-2", "Gramática Inglesa 2", 2, "CFE", "anual",
  cursar=["lengua-inglesa-1:f", "gramatica-1:f"],
  aprobar=["lengua-inglesa-1:f", "gramatica-1:a"])
M("fonologia-2", "Fonología y Práctica de Laboratorio 2", 2, "CFE", "anual",
  cursar=["lengua-inglesa-1:f", "fonologia-1:f"],
  aprobar=["lengua-inglesa-1:f", "fonologia-1:a"])
M("cultura-1", "Cultura de los Pueblos de Habla Inglesa 1", 2, "CFE", "anual",
  cursar=["lengua-inglesa-1:f"],
  aprobar=["lengua-inglesa-1:f"])
M("didactica-especifica-1", "Didáctica Específica 1", 2, "CFE", "cuatrimestral",
  cursar=["didactica-general:a", "taller-2:a"],
  aprobar=["didactica-general:a", "taller-2:a"])
M("didactica-especifica-2", "Didáctica Específica 2", 2, "CFE", "cuatrimestral",
  cursar=["didactica-especifica-1:f", "lengua-inglesa-1:f"],
  aprobar=["didactica-especifica-1:a", "lengua-inglesa-1:f"])
M("creatividad-1", "Creatividad 1", 2, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-1:f", "taller-2:a"],
  aprobar=["lengua-inglesa-1:f", "taller-2:a"])
M("taller-3", "Taller 3", 2, "CFPP", "cuatrimestral",
  cursar=["taller-2:a", "lengua-inglesa-1:f"],
  aprobar=["taller-2:a", "lengua-inglesa-1:f"])
M("taller-4", "Taller 4", 2, "CFPP", "cuatrimestral",
  cursar=["taller-3:a", "didactica-especifica-1:f", "psicologia-educacional:a", "lengua-inglesa-1:a"],
  aprobar=["taller-3:a", "didactica-especifica-1:f", "psicologia-educacional:a", "lengua-inglesa-1:a"])
M("sujetos-educacion-1", "Sujetos de la Educación 1", 2, "CFE", "cuatrimestral",
  cursar=["psicologia-educacional:f"],
  aprobar=["psicologia-educacional:a"])
M("sistemas-politica-educativa", "Sistema y Política Educativa", 2, "CFG", "cuatrimestral")
M("metodologia-investigacion", "Metodología de la Investigación", 2, "CFG", "cuatrimestral",
  cursar=["didactica-general:a", "pedagogia:a", "psicologia-educacional:a"],
  aprobar=["didactica-general:a", "pedagogia:a", "psicologia-educacional:a"])
M("esi", "Educación Sexual Integral (ESI)", 2, "CFG", "cuatrimestral",
  cursar=["taller-2:a", "psicologia-educacional:a"],
  aprobar=["taller-2:a", "psicologia-educacional:a"])

# ---------------------------------------------------------------------------
# 3er año
# ---------------------------------------------------------------------------
M("lengua-inglesa-3", "Lengua Inglesa 3", 3, "CFE", "anual",
  cursar=["lengua-inglesa-2:f", ["gramatica-2:f", "fonologia-2:f"]],
  aprobar=["lengua-inglesa-2:a", ["gramatica-2:f", "fonologia-2:f"]])
M("linguistica", "Lingüística", 3, "CFE", "anual",
  cursar=["fonologia-1:a", "lengua-inglesa-2:f", "gramatica-2:f", "didactica-especifica-1:f"],
  aprobar=["fonologia-1:a", "lengua-inglesa-2:f", "gramatica-2:a", "didactica-especifica-1:f"])
M("fonologia-3", "Fonología y Práctica de Laboratorio 3", 3, "CFE", "anual",
  cursar=["gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "fonologia-2:f"],
  aprobar=["gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "fonologia-2:a"])
M("literatura-1", "Literatura en Lengua Inglesa 1", 3, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "cultura-1:f"],
  aprobar=["lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "cultura-1:f"])
M("literatura-2", "Literatura en Lengua Inglesa 2", 3, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "cultura-1:f", "literatura-1:f"],
  aprobar=["lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "lengua-inglesa-2:f", "cultura-1:f", "literatura-1:a"])
M("sujetos-educacion-2", "Sujetos de la Educación 2", 3, "CFE", "cuatrimestral",
  cursar=["psicologia-educacional:f"],
  aprobar=["psicologia-educacional:a"])
M("creatividad-2", "Creatividad 2", 3, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-1:a", "gramatica-1:f", "fonologia-1:f", "didactica-especifica-1:a", "creatividad-1:a", "taller-2:a"],
  aprobar=["lengua-inglesa-1:a", "gramatica-1:f", "fonologia-1:f", "didactica-especifica-1:a", "creatividad-1:a", "taller-2:a"])
M("taller-5", "Taller 5 (de Inicial y Primaria)", 3, "CFPP", "cuatrimestral",
  cursar=["taller-4:a", "lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "didactica-especifica-1:a", "lengua-inglesa-2:f", "creatividad-1:a"],
  aprobar=["taller-4:a", "lengua-inglesa-1:a", "gramatica-1:a", "fonologia-1:a", "didactica-especifica-1:a", "lengua-inglesa-2:f", "creatividad-1:a"])
M("residencia-inicial-primario", "Residencia para el Nivel Inicial y Primario", 3, "CFPP", "cuatrimestral",
  cursar=["taller-5:a", "didactica-especifica-2:a", "lengua-inglesa-2:a", "gramatica-1:a", "fonologia-1:a", "creatividad-1:a", "pedagogia:a", "sujetos-educacion-1:a", "taller-nuevas-tecnologias:a", "fonologia-2:f"],
  aprobar=["taller-5:a", "didactica-especifica-2:a", "lengua-inglesa-2:a", "gramatica-1:a", "fonologia-1:a", "creatividad-1:a", "pedagogia:a", "sujetos-educacion-1:a", "taller-nuevas-tecnologias:a", "fonologia-2:f"],
  nota="Seminario de Investigación Acción 1 en cursada simultánea obligatoria.")
M("seminario-investigacion-accion-1", "Seminario de Investigación Acción 1", 3, "CFPP", "cuatrimestral",
  nota="Se cursa en simultáneo con la Residencia de Nivel Inicial y Primario; para aprobar hay que aprobar todas las instancias de esa Residencia.")
M("informatica-ensenanza", "Informática para la Enseñanza", 3, "CFG", "cuatrimestral",
  cursar=["taller-nuevas-tecnologias:a"],
  aprobar=["taller-nuevas-tecnologias:a"])
M("instituciones-educativas", "Instituciones Educativas", 3, "CFG", "cuatrimestral",
  cursar=["didactica-general:a", "pedagogia:a"],
  aprobar=["didactica-general:a", "pedagogia:a"])
M("saberes-ludicos", "Saberes Lúdicos, Corporales y Motores", 3, "CFG", "cuatrimestral",
  cursar=["taller-2:a"],
  aprobar=["taller-2:a"])
M("trabajo-de-campo", "Trabajo de Campo", 3, "CFG", "cuatrimestral",
  cursar=["metodologia-investigacion:a"],
  aprobar=["metodologia-investigacion:a"],
  nota="Debe cursarse posteriormente a UNO de: Didáctica General, Sistemas y Política Educativa, Psicología Educacional, Pedagogía o Instituciones Educativas.")

# ---------------------------------------------------------------------------
# 4to año
# ---------------------------------------------------------------------------
M("lengua-inglesa-4", "Lengua Inglesa 4", 4, "CFE", "anual",
  cursar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:a", "cultura-1:a", "lengua-inglesa-3:f"],
  aprobar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:a", "cultura-1:a", "lengua-inglesa-3:a"])
M("cultura-2", "Cultura de los Pueblos de Habla Inglesa 2", 4, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f", "cultura-1:f"],
  aprobar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f", "cultura-1:a"])
M("literatura-3", "Literatura en Lengua Inglesa 3", 4, "CFE", "anual",
  cursar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f", "literatura-2:f", "lengua-inglesa-3:f"],
  aprobar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f", "literatura-2:a", "lengua-inglesa-3:f"])
M("analisis-redaccion-textos", "Análisis y Redacción de Textos", 4, "CFE", "anual",
  cursar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f"],
  aprobar=["lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:f"])
M("teatro", "Teatro", 4, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-2:a", "gramatica-2:f", "fonologia-2:f"],
  aprobar=["lengua-inglesa-2:a", "gramatica-2:f", "fonologia-2:f"])
M("taller-6", "Taller 6 (de Nivel Medio)", 4, "CFPP", "cuatrimestral",
  cursar=["taller-5:a", "didactica-especifica-2:a", "lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:a", "informatica-ensenanza:a"],
  aprobar=["taller-5:a", "didactica-especifica-2:a", "lengua-inglesa-2:a", "gramatica-2:a", "fonologia-2:a", "informatica-ensenanza:a"])
M("residencia-nivel-medio", "Residencia para el Nivel Medio", 4, "CFPP", "cuatrimestral",
  cursar=["taller-6:a", "didactica-especifica-2:a", "gramatica-2:a", "fonologia-2:a", "sujetos-educacion-2:a", "lengua-inglesa-3:f", "linguistica:f"],
  aprobar=["taller-6:a", "didactica-especifica-2:a", "gramatica-2:a", "fonologia-2:a", "sujetos-educacion-2:a", "lengua-inglesa-3:f", "linguistica:f"],
  nota="Seminario de Investigación Acción 2 en cursada simultánea obligatoria.")
M("seminario-investigacion-accion-2", "Seminario de Investigación Acción 2", 4, "CFPP", "cuatrimestral",
  nota="Se cursa en simultáneo con la Residencia de Nivel Medio; para aprobar hay que aprobar todas las instancias de esa Residencia.")
M("nuevos-escenarios", "Nuevos Escenarios, Cultura, Tecnología y Subjetividad", 4, "CFG", "cuatrimestral",
  cursar=["instituciones-educativas:a"],
  aprobar=["instituciones-educativas:a"])
M("trabajo-profesionalizacion-docente", "Trabajo / Profesionalización Docente", 4, "CFG", "cuatrimestral",
  cursar=["instituciones-educativas:a"],
  aprobar=["instituciones-educativas:a"])
M("filosofia", "Filosofía", 4, "CFG", "cuatrimestral")
M("tic-aplicadas", "TIC Aplicadas", 4, "CFG", "cuatrimestral",
  cursar=["informatica-ensenanza:a"],
  aprobar=["informatica-ensenanza:a"])

# ---------------------------------------------------------------------------
# 5to año (sólo plan superior de 5 años)
# ---------------------------------------------------------------------------
M("ab-initio-1", "Portugués Ab Initio 1", 5, "CFE", "cuatrimestral")
M("ab-initio-2", "Portugués Ab Initio 2", 5, "CFE", "cuatrimestral",
  cursar=["ab-initio-1:a"], aprobar=["ab-initio-1:a"])
M("cultura-3", "Cultura de los Pueblos de Habla Inglesa 3", 5, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-3:f", "gramatica-2:a", "fonologia-2:a", "cultura-2:f", "literatura-1:a"],
  aprobar=["lengua-inglesa-3:f", "gramatica-2:a", "fonologia-2:a", "cultura-2:a", "literatura-1:a"])
M("literatura-4", "Literatura en Lengua Inglesa 4", 5, "CFE", "cuatrimestral",
  cursar=["lengua-inglesa-3:a", "gramatica-2:a", "fonologia-2:a", "literatura-3:f", "cultura-1:a"],
  aprobar=["lengua-inglesa-3:a", "gramatica-2:a", "fonologia-2:a", "literatura-3:a", "cultura-1:a"])
M("residencia-nivel-superior", "Residencia para el Nivel Superior", 5, "CFPP", "cuatrimestral",
  cursar=["taller-6:a", "didactica-especifica-2:a", "gramatica-2:a", "fonologia-2:a", "sujetos-educacion-2:a", "lengua-inglesa-3:a", "linguistica:f"],
  aprobar=["taller-6:a", "didactica-especifica-2:a", "gramatica-2:a", "fonologia-2:a", "sujetos-educacion-2:a", "lengua-inglesa-3:a", "linguistica:f"])
M("taller-musica", "Taller de Música", 5, "CFG", "cuatrimestral",
  cursar=["taller-2:a"], aprobar=["taller-2:a"])


def asignar_id_externo():
    """Cruza cada materia con data/materias.externas.json (proyecto 'rate my prof')
    por (nombre, anio) y le agrega su id numérico como referencia cruzada."""
    ruta = ROOT / "data" / "materias.externas.json"
    if not ruta.exists():
        print("AVISO: no está data/materias.externas.json; se omite idExterno.")
        return
    externas = json.loads(ruta.read_text(encoding="utf-8"))
    por_clave = {(e["nombre"], e["anio"]): e["id"] for e in externas}
    sin_match = []
    for m in MATERIAS:
        ext = por_clave.get((m["nombre"], m["anio"]))
        if ext is None:
            sin_match.append(m["nombre"])
        else:
            m["idExterno"] = ext
    if sin_match:
        raise SystemExit(
            "Estas materias no casan con materias.externas.json (revisar nombre/anio): "
            + ", ".join(sin_match)
        )


def main():
    ids = [m["id"] for m in MATERIAS]
    dups = {i for i in ids if ids.count(i) > 1}
    if dups:
        raise SystemExit(f"IDs duplicados: {dups}")

    asignar_id_externo()

    # Validación de integridad: toda correlativa referida debe existir.
    idset = set(ids)
    faltantes = set()
    for m in MATERIAS:
        for reqs in (m["paraCursar"], m["paraAprobar"]):
            for clausula in reqs:
                for op in clausula:
                    if op["materiaId"] not in idset:
                        faltantes.add(op["materiaId"])
    if faltantes:
        raise SystemExit(f"Correlativas a materias inexistentes: {sorted(faltantes)}")

    destino = ROOT / "data" / "materias.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(
        json.dumps({"materias": MATERIAS}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK -> {destino.relative_to(ROOT)}  ({len(MATERIAS)} materias)")


if __name__ == "__main__":
    main()
