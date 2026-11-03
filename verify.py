#!/usr/bin/env python3
"""
Verificación: calcula el resultado "a la fuerza bruta" (sin MapReduce, con el
módulo statistics) y lo compara con un archivo de resultado.

  python verify.py input output/result.tsv [GROUP_BY_COLS]
"""
import csv
import glob
import os
import statistics
import sys


def main():
    sys.stdout.reconfigure(encoding="utf-8")      # consola de Windows
    in_dir, result_path = sys.argv[1], sys.argv[2]
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    values = {}
    for path in sorted(glob.glob(os.path.join(in_dir, "**", "*.csv"), recursive=True)):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                try:
                    v = float(row[-1])
                except (ValueError, IndexError):
                    continue
                values.setdefault("|".join(x.strip() for x in row[:cols]), []).append(v)

    got, decimals = {}, 4
    with open(result_path, encoding="utf-8-sig") as f:
        delim = "	" if "	" in f.readline() else ","   # TSV (clásica) o CSV (Redis)
        for row in csv.reader(f, delimiter=delim):
            if len(row) < cols + 3:
                continue
            mean_txt = row[cols + 1]
            decimals = len(mean_txt.split(".")[1]) if "." in mean_txt else 0
            got["|".join(x.strip() for x in row[:cols])] = (
                int(row[cols]), float(mean_txt), float(row[cols + 2]))
    tol = 0.51 * 10 ** -decimals           # el resultado viene redondeado

    ok = set(values) == set(got)
    for k in sorted(values):
        n, mean, std = len(values[k]), statistics.fmean(values[k]), statistics.pstdev(values[k])
        g = got.get(k)
        match = g and g[0] == n and abs(g[1] - mean) <= tol and abs(g[2] - std) <= tol
        ok &= bool(match)
        print(f"{'OK ' if match else 'MAL'} {k:<10} esperado n={n} prom={mean:.4f} std={std:.4f}   obtenido={g}")
    print("\nTODO COINCIDE ✅" if ok else "\nHAY DIFERENCIAS ❌")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
