#!/usr/bin/env python3
"""
Reducer (versión clásica, por stdin/stdout).

Recibe la salida del mapper YA ORDENADA por clave (sort) y, por cada clave,
calcula: cantidad, promedio y desviación estándar.

Usa el algoritmo de Welford: recorre los valores una sola vez y usa memoria
constante, así que sirve para volúmenes grandes (no guarda la lista de valores).

STD_DDOF=0 -> desviación estándar poblacional (por defecto)
STD_DDOF=1 -> desviación estándar muestral
"""
import math
import os
import sys

DDOF = int(os.environ.get("STD_DDOF", "0"))


def emit(key, n, mean, m2):
    var = m2 / (n - DDOF) if n - DDOF > 0 else 0.0
    print(f"{key}\t{n}\t{mean:.2f}\t{math.sqrt(var):.2f}")


def main():
    current_key = None
    n, mean, m2 = 0, 0.0, 0.0

    cols = int(os.environ.get("GROUP_BY_COLS", "2"))
    keys_header = "\t".join(["categoria", "subcategoria"][:cols]) if cols <= 2 else "clave"
    print(f"{keys_header}\tn\tpromedio\tdesv_est")
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        key, value = line.rsplit("\t", 1)   # la clave puede tener varias columnas
        value = float(value)

        if key != current_key:
            if current_key is not None:
                emit(current_key, n, mean, m2)
            current_key, n, mean, m2 = key, 0, 0.0, 0.0

        # Welford: actualiza promedio y suma de cuadrados de desviaciones
        n += 1
        delta = value - mean
        mean += delta / n
        m2 += delta * (value - mean)

    if current_key is not None:     # emitir la última clave
        emit(current_key, n, mean, m2)


if __name__ == "__main__":
    main()
