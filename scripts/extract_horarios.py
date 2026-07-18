#!/usr/bin/env python3
"""
Extrae los horarios de los PDFs del Profesorado (TM / TV) a un JSON estructurado.

Herramienta de AUTORÍA (offline), no forma parte del bundle de la app.
El JSON que produce es un borrador para revisar a mano: nombres de materia,
docentes y modalidades salen best-effort y hay que validarlos contra el PDF.

Uso:
    python scripts/extract_horarios.py

Requiere: pip install pdfplumber
"""

import json
import re
import unicodedata
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent

# PDF -> turno
FUENTES = {
    "INGLÉS TM - 2do cuatrimestre 2026.pdf": "mañana",
    "INGLÉS TV - 2do cuatrimestre 2026.pdf": "vespertino",
}

DIAS = {
    "lunes": 1,
    "martes": 2,
    "miércoles": 3,
    "miercoles": 3,
    "jueves": 4,
    "viernes": 5,
}


def slug(texto: str) -> str:
    """Normaliza un nombre de materia a un id estable (sin acentos, kebab-case)."""
    t = unicodedata.normalize("NFKD", texto)
    t = t.encode("ascii", "ignore").decode("ascii").lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t


def es_mayuscula(linea: str) -> bool:
    """True si la línea es parte del nombre de materia (va en MAYÚSCULAS)."""
    return any(c.isalpha() for c in linea) and linea == linea.upper()


def clasificar_modalidad(nota: str) -> str:
    n = nota.lower()
    n_async = len(re.findall(r"asincr[oó]n", n))
    n_sync = len(re.findall(r"(?<!a)sincr[oó]n", n))
    if n_async and n_sync:
        return "bimodal"
    if n_async:
        return "asincronico"
    if n_sync:
        return "sincronico"
    return "presencial"


def parsear_celda(texto: str):
    """Separa el contenido de una celda en (materia, docente, nota)."""
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]
    materia, docente, nota = [], [], []
    for l in lineas:
        low = l.lower()
        if l.startswith("(") or l.endswith(")") or "sincrón" in low or "asincrón" in low:
            nota.append(l)
        elif es_mayuscula(l):
            materia.append(l)
        else:
            docente.append(l)
    return (
        " ".join(materia).strip(),
        " ".join(docente).strip() or None,
        " ".join(nota).strip() or None,
    )


def parsear_titulo(texto_pagina: str):
    """Devuelve (anio, comision) del encabezado de la página, o (None, None)."""
    linea = texto_pagina.strip().splitlines()[0] if texto_pagina.strip() else ""
    m_anio = re.search(r"(\d)\s*°?\s*A[ñn]o", linea)
    m_com = re.search(r"Comisi[oó]n\s+([AB])", linea)
    anio = int(m_anio.group(1)) if m_anio else None
    comision = m_com.group(1) if m_com else None
    return anio, comision, linea


def mapa_columnas(header):
    """Índice de columna -> día (1..5), heredando el día de la última cabecera."""
    col_day = {}
    actual = None
    for c in range(1, len(header)):
        h = (header[c] or "").strip().lower()
        if h in DIAS:
            actual = DIAS[h]
        if actual is not None:
            col_day[c] = actual
    return col_day


def hora_de_fila(col0: str):
    horas = re.findall(r"(\d{1,2}:\d{2})", col0 or "")
    if len(horas) >= 2:
        return horas[0], horas[1]
    return None


def procesar_pagina(page, turno, warns):
    texto = page.extract_text() or ""
    if "GRILLA DE PORCENTAJES" in texto:
        return []
    anio, comision, titulo = parsear_titulo(texto)

    tablas = page.extract_tables()
    if not tablas:
        warns.append(f"[{turno}] sin tabla: {titulo[:60]!r}")
        return []
    tabla = tablas[0]
    header = tabla[0]
    col_day = mapa_columnas(header)
    if not col_day:
        warns.append(f"[{turno}] sin columnas de día: {titulo[:60]!r}")
        return []
    if anio is None:
        warns.append(f"[{turno}] no pude leer el año: {titulo[:60]!r}")

    # Recolecto por columna una secuencia de (inicio, fin, materia, docente, nota)
    # y colapso franjas contiguas con la misma materia.
    bloques = []
    for c, dia in col_day.items():
        actual = None
        for r in range(1, len(tabla)):
            fila = tabla[r]
            horas = hora_de_fila(fila[0])
            celda = fila[c] if c < len(fila) else None
            materia = docente = nota = None
            if celda:
                materia, docente, nota = parsear_celda(celda)
            if not horas or not materia:
                if actual:
                    bloques.append(actual)
                    actual = None
                continue
            if actual and actual["_materia"] == materia and actual["dia"] == dia:
                actual["fin"] = horas[1]  # extiendo el bloque
                actual["nota"] = actual["nota"] or nota
                actual["docente"] = actual["docente"] or docente
            else:
                if actual:
                    bloques.append(actual)
                actual = {
                    "_materia": materia,
                    "dia": dia,
                    "inicio": horas[0],
                    "fin": horas[1],
                    "docente": docente,
                    "nota": nota,
                }
        if actual:
            bloques.append(actual)

    # Agrupo bloques en comisiones por materia.
    comisiones = {}
    for b in bloques:
        mid = slug(b["_materia"])
        key = (turno, anio, comision, mid)
        com = comisiones.setdefault(
            key,
            {
                "id": "-".join(
                    filter(None, [mid, str(anio), comision, turno])
                ),
                "materiaId": mid,
                "materiaNombre": b["_materia"],
                "turno": turno,
                "anio": anio,
                "comision": comision,
                "clases": [],
            },
        )
        com["clases"].append(
            {
                "dia": b["dia"],
                "inicio": b["inicio"],
                "fin": b["fin"],
                "docente": b["docente"],
                "modalidad": clasificar_modalidad(b["nota"]) if b["nota"] else "presencial",
                "nota": b["nota"],
            }
        )

    for com in comisiones.values():
        com["clases"].sort(key=lambda x: (x["dia"], x["inicio"]))
    return list(comisiones.values())


def main():
    todas = []
    warns = []
    for nombre, turno in FUENTES.items():
        ruta = ROOT / nombre
        if not ruta.exists():
            warns.append(f"NO ENCONTRADO: {nombre}")
            continue
        with pdfplumber.open(ruta) as pdf:
            for page in pdf.pages:
                todas.extend(procesar_pagina(page, turno, warns))

    materias = {}
    for com in todas:
        materias.setdefault(com["materiaId"], com["materiaNombre"])

    salida = {
        "_nota": "Borrador generado por scripts/extract_horarios.py. Revisar a mano.",
        "generadoDe": list(FUENTES.keys()),
        "materiasDetectadas": [
            {"id": k, "nombre": v} for k, v in sorted(materias.items())
        ],
        "comisiones": todas,
    }

    destino = ROOT / "data" / "horarios.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"OK -> {destino.relative_to(ROOT)}")
    print(f"Comisiones: {len(todas)} | Materias distintas: {len(materias)}")
    if warns:
        print("\nAvisos:")
        for w in warns:
            print("  -", w)


if __name__ == "__main__":
    main()
