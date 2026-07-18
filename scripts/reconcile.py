#!/usr/bin/env python3
"""
Reconcilia el borrador de horarios con el catálogo canónico de materias y lo separa
en CÁTEDRAS (una por docente).

Lee:
    data/horarios.raw.json   (salida de extract_horarios.py)
    data/materias.json       (salida de build_materias.py)
    data/alias_horarios.json (mapa nombre-crudo -> id canónico)

Escribe:
    data/horarios.json       (limpio, es el que consume la app)

Tareas:
    - Reemplaza el nombre sucio de cada comisión por el id canónico (vía alias).
    - Separa por docente en cátedras: la unidad seleccionable es materia + profe.
      Dos cátedras de la misma materia son alternativas (no chocan entre sí).
    - Normaliza el nombre del docente (saca "1 " que se cuela, unifica por acento).
    - Toma el año del catálogo cuando el grid no lo trae (Trabajo de Campo).
    - Deduplica clases, valida el mapeo y reporta lo que quede sin mapear.
"""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cargar(nombre):
    return json.loads((ROOT / "data" / nombre).read_text(encoding="utf-8"))


def slug(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def limpiar_docente(s):
    """Saca ruido de extracción del nombre del docente:
    '1 Morelli' -> 'Morelli' ; 'Belser 1er Cuat 2027: Pedagogía' -> 'Belser'."""
    if not s:
        return None
    s = re.sub(r"^\s*\d+\s*°?\s*", "", s)  # marca de fila que se cuela al inicio
    s = re.split(r"\s+\d+\s*(?:er|do|ro|°)?\.?\s*cuat", s, flags=re.IGNORECASE)[0]  # nota de cuatrimestre
    s = " ".join(s.split())
    return s or None


def clave_docente(s):
    """Clave sin acentos ni mayúsculas para agrupar variantes ('Pérez'/'Perez')."""
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def elegir_display(variantes):
    """Entre variantes de un mismo docente, elige la más 'linda' (con acentos, más larga)."""
    def puntaje(v):
        return (sum(ord(c) > 127 for c in v), len(v))
    return max(variantes, key=puntaje) if variantes else None


def main():
    raw = cargar("horarios.raw.json")
    materias = {m["id"]: m for m in cargar("materias.json")["materias"]}
    alias = cargar("alias_horarios.json")["alias"]

    sin_mapear = {}
    catedras = {}

    for com in raw["comisiones"]:
        nombre_crudo = com["materiaNombre"]
        materia_id = alias.get(nombre_crudo)
        if materia_id is None:
            sin_mapear[nombre_crudo] = sin_mapear.get(nombre_crudo, 0) + 1
            continue
        if materia_id not in materias:
            raise SystemExit(
                f"Alias apunta a materia inexistente: {nombre_crudo!r} -> {materia_id!r}"
            )
        materia = materias[materia_id]
        anio = com["anio"] if com["anio"] is not None else materia["anio"]
        comision = com["comision"]

        # Cada clase se rutea a la cátedra de su docente.
        for cl in com["clases"]:
            doc = limpiar_docente(cl.get("docente"))
            clave = (com["turno"], anio, comision, materia_id, clave_docente(doc))
            cat = catedras.get(clave)
            if cat is None:
                cat = catedras[clave] = {
                    "materiaId": materia_id,
                    "turno": com["turno"],
                    "anio": anio,
                    "comision": comision,
                    "_docentes": Counter(),
                    "clases": [],
                }
            if doc:
                cat["_docentes"][doc] += 1
            clase = {
                "dia": cl["dia"],
                "inicio": cl["inicio"],
                "fin": cl["fin"],
                "modalidad": cl["modalidad"],
            }
            if cl.get("nota"):
                clase["nota"] = cl["nota"]
            cat["clases"].append(clase)

    # Finalizo cada cátedra: docente display, dedup y orden de clases, id estable.
    salida = []
    for cat in catedras.values():
        docente = elegir_display(list(cat.pop("_docentes")))
        vistos, unicas = set(), []
        for cl in sorted(cat["clases"], key=lambda x: (x["dia"], x["inicio"], x["fin"])):
            k = (cl["dia"], cl["inicio"], cl["fin"], cl["modalidad"])
            if k in vistos:
                continue
            vistos.add(k)
            unicas.append(cl)
        cat["clases"] = unicas
        cat["docente"] = docente
        cat["id"] = "-".join(
            x for x in [
                cat["materiaId"], str(cat["anio"]), slug(cat["comision"]),
                slug(docente), cat["turno"],
            ] if x
        )
        salida.append(cat)

    salida.sort(key=lambda c: (c["anio"], c["materiaId"], c["turno"], str(c["comision"]), c["docente"] or ""))

    # Reordeno claves para legibilidad.
    salida = [
        {
            "id": c["id"],
            "materiaId": c["materiaId"],
            "turno": c["turno"],
            "anio": c["anio"],
            "comision": c["comision"],
            "docente": c["docente"],
            "clases": c["clases"],
        }
        for c in salida
    ]

    ofrecidas = {c["materiaId"] for c in salida}
    no_ofrecidas = [m for m in materias if m not in ofrecidas]

    (ROOT / "data" / "horarios.json").write_text(
        json.dumps(
            {
                "_nota": "Generado por scripts/reconcile.py. Cátedras = materia + docente.",
                "catedras": salida,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("OK -> data/horarios.json")
    print(f"Cátedras: {len(salida)} | Materias ofrecidas: {len(ofrecidas)}/{len(materias)}")
    if sin_mapear:
        print("\nSIN MAPEAR (agregar al alias):")
        for n, c in sorted(sin_mapear.items()):
            print(f"  - {n!r} x{c}")
    if no_ofrecidas:
        print(f"\nEn el catálogo pero no ofrecidas este cuatrimestre ({len(no_ofrecidas)}):")
        print("  " + ", ".join(sorted(no_ofrecidas)))


if __name__ == "__main__":
    main()
