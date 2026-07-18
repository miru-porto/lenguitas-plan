#!/usr/bin/env python3
"""
Extrae los horarios desde los .md de los grids (conversión de los Docs de la
institución) a data/horarios.raw.json.

Fuente preferida sobre el PDF: los .md traen el docente en **negrita** y la
modalidad entre paréntesis, así que se parsean mucho más limpio.

Uso:
    python scripts/extract_horarios_md.py

Salida con la misma forma que espera scripts/reconcile.py.
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FUENTES = {
    "INGLÉS TM - 2do cuatrimestre 2026.md": "mañana",
    "INGLÉS TV - 2do cuatrimestre 2026.docx.md": "vespertino",
}

DIAS = {
    "lunes": 1,
    "martes": 2,
    "miércoles": 3,
    "miercoles": 3,
    "jueves": 4,
    "viernes": 5,
}

ESPACIOS_TDC = [
    "Sistema y Política Educativa",
    "Instituciones Educativas",
    "Psicología Educacional",
    "Didáctica General",
    "Pedagogía",
]


def slug(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def norm(s):
    return " ".join((s or "").replace("\\", "").split())


def celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def es_separador(linea):
    return bool(re.fullmatch(r"[\s|:\-]+", linea.strip()))


def mapa_columnas(header):
    col_day, actual = {}, None
    for i, h in enumerate(header):
        clave = h.strip().lower()
        if clave in DIAS:
            actual = DIAS[clave]
        elif clave and clave != "hora":
            actual = None  # una columna con texto que no es día corta la herencia
        if actual is not None and i > 0:
            col_day[i] = actual
    return col_day


def hora_de_fila(c0):
    horas = re.findall(r"(\d{1,2}:\d{2})", c0 or "")
    return (horas[0], horas[1]) if len(horas) >= 2 else None


def clasificar(nota):
    n = (nota or "").lower()
    a = len(re.findall(r"asincr[oó]nic", n))
    s = len(re.findall(r"(?<!a)sincr[oó]nic", n))
    if a and s:
        return "bimodal"
    if a:
        return "asincronico"
    if s:
        return "sincronico"
    return "presencial"


def extraer_virtualidad(bold):
    """Devuelve sólo la frase de modalidad (ej. '25% sincrónico 25% asincrónico',
    'sincrónico'), ignorando notas de cuatrimestre. En minúscula, o None."""
    # Preferimos el contenido de un paréntesis que hable de modalidad.
    for g in re.findall(r"\(([^)]*)\)", bold):
        if re.search(r"sincr[oó]nic|%", g, re.IGNORECASE):
            return norm(g).lower()
    # Sin paréntesis: frase de modalidad suelta (ej. 'Chervonko 25% sincrónica ...').
    m = re.search(r"(\d+\s*%[^()]*?sincr[oó]nic\w*[^()]*|a?sincr[oó]nic\w*)", bold, re.IGNORECASE)
    return norm(m.group(1)).lower() if m else None


def parsear_celda(txt):
    """'MATERIA **Docente (modalidad)**' -> (materia, docente, modalidad, virtualidad)."""
    txt = txt.replace("\\", "").strip()
    if not txt:
        return None
    m = re.search(r"\*\*(.+?)\*\*", txt)
    if m:
        materia = norm(txt[: m.start()])
        bold = norm(m.group(1))
    else:
        materia, bold = norm(txt), ""
    if not materia:
        return None
    # El docente termina donde empieza la nota/modalidad: un "(", un "N%" o "sincrónic".
    idx = len(bold)
    for pat in (r"\(", r"\d+\s*%", r"a?sincr[oó]nic"):
        m2 = re.search(pat, bold, re.IGNORECASE)
        if m2:
            idx = min(idx, m2.start())
    docente = norm(bold[:idx]).strip(" (") or None
    virt = extraer_virtualidad(bold)
    return materia, docente, clasificar(virt), virt


def parsear_tdc(txt):
    """'TRABAJO DE CAMPO en Pedagogía **DEL REGNO (ASINCRÓNICO)**' -> (espacio, docente)."""
    txt = txt.replace("\\", "")
    if "TRABAJO DE CAMPO" not in txt:
        return None
    m = re.search(r"\*\*(.+?)\*\*", txt)
    docente = norm(m.group(1).split("(")[0]) if m else None
    antes = norm(re.sub(r"\*\*.+?\*\*", "", txt))
    resto = re.sub(r"^TRABAJO DE CAMPO\s+(?:en|de)\s+", "", antes, flags=re.IGNORECASE)
    for esp in ESPACIOS_TDC:
        if resto.lower().startswith(esp.lower()):
            return esp, docente
    return norm(resto), docente


def secciones(texto):
    """Devuelve [(titulo, [filas_tabla])] por cada grilla del archivo."""
    lineas = texto.splitlines()
    out, titulo, tabla, en_tabla = [], None, [], False
    for ln in lineas:
        s = ln.strip()
        if s.startswith("**Turno") or "Horarios TRABAJO DE CAMPO" in s:
            if titulo and tabla:
                out.append((titulo, tabla))
            titulo, tabla, en_tabla = s, [], False
        elif s.startswith("|"):
            tabla.append(s)
            en_tabla = True
        elif en_tabla and not s:
            if titulo and tabla:
                out.append((titulo, tabla))
            titulo, tabla, en_tabla = None, [], False
    if titulo and tabla:
        out.append((titulo, tabla))
    return out


def datos_titulo(titulo):
    m_anio = re.search(r"(\d)\s*°?\s*A[ñn]o", titulo)
    m_com = re.search(r"Comisi[oó]n\s+([AB])", titulo)
    return (
        int(m_anio.group(1)) if m_anio else None,
        m_com.group(1) if m_com else None,
    )


def bloques_por_columna(filas, parser):
    """Recorre la tabla y colapsa franjas contiguas iguales en bloques."""
    header = celdas(filas[0])
    col_day = mapa_columnas(header)
    datos = [f for f in filas[1:] if not es_separador(f)]
    bloques = []
    for c, dia in col_day.items():
        actual = None
        for fila in datos:
            cs = celdas(fila)
            horas = hora_de_fila(cs[0]) if cs else None
            celda = cs[c] if c < len(cs) else ""
            parsed = parser(celda) if celda else None
            if not horas or not parsed:
                if actual:
                    bloques.append(actual)
                    actual = None
                continue
            etq = (parsed, dia)
            if actual and actual["etq"] == etq:
                actual["fin"] = horas[1]
            else:
                if actual:
                    bloques.append(actual)
                actual = {"etq": etq, "parsed": parsed, "dia": dia,
                          "inicio": horas[0], "fin": horas[1]}
        if actual:
            bloques.append(actual)
    return bloques


def procesar(titulo, filas, turno):
    if "TRABAJO DE CAMPO" in titulo:
        coms = {}
        for b in bloques_por_columna(filas, parsear_tdc):
            espacio, docente = b["parsed"]
            key = (espacio, docente)
            com = coms.setdefault(key, {
                "id": slug(f"tdc {espacio} {docente} {turno}"),
                "materiaId": "trabajo-de-campo", "materiaNombre": "TRABAJO DE CAMPO",
                "turno": turno, "anio": None, "comision": espacio, "clases": [],
            })
            com["clases"].append({"dia": b["dia"], "inicio": b["inicio"], "fin": b["fin"],
                                  "docente": docente, "modalidad": "asincronico",
                                  "virtualidad": "asincrónico"})
        return list(coms.values())

    anio, comision = datos_titulo(titulo)
    coms = {}
    for b in bloques_por_columna(filas, parsear_celda):
        materia, docente, modalidad, virt = b["parsed"]
        key = (materia, docente)
        com = coms.setdefault(key, {
            "id": slug(f"{materia} {docente} {anio} {comision} {turno}"),
            "materiaId": None, "materiaNombre": materia,
            "turno": turno, "anio": anio, "comision": comision, "clases": [],
        })
        com["clases"].append({"dia": b["dia"], "inicio": b["inicio"], "fin": b["fin"],
                              "docente": docente, "modalidad": modalidad, "virtualidad": virt})
    return list(coms.values())


def main():
    todas, warns = [], []
    for nombre, turno in FUENTES.items():
        ruta = ROOT / nombre
        if not ruta.exists():
            warns.append(f"NO ENCONTRADO: {nombre}")
            continue
        texto = ruta.read_text(encoding="utf-8")
        for titulo, filas in secciones(texto):
            if len(filas) >= 2:
                todas.extend(procesar(titulo, filas, turno))

    for c in todas:
        c["clases"].sort(key=lambda x: (x["dia"], x["inicio"]))

    materias = {}
    for c in todas:
        materias.setdefault(c["materiaNombre"], 0)
        materias[c["materiaNombre"]] += 1

    salida = {
        "_nota": "Borrador generado por scripts/extract_horarios_md.py desde los .md.",
        "generadoDe": list(FUENTES.keys()),
        "materiasDetectadas": sorted(materias),
        "comisiones": todas,
    }
    (ROOT / "data" / "horarios.raw.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OK -> data/horarios.raw.json ({len(todas)} comisiones, {len(materias)} nombres)")
    for w in warns:
        print("  -", w)


if __name__ == "__main__":
    main()
