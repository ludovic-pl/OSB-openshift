ARG NGINX_IMAGE=nginx:alpine
ARG NODE_IMAGE=node:lts-alpine

## Build stage
FROM $NODE_IMAGE as build-stage

RUN cat /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem  >> /etc/ssl/certs/ca-certificates.crt
RUN cp /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem ./cert_sanofi.pem
RUN yarn config set cafile ./cert_sanofi.pem

WORKDIR /app

## Install Node packages
COPY ./package*.json ./
RUN yarn install

## Version information
ARG BUILD_NUMBER
ARG BUILD_BRANCH
ARG BUILD_COMMIT
ENV BUILD_NUMBER="$BUILD_NUMBER" \
    BUILD_BRANCH="$BUILD_BRANCH" \
    BUILD_COMMIT="$BUILD_COMMIT"

# Build the app
COPY ./ .
RUN yarn run update-config /app/build.json
RUN yarn docs:build

## Production stage
FROM $NGINX_IMAGE as production-stage

RUN cat /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem  >> /etc/ssl/certs/ca-certificates.crt

COPY --from=build-stage /app/docs/.vuepress/dist /usr/share/nginx/html
COPY --from=build-stage /app/build.json /usr/share/nginx/html
COPY --from=build-stage /app/sbom.md /usr/share/nginx/html
COPY --from=build-stage /app/LICENSE.md /usr/share/nginx/html/license.md
COPY ./nginx/default.conf /etc/nginx/conf.d/

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

ARG PORT=5006
ENV PORT=$PORT
EXPOSE $PORT

## Runs healthcheck on the application root
## checks every `interval` seconds, fails if `timeout`,
## unhealthy status is reached if `retries` number of consecutive failures,
## but failures does not count within `start-period` seconds of start.
HEALTHCHECK --start-period=10s --timeout=2s --interval=10s --retries=2 CMD \
    curl --fail --silent --show-error --max-time 1 \
    "http://localhost:$PORT/" \
    > /dev/null || exit 1
