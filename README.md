# DPV Keycloak Config

This is a short description of the contents of this repository. A full German description is
available as the "DPV Cloud Handbuch".

## Setup description
This configuration contains two profiles: One for local development and one for DPV Cloud
production. The both share the following containers:

- db: maria database server
- redis: redis cache
- keycloak: keycloak container
- proxy: nginx container
- backup: custom backup script

## Installation

### Local setup
With the following command you can pull and build all containers:
```
docker-compose -f docker-compose.yml -f docker-compose.local.yml build --pull
```
Make sure to fill all the required values in the *.env files before continuing.
Start the microservices with:
```
docker-compose -f docker-compose.yml -f docker-compose.local.yml up
```
This will show you all the logs in your current terminal, which is probably a good
idea for first start. If you want to run in background, just append `-d` or `--detach`.

### Production setup
```
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --pull
```
Make sure to fill all the required values in the *.env files before continuing.
Start the microservices with:
```
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```
This will show you all the logs in your current terminal, which is probably a good
idea for first start. If you want to run in background, just append `-d` or `--detach`.

##
You can reach the master console via:

http://localhost/admin/master/console


### Theme development setup

In local mode, the theme cache is deactivated by mounting disable-theme-cache.cli. So no further action needed. 

## Manually deactivate theme cache
```
docker exec -it --user root keycloak_keycloak /bin/bash
```
If you need nano :D 
```
microdnf install nano
```
Then modify the following file: 

```
nano /opt/jboss/keycloak/standalone/configuration/standalone.xml
```
And replace
```
<theme>
    <staticMaxAge>2592000</staticMaxAge>
    <cacheThemes>true</cacheThemes>
    <cacheTemplates>true</cacheTemplates>
    <welcomeTheme>${env.KEYCLOAK_WELCOME_THEME:keycloak}</welcomeTheme>
    <default>${env.KEYCLOAK_DEFAULT_THEME:keycloak}</default>
    <dir>${jboss.home.dir}/themes</dir>
</theme>
```
by
```
<theme>
<staticMaxAge>-1</staticMaxAge>
<cacheThemes>false</cacheThemes>
<cacheTemplates>false</cacheTemplates>
<welcomeTheme>${env.KEYCLOAK_WELCOME_THEME:keycloak}</welcomeTheme>
<default>${env.KEYCLOAK_DEFAULT_THEME:keycloak}</default>
<dir>${jboss.home.dir}/themes</dir>
</theme>
```

## Build theme

```
cd extensions
gradle build
cp ./dpv-theme/build/libs/dpv-theme.jar ./prebuild/dpv-theme.jar 
```