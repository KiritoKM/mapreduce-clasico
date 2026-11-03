FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY mapper.py reducer.py ./
# Los CSV se montan como volumen en /data/input (ver docker-compose.yml), así se
# pueden procesar muchos archivos sin reconstruir la imagen.
# El resultado se muestra en pantalla y además se guarda en /data/output/result.tsv
CMD sh -c "cat /data/input/*.csv | python3 mapper.py | LC_ALL=C sort | python3 reducer.py | tee /data/output/result.tsv"
