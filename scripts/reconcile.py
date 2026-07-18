#!/usr/bin/env python3
"""
Reconcilia el borrador de horarios con el catálogo canónico de materias.

Lee:
    data/horarios.raw.json   (salida de extract_horarios.py)
    data/materias.json       (salida de build_materias.py)
    data/alias_horarios.json (mapa nombre-crudo -> id canónico)

Escribe:
    data/horarios.json       (limpio, es el que consume la app)

Tareas:
    - Reemplaza el nombre sucio de cada comisión por el id/nombre canónico.
    - Caso especial "Trabajo de Campo": recupera comisión y docente del apellido
      que quedó pegado en el nombre, y toma el año del catálogo.
    - Funde comisiones que quedaron con la misma clave (turno, año, comisión, materia).
    - Valida que toda comisión mapee a una materia existente y reporta lo que no.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cargar(nombre):
    return json.loads((ROOT / "data" / nombre).read_text(encoding="utf-8"))


def main():
    raw = cargar("horarios.raw.json")
    materias = {m["id"]: m for m in cargar("materias.json")["materias"]}
    alias = cargar("alias_horarios.json")["alias"]

    sin_mapear = {}
    comisiones = {}

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
        clases = com["clases"]

        clave = (com["turno"], anio, comision, materia_id)
        destino = comisiones.get(clave)
        if destino is None:
            comisiones[clave] = {
                "id": "-".join(
                    str(x) for x in [materia_id, anio, comision, com["turno"]] if x
                ),
                "materiaId": materia_id,
                "materiaNombre": materia["nombre"],
                "turno": com["turno"],
                "anio": anio,
                "comision": comision,
                "clases": list(clases),
            }
        else:
            destino["clases"].extend(clases)

    # Ordeno clases y deduplico bloques idénticos.
    salida_coms = []
    for com in comisiones.values():
        vistos = set()
        unicas = []
        for cl in sorted(com["clases"], key=lambda x: (x["dia"], x["inicio"], x["fin"], x.get("docente") or "")):
            k = (cl["dia"], cl["inicio"], cl["fin"], cl.get("docente"), cl["modalidad"])
            if k in vistos:
                continue
            vistos.add(k)
            unicas.append(cl)
        com["clases"] = unicas
        salida_coms.append(com)

    salida_coms.sort(key=lambda c: (c["anio"] or 99, c["materiaNombre"], c["turno"], str(c["comision"])))

    # Materias del catálogo que este cuatrimestre NO se ofrecen (sólo informativo).
    ofrecidas = {c["materiaId"] for c in salida_coms}
    no_ofrecidas = [m["id"] for m in materias.values() if m["id"] not in ofrecidas]

    salida = {
        "_nota": "Generado por scripts/reconcile.py a partir de horarios.raw.json + materias.json + alias_horarios.json.",
        "comisiones": salida_coms,
    }
    (ROOT / "data" / "horarios.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"OK -> data/horarios.json")
    print(f"Comisiones: {len(salida_coms)} | Materias ofrecidas: {len(ofrecidas)}/{len(materias)}")
    if sin_mapear:
        print("\nSIN MAPEAR (agregar al alias):")
        for n, c in sorted(sin_mapear.items()):
            print(f"  - {n!r} x{c}")
    if no_ofrecidas:
        print(f"\nEn el catálogo pero no ofrecidas este cuatrimestre ({len(no_ofrecidas)}):")
        print("  " + ", ".join(sorted(no_ofrecidas)))


if __name__ == "__main__":
    main()
