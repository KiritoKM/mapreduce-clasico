#!/usr/bin/env python3
"""
Mapper (versión clásica, por stdin/stdout).

Entrada : líneas CSV  ->  categoria,subcategoria,valor
Salida  : líneas TSV  ->  categoria<TAB>subcategoria<TAB>valor

- La clave de agrupación son las primeras GROUP_BY_COLS columnas
  (por defecto 2: categoría y subcategoría). Con GROUP_BY_COLS=1 se agrupa
  solo por categoría, como en el laboratorio original.
- El valor es siempre la ÚLTIMA columna.
- Se ignoran líneas vacías, encabezados y filas mal formadas, para poder
  concatenar muchos CSV (cada uno con su encabezado) en un solo flujo.
"""
import os
import sys

GROUP_BY_COLS = int(os.environ.get("GROUP_BY_COLS", "2"))


def main():
    bad = 0
    for line in sys.stdin:
        line = line.strip().lstrip("﻿")
        if not line:
            continue
        fields = [f.strip() for f in line.split(",")]
        if len(fields) < GROUP_BY_COLS + 1:
            bad += 1
            continue
        try:
            value = float(fields[-1])
        except ValueError:          # encabezado o valor no numérico
            bad += 1
            continue
        key = "\t".join(fields[:GROUP_BY_COLS])
        sys.stdout.write(f"{key}\t{value}\n")
    if bad:
        print(f"[mapper] líneas ignoradas: {bad}", file=sys.stderr)


if __name__ == "__main__":
    main()
