# Test Lab Dashboard

![tests](https://github.com/roccolep/Test_Lab_Dashboard/actions/workflows/ci.yml/badge.svg)

A small Django app that sends commands to a mock target, shows the reply, and keeps a history. The app is deliberately simple. The focus of the project is the test suite around it: unit, integration, API, browser (UI), smoke, regression, and performance testing, with coverage measurement and CI.

## What the app does

1. A user fills in a form on the home page: a command name, a JSON payload, and a priority.
2. The command is saved, then sent to a mock target (a Python function standing in for a real system).
3. The mock target replies with an `ACK` (status **completed**) or an `ERROR` (status **failed**).
4. The page shows the full history, newest first, with status, reply, and timestamp.
5. The same functionality is available as a JSON API.

**Mock target rules** (`commands/services.py`): a command completes if its name is a known command and its payload contains a `unit` in the form letter + digits (for example `A1`). Otherwise it fails with a specific message: unknown command, missing `unit`, or invalid `unit`.

## Tech

Python, Django, SQLite, pytest, pytest-django, pytest-cov, Playwright, Locust, GitHub Actions.

## Setup

**Mac / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Windows (PowerShell)**
```
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000. For the browser tests, install the browser once with `playwright install chromium`.

## URLs

| URL | Method | Purpose |
|-----|--------|---------|
| `/` | GET, POST | Web page: form and history table |
| `/api/commands/` | GET | List all commands as JSON |
| `/api/commands/` | POST | Create a command from a JSON body (returns 201) |
| `/api/commands/<id>/` | GET | One command as JSON (404 if missing) |

Example:
```
curl -i -X POST http://127.0.0.1:8000/api/commands/ \
  -H "Content-Type: application/json" \
  -d '{"name": "move", "payload": {"unit": "A1"}, "priority": 1}'
```

## Running the tests

| Command | What it runs |
|---------|--------------|
| `pytest` | Everything |
| `pytest -m smoke` | Fast sanity checks: is the app basically alive? |
| `pytest -m regression` | Full behavior set, rerun after every change |
| `pytest -m api` | JSON API tests |
| `pytest -m ui` | Browser tests (Playwright) |
| `pytest --cov=commands --cov-report=term-missing` | Coverage report |
| `pytest -m ui --headed` | Browser tests with a visible browser |

### Markers

- **smoke**: a small hand-picked set (page loads, a valid submit saves, the happy path completes). If these fail, nothing else is worth running.
- **regression**: most behavior checks, including every edge case and error message. Rerun after every change to catch anything that used to work.
- **api**: tests that call the JSON endpoints.
- **ui**: tests that drive a real browser through the real page.

## Results

Last full run: **53 tests, all passing, about 2 seconds.**

| Suite | Tests |
|-------|-------|
| Smoke | 4 |
| Regression | 44 |
| API | 13 |
| UI (Playwright) | 9 |
| **Total** | **53** |

**Coverage:** 100% line coverage of the `commands` app (107 statements, 0 missed). Coverage shows that every line ran during the tests. The assertions are what check the behavior, so the numbers above should be read together with the test descriptions below.

## Test types covered

| Type | Where | What it checks |
|------|-------|----------------|
| Unit | `test_services.py`, `test_forms.py`, `test_models.py` | Mock target rules, form validation, model defaults, ordering, and `__str__` in isolation |
| Integration | `test_views.py` | Form submit through the view, mock target, and database to the rendered page |
| API | `test_api.py` | Status codes, JSON shape, and error handling (201, 400, 404, 405) |
| UI / end to end | `test_ui.py` | A real browser fills in the form and reads the result |
| Smoke | marker `smoke` | App is alive |
| Regression | marker `regression` | Existing behavior still works |
| Performance | `locustfile.py` | Behavior under simulated load |
| Coverage | pytest-cov | Which lines the tests reach |
| CI | `.github/workflows/ci.yml` | Tests run automatically on every push |

## Performance testing

Load tested with Locust (`locustfile.py`). Each simulated user loads the home page 3 times for every 1 command created through `POST /api/commands/`.

| Users | Duration (s) | Requests | RPS | Median (ms) | p95 (ms) | Failures |
|-------|--------------|----------|-----|-------------|----------|----------|
| 10 | 83 | 636 | 7.63 | 18 | 31 | 0 |
| 50 | 81 | 2,695 | 33.19 | 20 | 120 | 0 |

For the 10-user run, `GET /` had a median of 21 ms and `POST /api/commands/` had a median of 8 ms.

**Conditions:** Django development server with SQLite on a MacBook, Locust and the server on the same machine. These numbers describe that setup only and are not a prediction of production performance.

**Observations:** Throughput scaled almost linearly from 10 to 50 users, with no failures. The median stayed flat at about 20 ms, but the 95th percentile rose from 31 ms to 120 ms, so the slowest requests were affected first as load increased. The home page lists every command, so it also gets heavier as rows are added during a run.

Run it yourself:
```
python manage.py runserver
locust -f locustfile.py --host http://127.0.0.1:8000
```
Then open http://localhost:8089.


## Project layout

```
config/            Django project settings and root URLs
commands/          The app: models, forms, views, services, URLs, template
  services.py      Mock target and submit()
tests/             test_models, test_forms, test_services, test_views, test_api, test_ui
locustfile.py      Load test
pytest.ini         Settings and registered markers
.github/workflows  CI
```