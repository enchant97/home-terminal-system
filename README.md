# Home Terminal System (HTS)
## Project structure:
```
/PROJECTNAME:
    /PROJECTNAME
    /setup-files
    /run.py
    /requirments.txt
    /venv
```
## Notes:
* ufw = firewall
* nginx = static file webserver
* gunicorn = WSGI server 
## How to deploy (Linux):
### Installing required programs
```
sudo apt-get install ufw nginx supervisor git
```
### Setup filewall
```
ufw disable
sudo ufw default deny
sudo ufw allow ssh
sudo ufw allow http/tcp
sudo ufw enable
```
### Clone project folder
```
git clone https://github.com/enchant97/House_Terminal_System.git PROJECTNAME
cd /PROJECTNAME
python3 -m venv PROJECTNAME/venv
source venv/bin/activate
```
### Setup Nginx
make sure to edit the default file with the project name
```
sudo rm /etc/nginx/sites-enabled/default
sudo cp setup-files/nginx-sitesenabled.conf /etc/nginx/sites-enabled/PROJECTNAME.conf
sudo systemctl restart nginx`
```
### Setup supervisor
```
sudo mkdir -p /var/log/PROJECTNAME
sudo touch /var/log/PROJECTNAME/PROJECTNAME.err.log
sudo touch /var/log/PROJECTNAME/PROJECTNAME.out.log
sudo nano /etc/supervisor/conf.d/PROJECTNAME.conf
sudo supervisorctl reload
```
## Further setup for https
**Coming Soon!**
```
sudo ufw allow 443
sudo cp setup-files/nginx-sitesenabled_https.conf /etc/nginx/sites-enabled/PROJECTNAME.conf
```
