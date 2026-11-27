"""Comprueba la resolución de las fotos del banco y guarda su ancho y alto en indice.json.

    python comprobar_fotos.py              # comprueba; sale con código 1 si algo falla (lo usa la CI de GitHub)
    python comprobar_fotos.py --escribir   # además añade o corrige «ancho» y «alto» de cada foto en indice.json

Mínimos de ancho (px), por carpeta:
  portada/ y temas/  2400   (las fotos de portada se publican a 2550 px)
  beneficios/         800
banda/ y pie/ no tienen mínimo, pero también se guardan sus medidas. logos/ no se revisa.

El dashboard reescribe indice.json solo con «descripcion» y «etiquetas»: publicar.bat ejecuta este script con
--escribir antes de cada publicación, así las medidas vuelven solas y no se publica una foto por debajo del mínimo.
Requiere Pillow (pip install pillow).
"""
import json
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent
INDICE = RAIZ / "indice.json"
CARPETAS = ("portada", "temas", "banda", "beneficios", "pie")  # logos/ no: sus PNG son el respaldo de los SVG
EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp")
MINIMO_ANCHO = {"portada": 2400, "temas": 2400, "beneficios": 800}


def fotos():
    """{«carpeta/archivo»: (ancho, alto)} de las imágenes de la raíz de cada carpeta (las subcarpetas no cuentan)."""
    salida = {}
    for carpeta in CARPETAS:
        base = RAIZ / carpeta
        if not base.is_dir():
            continue
        for f in sorted(base.iterdir()):
            if f.is_file() and f.suffix.lower() in EXTENSIONES:
                with Image.open(f) as im:
                    salida[f"{carpeta}/{f.name}"] = im.size
    return salida


def escribir_indice(doc):
    """Mismo formato que escribe el dashboard (una entrada por foto, etiquetas en una línea), con ancho y alto."""
    d = lambda v: json.dumps(v, ensure_ascii=False)
    filas = []
    for clave, e in doc["fotos"].items():
        campos = [f'      "descripcion": {d(e.get("descripcion", ""))}',
                  f'      "etiquetas": [{", ".join(d(t) for t in e.get("etiquetas", []))}]']
        if "ancho" in e:
            campos += [f'      "ancho": {e["ancho"]}', f'      "alto": {e["alto"]}']
        filas.append(f"    {d(clave)}: {{\n" + ",\n".join(campos) + "\n    }")
    texto = (f'{{\n  "version": {d(doc.get("version", 1))},\n  "nota": {d(doc.get("nota", ""))},\n'
             f'  "fotos": {{' + ("\n" + ",\n".join(filas) + "\n  " if filas else "") + "}\n}\n")
    INDICE.write_text(texto, encoding="utf-8", newline="\n")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    escribir = "--escribir" in argv
    doc = json.loads(INDICE.read_text(encoding="utf-8"))
    entradas = doc.setdefault("fotos", {})
    medidas = fotos()
    errores, cambios = [], 0
    for clave, (ancho, alto) in medidas.items():
        carpeta = clave.split("/")[0]
        minimo = MINIMO_ANCHO.get(carpeta)
        if minimo and ancho < minimo:
            errores.append(f"{clave}: mide {ancho} × {alto} px; en {carpeta}/ el mínimo es {minimo} px de ancho.")
        e = entradas.get(clave)
        if e is None:
            if escribir:
                entradas[clave] = {"descripcion": "", "etiquetas": [], "ancho": ancho, "alto": alto}
                cambios += 1
            else:
                errores.append(f"{clave}: no está en indice.json (ejecuta publicar.bat o comprobar_fotos.py --escribir).")
        elif (e.get("ancho"), e.get("alto")) != (ancho, alto):
            if escribir:
                e["ancho"], e["alto"] = ancho, alto
                cambios += 1
            else:
                errores.append(f"{clave}: indice.json dice {e.get('ancho')} × {e.get('alto')} px y la foto mide {ancho} × {alto} px.")
    for clave in entradas:
        if clave.split("/")[0] in CARPETAS and clave not in medidas:
            print(f"Nota: {clave} está en indice.json pero la foto no existe.")
    if escribir and cambios:
        escribir_indice(doc)
        print(f"indice.json: medidas añadidas o corregidas en {cambios} fotos.")
    for e in errores:
        print("ERROR:", e)
    print(f"{len(medidas)} fotos revisadas; {len(errores)} problemas.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
