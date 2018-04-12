FROM onap/dcae-tosca-base:1.0.4

RUN apk add --no-cache \
    curl \
    && :

COPY ./app /srv/

COPY ./docker/docker-entrypoint.sh /srv/

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

RUN chmod +x /srv/tosca_server.py && \
    chmod +x /srv/docker-entrypoint.sh

RUN pip3 install -r /srv/requirements.txt

EXPOSE 8085 

ENTRYPOINT ["/srv/docker-entrypoint.sh", "/usr/local/bin/uwsgi", "--ini", "/srv/web/uwsgi.ini"]
