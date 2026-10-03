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

## Requirements and traceability

| ID | Requirement | Test type | Covered by | What is checked |
|----|-------------|-----------|------------|-----------------|
| REQ-1 | A command stores a name, JSON payload, priority, status, and reply, with defaults (status `pending`, priority 0) | Unit, integration, API | `test_models::test_defaults`, `test_forms::test_command_form_valid_data`, `test_forms::test_command_form_saves_to_db`, `test_views::test_form_submit_saves_command`, `test_views::test_submit_runs_mock_target`, `test_api::test_create_returns_201_and_completed`, `test_api::test_create_saves_one_row` | Defaults on a new row; name, payload, and priority accepted and saved through the form; status and reply stored after the mock target runs; the API returns name, payload, status, and reply; one row saved per create |
| REQ-2 | Invalid input is rejected and nothing is saved: empty name, payload that is not a JSON object, non-JSON payload text, empty payload, priority outside the allowed choices, missing required fields | Unit, integration, API, UI | `test_forms::test_command_form_invalid_data` (5 cases), `test_forms::test_command_form_empty_payload_is_invalid`, `test_views::test_invalid_submit_saves_nothing` (3 cases), `test_api::test__missing_required_fields`, `test_ui::test_invalid_json_shows_error_and_saves_nothing`, `test_ui::test_payload_must_be_an_object`, `test_ui::test_blank_name_shows_required_error` | Form rejects an empty name, a list payload, a number payload, non-JSON text, priority 9, and an empty payload; the web page saves nothing for an empty name, a list payload, and non-JSON text; the API returns 400 and saves nothing when payload and priority are missing; the browser shows an error and saves nothing for non-JSON text, a list payload, and a whitespace-only name |
| REQ-3 | The mock target completes a command with a known name and a valid `unit` (letter plus digits, like `A1`) | Unit, integration, API, UI | `test_services::test_mock_target`, `test_services::test_completed_with_valid_unit`, `test_views::test_submit_runs_mock_target`, `test_api::test_create_returns_201_and_completed`, `test_ui::test_valid_command_shows_completed` | Returns `completed` and an `ACK: move -> unit ...` reply; the web submit and the API both store `completed`; the page shows Completed and the ACK reply |
| REQ-4 | The mock target fails a command with a specific error for an unknown name, a missing `unit`, or an invalid `unit` | Unit, integration, API, UI | `test_services::test_missing_unit_fails` (3 cases), `test_services::test_invalid_unit_fails` (6 cases), `test_services::test_unknown_command_fails`, `test_views::test_failed_command_is_marked_failed`, `test_api::test_create_missing_unit_is_saved_as_failed`, `test_api::test_create_unknown_command_is_saved_as_failed`, `test_api::test_create_invalid_unit_is_saved_as_failed`, `test_ui::test_missing_unit_shows_failed`, `test_ui::test_unknown_command_shows_failed` | Exact `ERROR` text for a missing unit (`{}`, `None`, or another key) and an unknown command; `failed` status with an `ERROR: invalid unit` reply for `a1`, `A`, `1A`, `A1x`, an empty string, and `123`; the web page and API store `failed`; the page shows Failed and the error text for a missing unit and an unknown command |
| REQ-5 | History is listed newest first | Unit, API, UI | `test_models::test_newest_first_ordering`, `test_api::test_list_returns_created_commands_newest_first`, `test_ui::test_newest_command_is_listed_first` | Model ordering; API list order; newest row appears first in the page table |
| REQ-6 | The web page lets a user submit a command and see the reply; a successful submit redirects, so a refresh does not create a duplicate | Integration, UI | `test_views::test_index_view`, `test_views::test_form_submit_saves_command`, `test_views::test_valid_submit_redirects`, `test_ui::test_empty_state_message`, `test_ui::test_valid_command_shows_completed`, `test_ui::test_form_resets_after_successful_submit` | Page loads (200) with its title; submit saves a row; a valid submit returns 302; "No commands yet" when empty; the page shows the reply; the form is empty after a submit and one row exists after a reload |
| REQ-7 | The JSON API can create, list, and fetch commands | API | `test_api::test_create_returns_201_and_completed`, `test_api::test_list_empty`, `test_api::test_list_returns_created_commands_newest_first`, `test_api::test_detail_returns_command` | Create returns 201 with the saved command; list returns `{"results": []}` when empty and the created commands otherwise; detail returns the right name and id |
| REQ-8 | The API returns correct errors: 400 for bad input, 404 for a missing command, 405 for unsupported methods on `/api/commands/` | API | `test_api::test_body_that_is_not_json_returns_400`, `test_api::test_body_is_json`, `test_api::test__missing_required_fields`, `test_api::test_detail_missing_returns_404`, `test_api::test_method_not_allowed` | 400 and nothing saved for a non-JSON body, a JSON array body, and missing fields; 404 with an error message for an unknown id; 405 for `PUT` and `DELETE` |
| REQ-9 | The app stays responsive under simulated load | Performance | `locustfile.py` | 10 users: median 18 ms, p95 31 ms; 50 users: median 20 ms, p95 120 ms; 0 failures (local dev server) |
| REQ-10 | Tests run automatically on every change | CI | `.github/workflows/ci.yml` | Runs the tests with coverage on every push and pull request |

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