# Udacity full stack developer second project

## Python Files:
There is two python files:
* application.py: the primary application which operates a webserver to serve the web app
* database_setup.py: this initializes the database models (tables) necessary for communicating with the database

### Python Dependencies (libraries):

* sqlalchemy
* flask
* functools
* requests
* [google-auth](https://google-auth.readthedocs.io/en/latest/)

### System Dependencies:

* sqlite3
* python3

## Usage:

write in command prompt (cmd on windows,terminal in linux...etc), e.g. `python3 application.py`.

## technical info:
### Basic info:
This application has a build in web server that surves a web catalog for car makers and car models the user can authinticate via google account or github account and add,edit or delete their own data.

### API:
there is two JSON endpoints:
* `/model/<id>/JSON`: displays a single car model of id <id>
* `/carmaker/<id>/JSON`: displays all car models grouped by carmaker
