# Gametime

Gametime is a Django application that monitors live NBA and WNBA games and
notifies registered users when a game is close late in regulation. It uses
Celery and Redis for scheduled score checks, Twilio for SMS delivery, and an
ESPN fallback when the official NBA live-score endpoint is unavailable.

## Highlights

- Live NBA and WNBA scoreboard polling with a resilient NBA provider fallback.
- Configurable close-game alerts: 10 points or fewer with eight minutes or less
  remaining in the fourth quarter.
- Background jobs scheduled by Celery Beat and processed by Celery workers.
- Safe local development mode: SMS calls are printed unless Twilio credentials
  are configured.
- Automated Django checks, tests, and linting in GitHub Actions.

## Tech stack

Python 3.11, Django, Celery, Redis, SQLite, Twilio, Docker, pytest, and Ruff.

## Local setup

### Quick Demo (No Docker)
```bash
git clone https://github.com/nweekes423/Gametime.git
cd Gametime
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app/manage.py migrate
./demo-simple.sh  # Automated demo script
```

### Full Docker Demo
```bash
./demo-recruiter.sh  # Automated Docker demo with all services
```

### Manual Setup
```bash
python app/manage.py runserver
```

Open <http://127.0.0.1:8000> after starting the server. The provided `.env`
uses fake SMS mode by default; add valid Twilio values only in your local
environment or deployment secret manager.

## Background score checks

Start Redis, then run these commands in separate terminals:

```bash
redis-server
cd app && ../venv311/bin/celery -A nba_notifier worker --loglevel=info
cd app && ../venv311/bin/celery -A nba_notifier beat --loglevel=info
```

If the official NBA CDN returns an invalid response, Gametime logs the issue
and automatically fetches the NBA scoreboard from ESPN instead.

## Verification

```bash
source venv311/bin/activate
python app/manage.py check
pytest -p no:cacheprovider app/game_monitor/tests -q
ruff check --no-cache app
```

## Environment variables

Copy `.env.example` to `.env` and configure only what you need:

- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`
- `TWILIO_FAKE_MODE=True` for local development without sending SMS

Never commit `.env`, databases, generated scoreboards, TLS keys, or tokens.
