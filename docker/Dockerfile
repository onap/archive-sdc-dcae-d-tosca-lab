FROM python:3.5-alpine

RUN apk add --update --no-cache \
    autoconf \
    gcc \
    libc-dev \
    linux-headers \
    nginx \
    curl \
    && pip install --upgrade setuptools \
    && pip install gunicorn

RUN apk del \
    autoconf \
    gcc \
    libc-dev \
    linux-headers \
    && :

RUN mkdir -p /run/nginx /run/gunicorn && \
    touch /run/nginx/nginx.pid && \
    chown -R nginx:nginx /var/log/nginx /run/nginx /run/gunicorn && \
    chmod 0775 /var/log/nginx && \
    chmod 0770 /var/lib/nginx/tmp /run/gunicorn && \
    chmod 0664 /run/nginx/nginx.pid

COPY app /srv/

COPY docker/docker-entrypoint.sh /srv/

COPY nginx/nginx.conf /etc/nginx/nginx.conf

RUN chmod +x /srv/tosca_server.py && \
    chmod +x /srv/docker-entrypoint.sh

RUN pip3 install -r /srv/requirements.txt

EXPOSE 8085 

ENTRYPOINT ["/srv/docker-entrypoint.sh", "/usr/local/bin/gunicorn", "-c", "/srv/web/gunicorn.conf" , "tosca_server:application"]
