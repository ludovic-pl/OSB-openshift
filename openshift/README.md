# OSB deployment on Openshift

Openshift deployment of OSB is not fully mature for the moment.
In this project we make some configuration to build and deploy OSB on openshift.
A more mature deployment needs to use templates.

The configuration available in this repo can be deploy OSB on an openshift platform in four steps:

1. Imagestreams initialization

2. Buildconfigs files import and build

3. Deployment and services import using helm files

4. Routes configurations

Config files are in yaml format and available in the folder `openshift/`.
They can be imported using the yaml import tool of Openshift (available in web UI or in openshift console).

Most of configuration to import are in the files `openshift/*/full-deploy.yaml`.

## Pre-requisites

The associated source code needs to be available in a git repository.
During the deployment, we use a public git.
In case of a private git, some configuration will be needed for the buildconfig files (not tested or covered in this documentation).

In the following, `git_url` refers to the git URL containing the related source code.

## Initialize imagestreams

The imagestreams object can be imported using the file `openshift/imagestreams/full-deploy.yaml`.
No further configuration is needed for the imagestreams.

## Import buildconfigs files and run build
The file `openshift/buildconfigs/full-deploy.yaml` contains all the buildconfigs needed to deploy OSB.
First things first all the `<git_url>` in the file need to be replace by the `git_url`.
After the import, the build can be runned for each build configs except for the database (buildconfig `dbdata` and `dbexpose`).

For the database the process is more complexes.
The first step is to build the `dbdata` image.
Configure the buildarg variable `DBDATA` in the buildconfig `dbexpose` to be the URL of the `e2e-metadata-dbdata` imagesream.
Run the build of `dbexpose` when the `dbdata` build is done.

## Import deployment and services using helm files

Import he file `openshift/helm/full-deploy.yaml` in openshift.
With this file, all the service and deployment needed for the application will be deployed.

## Configure routes
The file `openshift/routes/full-deploy.yaml` contains all the buildconfigs needed to deploy OSB.
Two elements need to be configured in this file:
* `<api_swagger_service_url>`: which is the URL of the `api-swagger` service
* `<frontend_service_url>`: which is the URL of the `frontend` service

# Conclusion

By following these steps, everything should be set.
OSB interface is accessible using the URL created by the route named `frontend-route`.
The API swagger is accessible using the URL created by the route name `api-route-swagger`.
