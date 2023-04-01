FROM python:3.10.10-slim-bullseye

LABEL maintainer="Christopher Ince"

COPY api/requirements.txt /tmp/
COPY api/ /api/

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get update 
RUN apt-get install -y nginx 

COPY nginx.conf /etc/nginx/conf.d/
COPY frontend/build/ /usr/share/nginx/html/


RUN python /api/setup.py

CMD nginx -g daemon off;cd /api && python /app.py