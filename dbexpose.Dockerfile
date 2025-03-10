ARG NEO4J_IMAGE=neo4j:5.19.0-enterprise

# --- Prod stage ----
# Copy database directory from build-stage to the official neo4j docker image
FROM $NEO4J_IMAGE AS production-stage

ARG DBDATA
ARG UID=1000
ARG USER=neo4j
ARG GROUP=neo4j

RUN cp -v /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem /usr/local/share/ca-certificates/custom-cert.crt
RUN update-ca-certificates
RUN echo $neo4jpwd


# Match id of neo4j user with the current user on the host for correct premissions of db dumps mounted folder
RUN [ "x$UID" = "x1000" ] || { \
    echo "Changing uid & gid of neo4j user to $UID" \
    && usermod --uid "$UID" "neo4j" \
    && groupmod --gid "$UID" "neo4j" \
    ;}

# Install APOC plugin
RUN wget --quiet --timeout 60 --tries 2 --output-document /var/lib/neo4j/plugins/apoc.jar \
    https://github.com/neo4j/apoc/releases/download/5.19.0/apoc-5.19.0-core.jar

# Copy database backup from build stage
COPY --from=$DBDATA --chown=$USER:$GROUP /neo4j/data/backup /data/backup

# Set up default environment variables
ENV NEO4J_AUTH=neo4j/${neo4jpwd} \
    NEO4J_apoc_trigger_enabled="true" \
    NEO4J_apoc_import_file_enabled="true" \
    NEO4J_apoc_export_file_enabled="true" \
    NEO4J_dbms_databases_seed__from__uri__providers="URLConnectionSeedProvider" \
    NEO4J_apoc_initializer_system_1="CREATE DATABASE mdrdb OPTIONS {existingData: 'use', seedURI:'file:///data/backup/mdrdockerdb.backup'} WAIT 60 SECONDS"

RUN echo ${NEO4J_AUTH}
# Volume attachment point: if an empty volume is mounted, it gets populated with the pre-built database from the image
VOLUME /data


RUN chgrp -R 0 /data && \
    chmod -R g=u /data

RUN chgrp -R 0 /var/lib/neo4j && \
    chmod -R g=u /var/lib/neo4j

HEALTHCHECK --start-period=60s --timeout=3s --interval=10s --retries=3 \
    CMD wget --quiet --spider --timeout 2 --tries 1 "http://localhost:7474/" || exit 1

