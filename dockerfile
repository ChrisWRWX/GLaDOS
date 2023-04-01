FROM python:3.10.10-slim-bullseye

LABEL maintainer="Christopher Ince"

COPY nginx.conf /etc/nginx/conf.d/
COPY frontend/build/ /usr/share/nginx/html/

COPY api/requirements.txt /tmp/
COPY api/ /api/

RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt
    
RUN apt-get update 
RUN apt-get install –y nginx 

RUN python /api/setup.py
