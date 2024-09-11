# Company Count Application

This repository contains the Company Count Application, a Django-based project with Celery for task management, Gunicorn as the application server, and Nginx as a reverse proxy.

## Prerequisites

1. **Python 3.12.x**: Ensure Python 3.12.x is installed on your system.
2. **PostgreSQL**: Required for the database.
3. **Redis**: Required as the message broker for Celery.
4. **Nginx**: Required as the reverse proxy.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/RohitRK1130/CompanyCountApplication
cd CompanyCountApplication
```

### 2. Create and Activate a Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Update Environment Variables
Create a .env file in the root directory of the project and add the following configurations:
```bash
SECRET_KEY=<key>
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,13.126.48.243
DATABASE_NAME=<db-name>
DATABASE_USER=<db-user>
DATABASE_PASSWORD=<db-pass>
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=UTC
```

### 5. Set Up the Database
Run the following commands to set up the database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```
### 6. Set Up Celery Service
Create a systemd service file for Celery:
```bash
sudo nano /etc/systemd/system/celery.service
```
Add the following content:
```bash
[Unit]
Description=Celery Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/CompanyCountApplication
ExecStart=/home/ubuntu/venv/bin/celery -A CompanyMetrics worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```
Reload systemd to apply changes and start the Celery service:
```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
```
### 7. Set Up Gunicorn Service
Create a systemd service file for Gunicorn:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```
Add the following content:
```bash
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/CompanyCountApplication/
ExecStart=/home/ubuntu/venv/bin/gunicorn --access-logfile - --workers=1 --preload --log-level debug --bind unix:/home/ubuntu/CompanyCountApplication/app.sock CompanyMetrics.wsgi:application

[Install]
WantedBy=multi-user.target
```
Reload systemd to apply changes and start the Celery service:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
### 6. Configure Nginx
Create an Nginx configuration file for your project:
```bash
sudo nano /etc/nginx/sites-available/companycount
```
Add the following content:
```bash
server {
    listen 80;
    server_name 127.0.0.1 13.126.48.243;

    location / {
        proxy_pass http://unix:/home/ubuntu/CompanyCountApplication/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the Nginx configuration and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/companycount /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
