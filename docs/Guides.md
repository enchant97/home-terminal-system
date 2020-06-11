# Guides
[Back Home](index.md)
## Setup On Initial Install
### Adding Your Config
When you have cloned the project you will need to configure the app.
To do this you will need to navigate to HomeTerminal/config.py.
You can then copy any config names that you want to change into the production class for example:
`SQLALCHEMY_DATABASE_URI` can be changed to connect to a different database.
When running in production mode, by default it will use sqlite and
save in HomeTerminal/appdata.db otherwise it will be in memory.
### First Run
When first run a default user will be created called terminal.
The password for this account is the same as username.
This is the admin account which allows further user accounts to be created.
It is recomended to change the default password when setup is complete.
