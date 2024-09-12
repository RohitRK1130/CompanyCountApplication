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
### 6. Start Celery Service (For backend proccess)
To start the Celery Service use below command
```bash
celery -A CompanyMetrics worker --loglevel=info
```

### 7. Start Server
To start the server use below command
```bash
python manage.py runserver
```
