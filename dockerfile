FROM python:3.10.10-slim-bullseye

LABEL maintainer="Christopher Ince"

COPY api/requirements.txt /tmp/
COPY api/ /api/

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get update 
RUN apt-get install -y nginx espeak

COPY nginx.conf /etc/nginx/sites-enabled/default
COPY frontend/build/ /usr/share/nginx/html/

RUN python /api/setup.py
RUN openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=US/ST=Michigan/L=Upper Michigan/O=Aperture Science, Inc./OU=Testing Department/CN=aperturescience.com"

CMD nginx; cd /api && python app.py
