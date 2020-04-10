# Updating
[Back Home](index.md)
## Updating the local repository from source
```
cd PROJECTPATH/hometerminal
git stash save
git pull
git stash pop
sudo supervisorctl reload
```
If you have run git stash it will allow you to keep the config.py edits and any other changes.

## Notes about version numbers
In this project we use semantic versioning. You can learn more about it
[here](https://semver.org/). But here is the basics:

Say we have version 2.3.1
-   The first shows what major version it is on, this should increment when there is a
incompatible change, like for example when a existing database table is changed.
-   The second shows a minor version, this should increment when there is a change
however it will work with older version of the same major version number
-   The last shows what patch it is on, this is used to show that a bugfix was
issued that adds no new functionality into the code

Now you know what the different version numbers are for you will most likely have to
reset the database when incrementing to a major change. You may also incounter a new configuration
that is required, so after a update always look at the base config class.
