# Guides
[Back Home](index.md)

## Deploying
Depending on how you decide to run this app it will require different setups.
Docker Deployment is the preferred method.

## Configure App
These are passed in using environment values or a .env file

| Name                | Meaning                                        | Required |
|:--------------------|:-----------------------------------------------|:---------|
| SECRET_KEY          | the secret key (keep it secret)                | YES      |
| DATABASE_URI        | What database to connect to                    | YES      |
| IMG_PATH            | override for the default img path              | NO       |
| MAX_IMAGE_SIZE      | max image resolution for dynamic images        | NO       |
| JPEG_QUALITY        | the jpeg quality percentage as int             | NO       |
| ALLOWED_IMG_EXT     | the allowed image extensions                   | NO       |
| ADMIN_USERNAME      | the admin username                             | NO       |
| MAX_SOCKET_MESS     | max number of queued messages if -1 has no max | NO       |
| MAX_SOCKET_PUT_WAIT | max number of seconds to wait if queue is full | NO       |

| Database   | URI                                                                             |
|:-----------|:--------------------------------------------------------------------------------|
| SQLite     | `sqlite:///file_path`                                                           |
| MySQL      | `mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]`             |
| PostgreSQL | `postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]` |

## First Run
When first run a default user will be created called "terminal".
The password for this account is the same as username.
This is the admin account which allows further user accounts to be created.
It is recommended to change the default password when setup is complete.

Depending on your hardware it may take a few seconds to load the first page,
this is due to the database being setup.

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

