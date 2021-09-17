# ytasagroup
Watch synchronized YouTube Videos with your friends

## Prerequisites (Ubuntu)
```
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx python3-venv
```

## Installation
```
git clone https://github.com/DailoxFH/ytasagroup.git
python3 -m venv ytasagroupenv
source ytasagroupenv/bin/activate
pip install wheel
pip install -r requirements.txt
```

To start the server:
```
ytasagroupenv/bin/uwsgi --ini ytasagroup.ini
```
Processes in ytasagroup.ini of course can be customized. 

## Nginx
```
sudo nano /etc/nginx/sites-available/ytasagroup
```
Config:
```
server {
    listen 80;
    server_name your_domain;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:{PATH_TO_PROJECT}/ytasagroup.sock;
    }
}
```
Enable, check for errors and restart:
```
sudo ln -s /etc/nginx/sites-available/ytasagroup /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```


