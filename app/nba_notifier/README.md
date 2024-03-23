# Django NBA Notifier

Gametime is a Django web application using the NBA API to monitor live basketball games. 
It sends text message notifications to registered users when a game is within a 10-point margin with 8 minutes or less in 
the 4th quarter. 
The project is Dockerized, integrates with Jenkins for CI/CD, and is hosted on AWS Elastic Beanstalk.

## Project Structure

- **Dockerfile**: Docker configuration.
- **Jenkinsfile**: Jenkins CI/CD pipeline.
- **nba_notifier/**
  - **game_monitor/**: Django app.
    - **backup_tasks.py**: Backup tasks.
    - **forms.py**: User phone registration form.
    - **models.py**: User phone model.
    - **static/**: Static files.
    - **templates/**: HTML templates.
    - **urls.py**: URL routing.
    - **views.py**: Views.
  - **gettoken.py**: Script for obtaining tokens.
  - **scoreboard.json**: File for live NBA data (testing).
  - **update_scoreboard.py**: Script for updating NBA scoreboard.
  - **settings.py**: Django project settings.
  - **requirements.txt**: Python dependencies.
  - **manage.py**: Django management script.
  - **staticfiles/**: Collected static files.
  - **venv/**: Virtual environment.

## Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/your-username/django-nba-notifier.git
   cd django-nba-notifier
   pip install -r requirements.txt
   python manage.py runserver
   http://127.0.0.1:8000/




