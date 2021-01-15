# Guides
[Back Home](index.md)

---

## Deploying
Depending on how you decide to run this app it will require different setups.
Docker Deployment is the prefered method.

These deployment guides do not currently instruct you on how to run with https.

### Docker Deployment
#### Using docker-compose
- Change the SECRET_KEY environment value to something secure
- After first run copy `default.conf` and `proxy_params` file into the ingress volume
- Running this will create three containers called: ingress, flask and database

#### Just Dockerfile
- Run docker file with required environment values (SECRET_KEY, DATABASE_URI)
- Create volume for the app data to be stored e.g. `hts:/data`
- If DATABASE_URI is blank it will use the default sqlite database stored in `/data`

### Non-Docker Deployment
You can run this project without Docker however setup for that is not shown in these guides
as there are multiple different ways it could be deployed.

---

## Configure App
### Environment Values
These are passed in using environment values

|Name             |Meaning                                     |Required|
|:----------------|:-------------------------------------------|:-------|
|FLASK_CONFIG_PATH|override path for the default flask.cfg file|NO      |
|SECRET_KEY       |the secret key (keep it secret)             |YES     |
|IMG_PATH         |override for the default img path           |NO      |
|DATABASE_URI     |the SQLALCHEMY_DATABASE_URI                 |NO      |

### flask.cfg file
These are given in the flask.cfg and are loaded before environment variables.
If you wish to override flask.cfg it is suggested to copy the default one and
then make your changes to prevent missing a required config.

|Name               |Meaning                                       |Required|
|:------------------|:---------------------------------------------|:-------|
|MAX_IMAGE_SIZE     |max image resolution for dynamic images       |YES     |
|JPEG_QUALITY       |the jpeg quality percentage as int            |YES     |
|ALLOWED_IMG_EXT    |the allowed image extentions                  |YES     |
|ADMINUSERNAME      |the admin username                            |YES     |
|MAX_SOCKET_MESS    |max number of queued messages if -1 has no max|NO      |
|MAX_SOCKET_PUT_WAIT|max number of seconds to wait if queue is full|NO      |

---

## First Run
When first run a default user will be created called "terminal".
The password for this account is the same as username.
This is the admin account which allows further user accounts to be created.
It is recomended to change the default password when setup is complete.

Depending on your hardware it may take a few seconds to load the first page,
this is due to the database being setup.

---

## Updating
In this project we use semantic versioning. You can learn more about it
[here](https://semver.org/).

Before updating to the next version it is important that you look at what has changed in that update,
if you have missed several versions please look at all of the change-logs of the major/minor updates.

- During a major update it is considered that it is not compatible with previous update
- During a minor update it is considered to be compatible with last update,
however it may need certain changes to the database, config files.
- During a fix/patch it is considered to be 100% compatible with
last update as it is only a bug fix or very minor feature change

To update using Docker simply pull the repo changes using git and then run a Docker build.
If database changes are required like renamed a column please do this when the server is down.

---
