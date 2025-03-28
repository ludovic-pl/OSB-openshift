# OSB deployment on Openshift

Openshift deployment of OSB is not fully mature for the moment.
A clean deplyment can be done using template.
There wasn't enough time for this demonstrator to produce a template.
The deployment has more steps than a deplyment using templates.

OSb deployment on an Openshift platform is in 3 steps

1. Initialize imagestreams

2. Import of buildconfigs files and run build

3. Import deployment and services using helm files

4. Configure routes

Config files are in yaml format.
They can be imported using the yaml import tool of Openshift (available in web UI or in openshift console).

## Pre-requisities

All of the files in the aarchive need to be available in a GIT file.
The git url noted `git_url` will be used to construct the container images.

The git must be public.
If the git must be private, credentials can be configured in the buildconfig.
But this process is not covered in this documentation.

## Initialize imagestreams

## Import buildconfigs files and run build
The file `openshift/buildconfigs/full-deploy.yaml` contains all of the buildconfigs needed to deply OSB.
First things first all of the `'https://github.com/ludovic-pl/OSB-openshift.git'` url need to be replace by the `git_url`.
After the import, the build can be runned for each build configs except for the database (buildconfig `dbdata` and `dbexpose`).

For the database the process is more complexe.
The first step is to build the `dbdata` image.
Configure the buildarg variable `DBDATA` in the buildconfig `dbexpose` to be the url of the `e2e-metadata-dbdata` imagesream.
Run the build of `dbexpose` when the `dbdata` build is done.

## Import deployment and services using helm files

Import he file `openshift/helm/full-deploy.yaml` in openshift.
With this file, all of the service and deployment needed for the application will be deployed.

## Configure routes

In this step we explain how to create the route without a assigned domaine name or certificate.
As in the previous step, the routes can be imported by loading the file `openshift/routes/full-deploy.yaml` into openshift.
