# Contributing
[Back Home](index.md)

## Prerequisites
-   Have the requirements for deploying the project
-   [Git](https://git-scm.com/)
-   [pytest](https://pypi.org/project/pytest/) to run unit tests in python

## Getting The Sources
First fork the repository to your GitHub account, then clone your fork locally:
```
git clone https://github.com/<<<your-github-account>>>/House_Terminal_System.git
```

You will want to update your repository every so often with your fork
```
cd House_Terminal_System
git checkout master
git pull https://github.com/enchant97/House_Terminal_System.git master
```
Then merge any conflicts, commit them and then push them to your fork.

## Pull Requests
We will analyise the code to make sure it meets our standards,
if small corrections are required we will apply them for you.

Always remember to create one pull request per issue and
[link the issue in the pull request](https://github.blog/2011-10-12-introducing-issue-mentions/).

Make sure to follow the coding guide lines
-   We use master branch for tested/fully-working commits, use dev for pull requests
-   Don't change `__version__` we will decide what version it will be released for
-   Use 4 spaces for indentation for python code as per python pep8 guide and 2 spaces for css files.
-   Use doc strings for functions/classes and line comments for advanced algorithms
-   Use double quotes for python strings
-   Avoid using lambdas in python code
-   Make sure to use DRY code
-   If creating a table model make sure to use one of the base classes to inheriting from
-   Test your code fully before submiting a pull request (don't just use pytest actually use the program)
-   It is intended for the database to be fully compatible with MYSQL, postgresql and sqlite
-   Try not to add new app configs that do not have defaults,
this is to minimise changes for the user who is deploying this project

## Where To Contribute
Check the [full issues list](https://github.com/enchant97/House_Terminal_System/issues).
Note just because an issue exists it does not mean we will accept a contribution. There are
several reasons why we may not accept a pull request:
-   Performance - We want to develop a fast web app that can run on the smallest server
(like a Raspberry Pi 2 Model B)
-   User Experience - We want to make our project easy for almost any user to be able to use it
-   Feature change - A feature change that will need to be developed in a certain way
and be relevant to the way we want to develop our program

## Suggestions
We are interested in your feedback for the Home Terminal. You can submit a
suggestion or feature request through the issue tracker.
Be sure to leave detailed information on what feature you want.

Also, to avoid repetition make sure to check the roadmap and
the issue tracker to see if your suggestion has already been thought of.
