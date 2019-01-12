# Udacity full stack developer Fifth project linux server configuration

## Website Info:
website is hosted on Amazon lightsail
Ip address: 3.121.185.127
SSH Port: 2200

### VPS configration:
follow the following steps: 

### 1:
- create a username grader by excuting the following command: ```sudo adduser grader```
- give the grader sudo access with ```usermod -aG sudo grader```

### 2:
- Update and upgrade packages: ```sudo apt update``` then ```sudo apt upgrade``` 

### 3:
- change the SSH port : ```sudo nano /etc/ssh/sshd_config``` then change port number from 22 to 2200
- then restart the ssh service by: ```sudo service ssh restart```

### 4:configure the firewall to close all the ports but SSH port 2200 and HTTP port 80 and NTP port 123:

- ```sudo ufw allow 2200/tcp```<br />
- ```sudo ufw deny 22```<br />
- ```sudo ufw allow 80/tcp```<br />
- ```sudo ufw allow 123/udp```<br />
- ```sudo ufw allow ssh```<br />
- ```sudo ufw allow www ```<br />
- ```sudo ufw allow ftp```<br />
- ```sudo ufw enable```<br />

### 5: change the time zone to UTC:
- by ```sudo dpkg-reconfigure tzdata``` then choose none of the above then choose UTC

### 6: Generate SSH key:
- Run ```ssh-keygen```
- save the file in /home/user/.ssh/id_rsa
- switch to grader ```sudo login grader```
- make ssh directory in grader ```mkdir .ssh```
- make authorized_keys file  ```touch .ssh/authorized_keys```
- Give the permissions : ```chmod 700 .ssh``` and ```chmod 644 .ssh/authorized_keys.```<br />
- ```nano /etc/ssh/sshd_config``` , change PasswordAuthentication to ```no``` <br />
- then restart the SSH service ```sudo service ssh restart```

### 7: Install Apache and mod_wsgi:
- ```sudo apt-get install apache2``` and ```sudo apt-get install libapache2-mod-wsgi python-dev```
- Enable mod_wsgi with ```sudo a2enmod wsgi```
- start the webserver ```sudo service apache2 start```

### 8: Clone the Catalog from Github:
- First install git ```sudo apt-get install git```
- Navigate to www directory: ```cd /var/www```
- make catalog directory: ```sudo mkdir catalog```
- navigate to catalog ```cd catalog```
- clone the repo  ```git clone "github repo link" catalog```

### 9: Create a catalog.wsgi file:

- run ```nano catalog.wsgi```, Then write this inside catalog.wsgi:<br /> <br />
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/catalog/")
from catalog import app as application
application.secret_key = 'secret key'
WTF_CSRF_ENABLED = True
```
.<br />

- Then rename application.py (your main python file)  to ```__ini__.py```  ```mv application.py __init__.py```<br />

### 10: install dependencies:
- Flask ```pip3 install Flask```
- And the catalog project dependencies: ```sudo pip3 install httplib2 oauth2client sqlalchemy flask-sqlalchemy psycopg2-binary bleach requests sqlalchemy_utils``

### 11: Configure and enable virtual host:
- with ```sudo nano /etc/apache2/sites-enabled/000-default.conf```
- and change it with your server info

### 12: Install Postgres:
- ```sudo apt-get install libpq-dev python-dev```
- ```sudo apt-get install postgresql postgresql-contrib```
- ```sudo su - postgres```
- Then we create database for our project by:
- ```psql```
- ```CREATE USER catalog WITH PASSWORD 'password';```<br />
- ```ALTER USER udacity CREATEDB;```<br />
- ```CREATE DATABASE catalog WITH OWNER udacity;```<br />
- ```\c catalog```<br />
- ```REVOKE ALL ON SCHEMA public FROM public;```<br />
- ```GRANT ALL ON SCHEMA public TO catalog;```<br />
# - DO NOT FORGET TO CHANGE YOUR DATABASE ENGINE IN YOUR APPLICATION

### 13: Restart our apache server:
- we restart apache so the changes apply  ```sudo service apache2 restart```
-Done.

## technical info:
### Basic info:
This application has a build in web server that surves a web catalog for car makers and car models the user can authinticate via google account or github account and add,edit or delete their own data.

### API:
there is two JSON endpoints:
* `/model/<id>/JSON`: displays a single car model of id <id>
* `/carmaker/<id>/JSON`: displays all car models grouped by carmaker
  
  
### References:
- https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
- https://www.ostechnix.com/configure-apache-virtual-hosts-ubuntu-part-1/
