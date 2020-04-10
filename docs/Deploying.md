# Deploying
[Back Home](index.md)
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
git clone https://github.com/enchant97/House_Terminal_System.git hometerminal
cd /hometerminal
python3 -m venv hometerminal/venv
source venv/bin/activate
```
### Setup Nginx
make sure to edit the default file with the project name
```
sudo rm /etc/nginx/sites-enabled/default
sudo cp setup-files/nginx-sitesenabled.conf /etc/nginx/sites-enabled/hometerminal.conf
sudo systemctl restart nginx`
```
### Setup supervisor
```
sudo mkdir -p /var/log/hometerminal
sudo touch /var/log/hometerminal/hometerminal.err.log
sudo touch /var/log/hometerminal/hometerminal.out.log
sudo nano /etc/supervisor/conf.d/hometerminal.conf
sudo supervisorctl reload
```
## Further setup for https
```
sudo ufw allow 443
sudo cp setup-files/nginx-sitesenabled_https.conf /etc/nginx/sites-enabled/hometerminal.conf
```
### Create a self-signed https cetificate
```
openssl req -newkey rsa:4096 \
    -x509 \
    -sha256 \
    -days 3650 \
    -nodes \
    -out CERTNAME.crt \
    -keyout KEYNAME.key \
    -subj "/C=EN/ST=Kent/L=Canterbury/O=exampleorginisation/OU=example department/CN=www.example.com"
```
The fields, specified in -subj line are listed below:
* C= - Country name. The two-letter ISO abbreviation.
* ST= - State or Province name.
* L= - Locality Name. The name of the city where you are located.
* O= - The full name of your organization.
* OU= - Organizational Unit.
* CN= - The fully qualified domain name.
* [Source](https://linuxize.com/post/creating-a-self-signed-ssl-certificate/)
