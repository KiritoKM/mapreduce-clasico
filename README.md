# MapReduce: promedio y desviación estándar por categoría (Docker + Python)

Lab 2 – MapReduce. Calcula, con el paradigma MapReduce, el **promedio** y la **desviación estándar** de un valor agrupado por **categoría y subcategoría**, a partir de **uno o muchos archivos CSV**.

```
cat input/*.csv  →  mapper.py  →  sort  →  reducer.py
   (split)            (map)      (shuffle)   (reduce)
```

## Estructura

```
mapreduce-clasico/
├── docker-compose.yml
├── Dockerfile
├── mapper.py           emite  categoria<TAB>subcategoria<TAB>valor
├── reducer.py          por clave: n, promedio y desviación estándar
├── generate_data.py    genera muchos CSV grandes (prueba de volumen)
├── verify.py           compara el resultado contra un cálculo de fuerza bruta
├── input/              ventas_1.csv, ventas_2.csv, ventas_3.csv
└── output/             result.tsv
```

Formato de entrada: `categoria,subcategoria,valor`. Cada archivo puede tener su propio encabezado: las líneas cuyo último campo no es numérico se ignoran.

## Cómo ejecutar

```bash
docker compose up --build
```

Salida (también queda guardada en `output/result.tsv`):

```
categoria  subcategoria  n  promedio  desv_est
A          x             4  5.00      1.87
A          y             3  6.00      3.27
B          y             3  7.00      1.63
B          z             3  4.00      1.63
C          x             3  5.00      0.82
C          z             2  2.00      1.00
```

Para agrupar solo por categoría, como en el laboratorio original:

```bash
docker compose run --rm -e GROUP_BY_COLS=1 mapreduce
```

## Entregables

### 1. Promedio agrupado por dos columnas
[mapper.py](mapper.py) usa como clave las primeras `GROUP_BY_COLS` columnas y como valor la última.
- `GROUP_BY_COLS=2` (por defecto) agrupa por **categoría + subcategoría**.
- `GROUP_BY_COLS=1` agrupa solo por categoría.

Como la clave tiene varias columnas separadas por tabulador, [reducer.py](reducer.py) separa el valor con `rsplit("\t", 1)`: todo lo que está antes del último tabulador es la clave.

### 2. Reducer con desviación estándar
[reducer.py](reducer.py) usa el **algoritmo de Welford**:

```
n    += 1
δ     = x - media
media += δ / n
M2   += δ · (x - media)        desv_est = sqrt(M2 / (n - ddof))
```

- Recorre los valores una sola vez y usa **memoria constante**: no guarda la lista de valores, así que sirve para claves con millones de registros.
- Es numéricamente estable, a diferencia de `sqrt(E[x²] − E[x]²)`.
- `STD_DDOF=0` da la desviación **poblacional** (por defecto); `STD_DDOF=1` da la **muestral**.

### 3. Múltiples CSV y grandes volúmenes
- Los CSV se montan como **volumen** (`./input:/data/input`) en vez de copiarse a la imagen con `COPY`. Se pueden agregar archivos sin reconstruir la imagen, y `INPUT_DIR` apunta a cualquier carpeta.
- `cat /data/input/*.csv` concatena todos los archivos; los encabezados repetidos se descartan en el mapper.
- Mapper y reducer trabajan **línea por línea** (streaming), y `sort` hace un **ordenamiento externo** en disco. Nada necesita que todos los datos quepan en RAM.
- `LC_ALL=C sort` ordena por bytes, de forma consistente con la comparación de strings del reducer.

## Prueba de volumen

```bash
python generate_data.py --files 8 --rows 300000 --out input_big
```

En PowerShell:

```powershell
$env:INPUT_DIR="./input_big"; docker compose up --build; Remove-Item Env:INPUT_DIR
python verify.py input_big output/result.tsv
```

En bash:

```bash
INPUT_DIR=./input_big docker compose up --build && python verify.py input_big output/result.tsv
```

Con 8 archivos (26 MB, 2,4 millones de filas) tarda unos 20 s. Casi todo ese tiempo se va en `sort`, el *shuffle* centralizado en un solo proceso.
