#!/usr/bin/env python3
"""
Genera muchos CSV grandes para probar el procesamiento de volúmenes altos.

  python generate_data.py --files 8 --rows 500000 --out input_big

Cada archivo tiene encabezado y filas  categoria,subcategoria,valor.
Las categorías tienen distribuciones distintas para que los promedios y
desviaciones sean distinguibles.
"""
import argparse
import os
import random

CATEGORIES = {        # categoria: (media, desviacion)
    "A": (50, 10), "B": (20, 5), "C": (100, 30), "D": (5, 1), "E": (70, 20),
}
SUBCATS = ["x", "y", "z", "w"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=int, default=8)
    ap.add_argument("--rows", type=int, default=500_000, help="filas por archivo")
    ap.add_argument("--out", default="input_big")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    rnd = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    cats = list(CATEGORIES)
    for i in range(a.files):
        path = os.path.join(a.out, f"part_{i:03d}.csv")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("categoria,subcategoria,valor\n")
            buf = []
            for _ in range(a.rows):
                c = rnd.choice(cats)
                s = rnd.choice(SUBCATS)
                mu, sd = CATEGORIES[c]
                buf.append(f"{c},{s},{rnd.gauss(mu, sd) + SUBCATS.index(s):.3f}\n")
                if len(buf) >= 10000:
                    f.writelines(buf)
                    buf.clear()
            f.writelines(buf)
        print(f"{path}  {os.path.getsize(path) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
