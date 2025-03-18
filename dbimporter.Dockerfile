ARG PYTHON_IMAGE=python:3.13.0-slim

# --- Build stage ----
FROM $PYTHON_IMAGE AS build-stage

ARG reportDate="2024-01-05 14:54:32 +0100"

ARG CDISC_DATA_DIR="mdr_standards_import/container_booting/"

RUN cp -v /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem /usr/local/share/ca-certificates/custom-cert.crt
RUN update-ca-certificates

## Install required system packages, for clinical-mdr-api as well
RUN apt-get update \
    && apt-get -y install \
    ca-certificates-java \
    openjdk-17-jre-headless \
    git \
    curl \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    jq \
    gcc \
    net-tools \ 
    && pip install --upgrade pip pipenv wheel \
    && apt-get clean && rm -rf /var/lib/apt/lists && rm -rf ~/.cache

# Environment variables for database
ARG NEO4J_MDR_BOLT_PORT=7687
ARG NEO4J_MDR_HTTP_PORT=7474
ARG NEO4J_MDR_HTTPS_PORT=7473
ARG NEO4J_MDR_HOST=localhost
ARG NEO4J_MDR_AUTH_USER=neo4j
ARG NEO4J_MDR_DATABASE=mdrdb
ARG NEO4J_MDR_DATABASE_DBNAME=mdrdockerdb
ARG NEO4J_MDR_AUTH_PASSWORD=$neo4jpwd
ARG NEO4J_CDISC_IMPORT_BOLT_PORT=7687
ARG NEO4J_CDISC_IMPORT_HOST=localhost
ARG NEO4J_CDISC_IMPORT_AUTH_USER=neo4j
ARG NEO4J_CDISC_IMPORT_AUTH_PASSWORD=$neo4jpwd
ARG NEO4J_CDISC_IMPORT_DATABASE=cdisc-import
ARG NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

WORKDIR /import

COPY ./default_neo4j.sh .
# Copy program files for neo4j-mdr-db and mdr-standards-import
COPY ./neo4j-mdr-db neo4j-mdr-db
COPY ./mdr-standards-import mdr-standards-import
COPY ./studybuilder-import studybuilder-import
COPY ./clinical-mdr-api clinical-mdr-api

# Copy environment file for mdr-standards-import
COPY ./studybuilder-import/.env.import mdr-standards-import/.env

# Set up environments for studybuilder-import
COPY ./studybuilder-import/.env.import studybuilder-import/.env

RUN chgrp -R 0 /import && \
    chmod -R g=u /import

CMD [ "sh", "./default_neo4j.sh" ]