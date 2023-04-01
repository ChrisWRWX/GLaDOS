FROM nginx

LABEL maintainer="Christopher Ince"

COPY nginx.conf /etc/nginx/conf.d/
COPY frontend/dist/ /usr/share/nginx/html/