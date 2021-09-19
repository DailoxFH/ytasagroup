# ytasagroup
Watch synchronized YouTube Videos with your friends using flask. 

## How does it work?
Simply paste either the youtube id or the whole link (e.g. dQw4w9WgXcQ or https://www.youtube.com/watch?v=dQw4w9WgXcQ), choose your username and confirm it by clicking the button. A room, with a unique room id, is generated which you can share with your friends. They just need to visit your domain with the unique room id, also choose a username and you now can watch synchronized youtube videos.

It's event based, so if you start or stop the video, the change will be submitted to the server, the clients will be notified and do what you did. The actions will be logged in the event log on the right side, the last action will appear on the left side. All users who joined the room will also be logged on the right side of the screen, under the event log. If you want to play a new video, simply paste the id or the link at the bottom in the textbox and confirm by clicking the submit button. 

Everything stays in memory. To delete all users and rooms, just restart the server. I would recommend to customize processes in ytasagroup.ini to your liking. 


## Prerequisites (Ubuntu)
```
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx python3-venv
```

## Installation
```
git clone https://github.com/DailoxFH/ytasagroup.git
cd ytasagroup
python3 -m venv ytasagroupenv
source ytasagroupenv/bin/activate
pip install wheel
pip install -r requirements.txt
deactivate
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


