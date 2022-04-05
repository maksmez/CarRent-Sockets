FROM python:3.9.4
MAINTAINER MaksMez_ <maks.m.e@mail.ru>
WORKDIR ./carrent
COPY requirements.txt .
COPY config_server .
COPY database.db .
COPY server.py .
RUN pip install --no-cache-dir -r  requirements.txt
CMD ["python", "server.py"]
