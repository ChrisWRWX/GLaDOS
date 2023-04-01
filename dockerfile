FROM python:3.10.10-slim-bullseye

LABEL maintainer="Christopher Ince"

COPY api/requirements.txt /tmp/
COPY api/ /api/

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get update 
RUN apt-get install -y nginx espeak

COPY nginx.conf /etc/nginx/sites-enabled/default
COPY frontend/build/ /usr/share/nginx/html/

RUN python /api/setup.py

CMD nginx; cd /api && python app.py
