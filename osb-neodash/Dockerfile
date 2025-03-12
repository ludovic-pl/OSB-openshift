ARG NGINX_IMAGE=nginx:alpine
ARG NODE_IMAGE=node:lts-alpine
# build stage
FROM $NODE_IMAGE AS build-stage

RUN cat /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem  >> /etc/ssl/certs/ca-certificates.crt
RUN cp /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem /tmp/cert_sanofi.pem
RUN yarn config set cafile /tmp/cert_sanofi.pem
RUN npm config set cafile /tmp/cert_sanofi.pem
ENV NODE_EXTRA_CA_CERTS=/tmp/cert_sanofi.pem

RUN yarn global add typescript jest

# Run update
RUN apk add --no-cache git
# Pull and copy source code
RUN git clone https://github.com/neo4j-labs/neodash.git && cp -vr /neodash/. /.

COPY style.config.json public/
COPY style.css public/
COPY open_study_builder_logo.png public/
COPY ApplicationConfig.ts src/config/
COPY DashboardHeaderLogo.tsx src/dashboard/header/

RUN yarn install

RUN yarn run build-minimal

# production stage
FROM $NGINX_IMAGE AS neodash

RUN cat /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem  >> /etc/ssl/certs/ca-certificates.crt

RUN apk upgrade

ENV NGINX_PORT=5005

COPY --from=build-stage /dist /usr/share/nginx/html
COPY --from=build-stage /conf/default.conf.template /etc/nginx/templates/
COPY --from=build-stage /scripts/config-entrypoint.sh /docker-entrypoint.d/config-entrypoint.sh
COPY --from=build-stage /scripts/message-entrypoint.sh /docker-entrypoint.d/message-entrypoint.sh

RUN chgrp -R 0 /var/cache/nginx && \
    chmod -R g=u /var/cache/nginx
RUN chgrp -R 0 /var/log/nginx && \
    chmod -R g=u /var/log/nginx
RUN chgrp -R 0 /etc/nginx/ && \
    chmod -R g=u /etc/nginx/
RUN chgrp -R 0 /usr/share/nginx/ && \
    chmod -R g=u /usr/share/nginx/
RUN chgrp -R 0 /docker-entrypoint.d/ && \
    chmod -R g=u /docker-entrypoint.d/
RUN touch /var/run/nginx.pid && \
    chgrp -R 0 /var/run/nginx.pid && \
    chmod -R g=u /var/run/nginx.pid
RUN chmod +x /docker-entrypoint.d/config-entrypoint.sh  && \
    chmod +x /docker-entrypoint.d/message-entrypoint.sh

## Launch webserver as non-root user.
USER nginx

EXPOSE $NGINX_PORT

HEALTHCHECK cmd curl --fail "http://localhost:$NGINX_PORT" || exit 1
LABEL version="2.4.8"
