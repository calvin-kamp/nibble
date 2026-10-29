# Nibble API

Backend for Nibble, a web app for tracking nutrition and sharing recipes. Users
log the food they eat, compare it with their daily targets, record their weight
and publish recipes that a moderator approves. The project is a Django REST
Framework API; the Vue frontend in [`../frontend`](../frontend/README.md) talks
to it over HTTP.

- **Framework:** Django 6.1 with Django REST Framework 3.18
- **Authentication:** JWT (SimpleJWT) in `HttpOnly` cookies, CSRF check on every write
- **Database:** PostgreSQL 17, started as a container
- **Background jobs:** Celery with Redis (e-mails, account deletion, food import)
- **Food data:** Open Food Facts, imported into the own database
- **Runtime:** Python 3.13 inside Docker, served by gunicorn

The full API specification is in [`openapi.yaml`](openapi.yaml). Error messages
are German, field names and enum values are English.

---

## Table of contents

- [Quick start](#quick-start)
- [Try the API](#try-the-api)
- [Admin panel](#admin-panel)
- [Food data](#food-data)
- [Useful commands](#useful-commands)
- [Configuration](#configuration)
- [Running in production](#running-in-production)
- [Project layout](#project-layout)
- [Background jobs](#background-jobs)
- [How recipe moderation works](#how-recipe-moderation-works)
- [Authentication](#authentication)
- [Consent and personal data](#consent-and-personal-data)
- [Errors and rate limits](#errors-and-rate-limits)
- [API reference](#api-reference)
- [Tests](#tests)
- [Troubleshooting](#troubleshooting)

---

## Quick start

**Requirements:** [Docker](https://docs.docker.com/get-docker/) with Docker
Compose v2. Nothing else has to be installed on your machine.

Create the `.env` file from the template:

**Windows (PowerShell)**

```powershell
Copy-Item .env.template .env
```

**macOS / Linux**

```bash
cp .env.template .env
```

Open `.env` and replace `YOUR_SECRET_KEY`, `YOUR_JWT_SIGNING_KEY` and
`CHANGE_ME` (twice: `POSTGRES_PASSWORD` and `DATABASE_URL`). All other values of
the template work for local development as they are, see
[Configuration](#configuration).

Build and start the containers:

```bash
docker compose up --build
```

The API is now available at `http://localhost:8000/`.

`docker compose up` starts five containers:

| Service  | Purpose                                                                         |
| -------- | ------------------------------------------------------------------------------- |
| `db`     | PostgreSQL 17, port `5432`                                                      |
| `redis`  | Cache (rate limits, stats) and queue for the background jobs, port `6379`       |
| `api`    | gunicorn on port `8000`, every endpoint at the root                              |
| `worker` | Celery worker: sends e-mails, deletes accounts, imports foods                   |
| `beat`   | Celery beat: starts the scheduled jobs, see [Background jobs](#background-jobs) |

The migrations are part of the repository and are applied automatically when the
`api` container starts. The food search stays empty until the products are
imported once, see [Food data](#food-data).

Every command of this README is run from the folder that contains `manage.py`
(`backend/`).

---

## Try the API

Every request with `POST`, `PUT`, `PATCH` or `DELETE` needs the header
`X-CSRFToken`. Its value comes from `GET /auth/csrf`, which also sets the
`csrftoken` cookie. The login sets the tokens as cookies, so the following
requests have to reuse them: PowerShell keeps them in a session variable, curl in
a cookie file. Postman works as well and stores the cookies by itself.

**Windows (PowerShell)**

Use `Invoke-RestMethod`. The `curl` command of PowerShell is something else and
does not accept the bash examples.

```powershell
$api = "http://localhost:8000"

# 1. Get the CSRF token; the cookies are stored in $session
$csrf = (Invoke-RestMethod -Uri "$api/auth/csrf" -SessionVariable session).csrf_token
$headers = @{ "X-CSRFToken" = $csrf }

# 2. Register (logs in right away)
$register = @{ email = "demo@example.com"; password = "S3cure-Passw0rd!" } | ConvertTo-Json

Invoke-RestMethod -Uri "$api/auth/register" -Method Post -ContentType "application/json" -Body $register -Headers $headers -WebSession $session

# 3. Choose a username and give the privacy consent
Invoke-RestMethod -Uri "$api/profile" -Method Patch -ContentType "application/json" -Body (@{ username = "demo" } | ConvertTo-Json) -Headers $headers -WebSession $session

Invoke-RestMethod -Uri "$api/privacy/consent" -Method Put -ContentType "application/json" -Body (@{ accepted = $true; policy_version = "1" } | ConvertTo-Json) -Headers $headers -WebSession $session

# 4. Read the account state
Invoke-RestMethod -Uri "$api/auth/me" -WebSession $session | ConvertTo-Json -Depth 5
```

**macOS / Linux**

```bash
API=http://localhost:8000

# 1. Get the CSRF token; the cookies are stored in cookies.txt
CSRF=$(curl -s -c cookies.txt $API/auth/csrf | sed -E 's/.*"csrf_token":"([^"]+)".*/\1/')

# 2. Register (logs in right away)
curl -b cookies.txt -c cookies.txt -X POST $API/auth/register \
  -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" \
  -d '{"email": "demo@example.com", "password": "S3cure-Passw0rd!"}'

# 3. Choose a username and give the privacy consent
curl -b cookies.txt -X PATCH $API/profile \
  -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" \
  -d '{"username": "demo"}'

curl -b cookies.txt -X PUT $API/privacy/consent \
  -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF" \
  -d '{"accepted": true, "policy_version": "1"}'

# 4. Read the account state
curl -b cookies.txt $API/auth/me
```

Expected response of step 4:

```json
{
  "id": 1,
  "email": "demo@example.com",
  "email_verified": false,
  "username": "demo",
  "privacy_consent": true,
  "onboarding": { "completed": false, "current_step": "goal" },
  "is_staff": false,
  "deletion_scheduled_for": null
}
```

The registration only works once per address; use another address for a second
run. The verification e-mail is printed in the log of the worker
(`docker compose logs worker`), because `.env.template` sets
`EMAIL_URL=consolemail://`. All endpoints are listed in the
[API reference](#api-reference).

---

## Admin panel

Create an account for the admin panel:

```bash
docker compose exec api python manage.py createsuperuser
```

The panel is reachable at `http://localhost:8000/admin/`. There you can edit
users, profiles, recipes, submissions, foods, meals, entries, goals and weights.
A superuser is also staff, so the same account can use the moderation endpoints
of the API.

---

## Food data

The food search reads from the own database, not from the Open Food Facts API.
Import the products once:

```bash
# Development: stop after 5000 products
docker compose exec api python manage.py import_off_products --limit 5000

# Full import
docker compose exec api python manage.py import_off_products
```

The command streams the CSV export of Open Food Facts (about 1.5 GB) and stores
nothing on disk. Only products from Germany, Austria and Switzerland pass, with a
name, all four nutrients and a scan within the last two years. Stored are
barcode, name, brand, unit (g or ml), package and serving size, and kcal,
protein, carbs and fat per 100.

| Option              | Effect                                                                     |
| ------------------- | -------------------------------------------------------------------------- |
| `--limit N`         | Stops after `N` products and keeps all others.                             |
| `--scan-years N`    | Only products scanned in the last `N` years. `0` imports all. Default `2`. |
| `--source PATH_URL` | Another URL or path of the export (`.csv` or `.csv.gz`).                   |

Without `--limit`, products that are no longer in the export are deleted at the
end. Tracked entries keep their own copy of the values. The full import also runs
every Sunday at 04:00, see [Background jobs](#background-jobs).

---

## Useful commands

```bash
# Follow the logs of the API or the worker
docker compose logs -f api
docker compose logs -f worker

# Run the migrations manually
docker compose exec api python manage.py migrate

# Open a Django shell
docker compose exec api python manage.py shell

# Send a test e-mail directly, without the worker
docker compose exec api python manage.py sendtestemail you@example.com

# Remove metadata from recipe images stored before the cleanup existed
docker compose exec api python manage.py strip_image_metadata --dry-run
docker compose exec api python manage.py strip_image_metadata

# Run the tests
docker compose exec api python manage.py test

# Stop the containers
docker compose down

# Stop the containers and delete the database
docker compose down -v
```

---

## Configuration

All settings are environment variables. They are set in the `.env` file, which
is created from `.env.template` (see [Quick start](#quick-start)).
`compose.yaml` overrides `DATABASE_URL`, `REDIS_URL` and
`CELERY_BROKER_URL` for the containers, so the values in `.env` are only used
when Django runs outside Docker.

| Variable                         | Required | Example                                      | Purpose                                                                                   |
| -------------------------------- | -------- | -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `SECRET_KEY`                     | yes      | `k3j...`                                     | Django's cryptographic key. No default, the server needs it.                              |
| `DEBUG`                          | no       | `True`                                       | Debug mode. Defaults to `False`; never enable it in production.                           |
| `ALLOWED_HOSTS`                  | no       | `localhost,127.0.0.1`                        | Comma-separated hostnames the server answers for. Required when `DEBUG=False`.            |
| `CORS_ALLOWED_ORIGINS`           | no       | `http://localhost:5173`                      | Comma-separated origins the frontend may call the API from.                               |
| `CSRF_TRUSTED_ORIGINS`           | no       | `http://localhost:5173`                      | Comma-separated origins whose writes pass the CSRF check.                                 |
| `JWT_SIGNING_KEY`                | no       | `p9x...`                                     | Key that signs the tokens. Falls back to `SECRET_KEY`.                                    |
| `AUTH_COOKIE_SECURE`             | no       | `False`                                      | `True` sends the auth and CSRF cookies only over HTTPS. Defaults to `True`.               |
| `AUTH_COOKIE_DOMAIN`             | no       | `.example.com`                               | Cookie domain when frontend and API run on subdomains. Not set locally.                   |
| `AUTH_COOKIE_REFRESH_PATH`       | no       | `/auth/`                                     | Path of the refresh cookie. Defaults to `/auth/`.                                         |
| `SECURE_SSL_REDIRECT`            | no       | `False`                                      | Redirect to HTTPS. Defaults to `True`.                                                    |
| `SECURE_HSTS_SECONDS`            | no       | `0`                                          | HSTS duration in seconds. Defaults to one year.                                           |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | no       | `False`                                      | HSTS for subdomains. Defaults to `False`.                                                 |
| `SESSION_COOKIE_SECURE`          | no       | `False`                                      | `Secure` flag on the admin session cookie. Defaults to `True`.                            |
| `NUM_PROXIES`                    | no       | `1`                                          | Number of reverse proxies in front of the API, so the rate limits see the client IP.      |
| `LOG_DRIVER`                     | no       | `json-file`                                  | Docker log driver. Defaults to `journald`, see [Running in production](#running-in-production). |
| `FRONTEND_URL`                   | no       | `http://localhost:5173`                      | Base of the links in e-mails.                                                             |
| `EMAIL_URL`                      | no       | `consolemail://`                             | Mail server as URL. Defaults to `consolemail://`, which prints the e-mails to the log.    |
| `DEFAULT_FROM_EMAIL`             | no       | `Nibble <noreply@example.com>`               | Sender of all e-mails.                                                                    |
| `POSTGRES_DB`                    | yes      | `nibble`                                     | Name of the database the `db` container creates.                                          |
| `POSTGRES_USER`                  | yes      | `nibble`                                     | Database user.                                                                            |
| `POSTGRES_PASSWORD`              | yes      | `choose-a-password`                          | Database password.                                                                        |
| `DATABASE_URL`                   | yes      | `postgres://nibble:pw@localhost:5432/nibble` | Connection string outside Docker.                                                         |
| `REDIS_URL`                      | yes      | `redis://localhost:6379/0`                   | Cache outside Docker.                                                                     |
| `CELERY_BROKER_URL`              | no       | `redis://localhost:6379/1`                   | Queue of the background jobs outside Docker. Falls back to `REDIS_URL`.                   |
| `OFF_DUMP_URL`                   | no       | `https://static.openfoodfacts.org/...`       | Source of the food import. Defaults to the official export.                               |

**Local development over HTTP** needs these values, which `.env.template`
already contains: `AUTH_COOKIE_SECURE=False`, `SECURE_SSL_REDIRECT=False`,
`SECURE_HSTS_SECONDS=0` and `SESSION_COOKIE_SECURE=False`. Browsers do not send
`Secure` cookies over HTTP, so with the defaults every request after the login
answers `401`.

**E-mail over SMTP:** `EMAIL_URL` has the form
`smtp+ssl://USER:PASSWORD@HOST:465` (or `smtp+tls://...:587`). Special characters
in user and password have to be URL-encoded, for example `@` as `%40`. The
`worker` container sends the e-mails, so it needs this value too.

`CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` have to contain the exact
origin the frontend is served from, including protocol and port.

The server will not start without `SECRET_KEY` and `REDIS_URL`.

---

## Running in production

```bash
docker compose up -d --build
```

Before deploying, set in `.env`:

- `DEBUG=False`
- `AUTH_COOKIE_SECURE=True` and serve the API over HTTPS
- `AUTH_COOKIE_DOMAIN=.example.com` when frontend and API run on subdomains of
  the same domain
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the real
  domains
- `NUM_PROXIES=1` behind a reverse proxy
- `EMAIL_URL` and `DEFAULT_FROM_EMAIL` for the real mail server
- delete the four lines `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`,
  `SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SESSION_COOKIE_SECURE`; without them the
  safe defaults apply
- delete `LOG_DRIVER`, so the containers log to journald (see below)
- new random values for `SECRET_KEY` and `JWT_SIGNING_KEY`. Generate a random
  value, once per key, with (no local Python needed):

```bash
docker compose run --rm --no-deps --entrypoint python api -c "import secrets; print(secrets.token_urlsafe(50))"
```

Django serves the recipe images under `/media/` itself, also with `DEBUG=False`.
They are stored in the `media_data` volume, so they survive a redeploy.

### Server logs (14 days at most)

The access log of gunicorn contains only the path, without the query string; the
referrer loses everything after `?` as well (`config/gunicorn_logger.py`). Search
terms therefore never reach the log.

Docker rotates `json-file` and `local` logs by size only, not by age. In
production every container writes to the journald of the host instead, which
deletes entries after 14 days. Run once on the server (needs a systemd host):

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nMaxRetentionSec=14day\n' | sudo tee /etc/systemd/journald.conf.d/nibble.conf
sudo systemctl restart systemd-journald
```

The limit applies to the whole journal of the host. Read the logs with
`journalctl CONTAINER_NAME=nibble-api`. Docker Desktop has no journald, so local
development uses `LOG_DRIVER=json-file`.

---

## Project layout

```
config/            Project configuration: settings, root URLs, Celery, error format,
                   base throttles, shared fields, serializers and validators
apps/accounts/     Users and profiles: registration, login, onboarding, consent,
                   body data, account deletion and data export
apps/recipes/      Recipes, saved recipes and moderation
apps/foods/        Open Food Facts products, food search and import command
apps/tracking/     Nutrition (goals, food entries, meals, daily summary) and weight
apps/stats/        Public numbers for the landing page
```

An app with one area keeps its API layer in `api/`. An app with several areas
has one package per area instead. Each package holds its `serializers.py`,
`views.py` and `urls.py` and, where needed, `throttles.py`, `permissions.py`,
`utils.py` or `exceptions.py`:

```
apps/accounts/     auth/  account/  onboarding/  profile/  privacy/
apps/recipes/      catalog/  moderation/
apps/tracking/     nutrition/  weight/
apps/foods/        api/
apps/stats/        api/
```

What only one package uses lives in that package. What several packages of an
app share lives in the app folder: `models.py`, `services.py` (logic that is not
tied to a request) and files like `permissions.py` or `mixins.py`. Tests are in
the app's `tests/` package; helpers shared by several test files are in
`tests/test_utils.py`. The app labels stay `accounts`, `recipes` and so on, so
table names and migrations are the same as without the `apps/` folder.

| File                               | Content                                                            |
| ---------------------------------- | ------------------------------------------------------------------ |
| `apps/accounts/services.py`        | Onboarding step rules, e-mails, account deletion, data export      |
| `apps/accounts/tokens.py`          | Signed tokens for the links in e-mails, token blacklist            |
| `apps/accounts/authentication.py`  | Reads the token from the cookie and enforces the CSRF check        |
| `apps/accounts/auth/cookies.py`    | Sets and deletes the auth cookies                                  |
| `apps/accounts/profile/`           | Username and body data (birth date, height, sex; `/tracking/body`) |
| `apps/recipes/services.py`         | Moderation workflow and notifications                              |
| `apps/recipes/utils.py`            | Removes metadata (location, camera) from uploaded images           |
| `apps/tracking/mixins.py`          | Login and consent for every tracking endpoint                      |
| `apps/tracking/services.py`        | Deletes all health data when the consent is revoked                |
| `apps/tracking/nutrition/utils.py` | Values from amount and unit, daily totals                          |
| `apps/tracking/weight/utils.py`    | Weekly averages and trend                                          |
| `apps/stats/services.py`           | Counts users, recipes, foods and entries                           |
| `apps/*/tasks.py`                  | Background jobs, see [Background jobs](#background-jobs)           |

Other files in the root: `compose.yaml`, `Dockerfile`, `entrypoint.sh`
(runs the migrations and `collectstatic` on start), `openapi.yaml` and
`.env.template`.

---

## Background jobs

Celery runs work outside the request. `redis` holds the queue, `worker` executes
the jobs and `beat` adds the scheduled ones to the queue.

| Job                                           | When                       | Content                                            |
| --------------------------------------------- | -------------------------- | -------------------------------------------------- |
| `config.tasks.send_email_task`                | after every e-mail trigger | Sends one e-mail; retries up to 5 times on failure |
| `apps.accounts.tasks.delete_expired_accounts` | daily, 03:00               | Deletes accounts whose 7-day period has ended      |
| `apps.accounts.tasks.flush_expired_tokens`    | daily, 03:30               | Removes expired tokens from the blacklist          |
| `apps.foods.tasks.import_off_products`        | Sundays, 04:00             | Full food import, see [Food data](#food-data)      |

E-mails are queued only after the database transaction has been saved, so no
e-mail goes out for a change that was rolled back. All times are `Europe/Berlin`.

---

## How recipe moderation works

Every recipe starts as `pending` and is only visible to its author until a staff
member approves it.

1. The author creates a recipe. It is `pending`, and every staff account gets an
   e-mail.
2. A staff member approves or rejects it
   (`POST /moderation/submissions/{id}/approve`, or `/reject` with a reason).
   An author with a verified address gets an e-mail with the result.
3. While a recipe was never approved, every change edits it directly and sends it
   back to moderation.
4. Once approved, the public version stays unchanged. Every change by the author
   (content, new image or removed image) is collected in one open revision until
   a staff member approves or rejects it.

Images are limited to 5 MB. Metadata such as location and camera model is
removed on upload.

---

## Authentication

Login and registration set two cookies. There is no `Authorization` header.

| Cookie          | Lifetime   | Path         | Purpose                                |
| --------------- | ---------- | ------------ | -------------------------------------- |
| `access_token`  | 15 minutes | `/`          | Authenticates every protected request. |
| `refresh_token` | 7 days     | `/auth/`     | Used to get new tokens and to log out. |
| `csrftoken`     | session    | `/`          | Value for the `X-CSRFToken` header.    |

`access_token` and `refresh_token` are `HttpOnly`; `csrftoken` is readable by the
frontend. All three are `SameSite=Lax`; `Secure` follows `AUTH_COOKIE_SECURE`.
The client has to send credentials with every request, otherwise the cookies are
neither stored nor sent. With `fetch` this is `credentials: "include"`.

Flow in the frontend:

1. On page load, call `GET /auth/me`.
2. On `401`, call `POST /auth/refresh` once and repeat the request. The
   refresh issues a new refresh token and blocks the old one, so an active
   session lasts 7 days from the last use.
3. If the refresh fails, the session has ended and the frontend shows the login.

Every `POST`, `PUT`, `PATCH` and `DELETE` needs the header `X-CSRFToken`, also
before the login. Without it the API answers `403 csrf_failed`.

A changed password blocks all refresh tokens of the user, so other devices are
logged out after at most 15 minutes. An unverified account can use everything;
it only receives no notification e-mails. Links in e-mails are valid for 3 days
(verification), 24 hours (e-mail change) and 1 hour (password reset).

---

## Consent and personal data

| Rule                   | Behaviour                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------- |
| Tracking needs consent | Every endpoint under `/tracking/` answers `403 consent_required` without consent.  |
| Revoking the consent   | Deletes all entries, meals, goals, weights and body data at once. Recipes stay.        |
| Consent history        | Every decision is stored with time and policy version.                                 |
| Data export            | `GET /account/export` returns everything stored about the user as JSON.            |
| Account deletion       | `POST /account/deletion` schedules the deletion in 7 days; `DELETE` takes it back. |
| After the deletion     | Approved recipes stay without author, everything else is deleted.                     |

---

## Errors and rate limits

Every error has the same shape. `errors` only appears for validation errors:

```json
{
  "code": "validation_error",
  "message": "Die Eingabe ist ungültig.",
  "errors": { "policy_version": ["Gib die Version des Datenschutztexts an."] }
}
```

Exceeding a limit answers `429 throttled` with the header `Retry-After`. The
counters are stored in Redis.

| Endpoint                                                | Limit                                                      |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| `POST /auth/register`                               | 10 per hour per IP                                         |
| `POST /auth/login`                                  | 5 per minute per IP                                        |
| `POST /auth/refresh`                                | 30 per minute per IP                                       |
| `POST /auth/password/forgot`                        | 5 per hour per IP, 3 per hour per address                  |
| `POST /auth/email/verification/resend`              | 3 per hour per user                                        |
| `POST /auth/password/change`                        | 5 per 15 minutes per user                                  |
| `POST /auth/email/change`                           | 3 per hour per user                                        |
| `GET /profile/username-availability`                | 60 per minute per user                                     |
| `POST /account/deletion`, `GET /account/export` | 3 per hour per user each                                   |
| all other endpoints                                     | 120 per minute per user, 60 per minute per IP without login |

---

## API reference

Base URL: `http://localhost:8000/`

All request and response bodies are JSON, except the image upload
(`multipart/form-data`). Paths have no trailing slash. Request and response
bodies of every endpoint are described in [`openapi.yaml`](openapi.yaml); open it
in an OpenAPI viewer such as the Swagger Editor for a readable version.

Access: **public** works without login, **login** needs the access cookie,
**consent** needs login and a given privacy consent, **staff** needs a staff
account.

### Auth

| Method | Path                              | Access | Purpose                                                   |
| ------ | --------------------------------- | ------ | --------------------------------------------------------- |
| GET    | `/auth/csrf`                      | public | Sets the `csrftoken` cookie and returns its value         |
| POST   | `/auth/register`                  | public | `{ email, password }`; creates the account and logs in    |
| POST   | `/auth/login`                     | public | `{ email, password }`; sets the auth cookies              |
| POST   | `/auth/refresh`                   | public | Uses the refresh cookie; renews both cookies              |
| POST   | `/auth/logout`                    | public | Blocks the refresh token and deletes the cookies          |
| GET    | `/auth/me`                        | login  | Account state: e-mail, username, consent, onboarding step |
| POST   | `/auth/email/verify`              | public | `{ token }` from the verification link                    |
| POST   | `/auth/email/verification/resend` | login  | Sends the verification e-mail again                       |
| POST   | `/auth/email/change`              | login  | `{ email, password }`; sends a link to the new address    |
| POST   | `/auth/email/change/confirm`      | public | `{ token }`; sets the new address                         |
| POST   | `/auth/password/change`           | login  | `{ current_password, new_password }`                      |
| POST   | `/auth/password/forgot`           | public | `{ email }`; always `204`, so addresses cannot be guessed |
| POST   | `/auth/password/reset`            | public | `{ token, new_password }`                                 |

### Account, onboarding and profile

| Method | Path                             | Access | Purpose                                                |
| ------ | -------------------------------- | ------ | ------------------------------------------------------ |
| POST   | `/account/deletion`              | login  | `{ password }`; schedules the deletion in 7 days       |
| DELETE | `/account/deletion`              | login  | Takes the scheduled deletion back                      |
| GET    | `/account/export`                | login  | All stored data as JSON                                |
| GET    | `/onboarding`                    | login  | Current step                                           |
| PATCH  | `/onboarding`                    | login  | Moves to another step, for example to skip the targets |
| POST   | `/onboarding/complete`           | login  | Finishes the onboarding                                |
| GET    | `/profile`                       | login  | Username and creation date                             |
| PATCH  | `/profile`                       | login  | `{ username }`; sets or changes the username           |
| GET    | `/profile/username-availability` | login  | `?username=...`; checks whether a username is free     |
| GET    | `/privacy/consent`               | login  | Current consent                                        |
| PUT    | `/privacy/consent`               | login  | `{ accepted, policy_version }`; gives or revokes it    |

### Recipes and moderation

| Method     | Path                                   | Access | Purpose                                                                          |
| ---------- | -------------------------------------- | ------ | -------------------------------------------------------------------------------- |
| GET        | `/recipes`                             | public | Approved recipes, paginated, with filters (`q`, `diet`, `intolerances` and more) |
| POST       | `/recipes`                             | login  | Creates a recipe (`pending`)                                                     |
| GET        | `/recipes/{id}`                        | public | One recipe                                                                       |
| PUT        | `/recipes/{id}`                        | login  | Changes an own recipe                                                            |
| DELETE     | `/recipes/{id}`                        | login  | Deletes an own recipe                                                            |
| PUT/DELETE | `/recipes/{id}/image`                  | login  | Uploads, replaces or removes the image                                           |
| PUT/DELETE | `/recipes/{id}/saved`                  | login  | Saves or unsaves a recipe                                                        |
| GET        | `/moderation/submissions`              | staff  | Submitted recipes and revisions, paginated                                       |
| GET        | `/moderation/submissions/{id}`         | staff  | One submission                                                                   |
| POST       | `/moderation/submissions/{id}/approve` | staff  | Approves the submission                                                          |
| POST       | `/moderation/submissions/{id}/reject`  | staff  | `{ reason }`; rejects the submission                                             |

### Foods and tracking

| Method         | Path                                            | Access  | Purpose                                                |
| -------------- | ----------------------------------------------- | ------- | ------------------------------------------------------ |
| GET            | `/foods/search`                                 | login   | `?q=...` or `?barcode=...`, paginated                  |
| GET/PATCH      | `/tracking/goal`                                | consent | Goal and daily targets                                 |
| GET/PATCH      | `/tracking/body`                                | consent | Birth date, height and sex                             |
| POST           | `/tracking/entries`                             | consent | Tracks a food: barcode, amount, unit, date, meal type  |
| POST           | `/tracking/entries/from-meal`                   | consent | Tracks a saved meal                                    |
| PATCH/DELETE   | `/tracking/entries/{id}`                        | consent | Changes or deletes an entry                            |
| GET            | `/tracking/days/{date}`                         | consent | Daily summary compared with the targets                |
| GET/POST       | `/tracking/meals`                               | consent | Saved meals made of several foods                      |
| GET/PUT/DELETE | `/tracking/meals/{id}`                          | consent | One saved meal                                         |
| GET/POST       | `/tracking/weights`                             | consent | Weight history for the chart, one entry per day        |
| PATCH/DELETE   | `/tracking/weights/{id}`                        | consent | Changes or deletes a weight entry                      |
| GET            | `/tracking/weights/weeks`                       | consent | Calendar weeks with average and trend                  |
| GET            | `/tracking/weights/weeks/{iso_year}/{iso_week}` | consent | One calendar week                                      |

### Stats

| Method | Path     | Access | Purpose                                                           |
| ------ | -------- | ------ | ----------------------------------------------------------------- |
| GET    | `/stats` | public | `{ users, recipes, foods, entries }`; cached for up to 10 minutes |

Paginated lists use `?page=1` with 20 results per page and answer
`{ count, next, previous, results }`.

---

## Tests

The tests use Django's test runner and the `APITestCase` of Django REST
Framework. Run them with the stack running (`docker compose up`), because the
tests need the database container:

```bash
docker compose exec api python manage.py test
```

Django creates a separate test database for the run and deletes it afterwards,
so your data is not touched. The tests use an in-memory cache instead of Redis,
run the background jobs directly instead of through the worker and store images
in a temporary folder.

To run only a part, pass a module or a single test:

```bash
# One app
docker compose exec api python manage.py test apps.accounts

# One file
docker compose exec api python manage.py test apps.tracking.tests.test_weights

# One test
docker compose exec api python manage.py test apps.accounts.tests.test_auth.CookieAuthTests.test_writes_need_the_csrf_header
```

| File                                       | Covers                                                                                                          |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `apps/accounts/tests/test_auth.py`         | CSRF header, registration, login, rate limit, refresh rotation, logout, verification, password change and reset |
| `apps/accounts/tests/test_email_change.py` | E-mail change: link and notice, change only after the click, taken addresses, expired and outdated links        |
| `apps/accounts/tests/test_onboarding.py`   | Onboarding steps and their order, unique usernames, consent history, deletion of tracking data on revocation    |
| `apps/accounts/tests/test_account.py`      | Account deletion with grace period and daily job, data export with and without consent                          |
| `apps/accounts/tests/test_body.py`         | Body data: single fields, limits, minimum age, consent, deletion with the account                               |
| `apps/recipes/tests/test_recipes.py`       | Creating, filtering and editing recipes, author check, images and their metadata, saved recipes                 |
| `apps/recipes/tests/test_moderation.py`    | Staff-only access, approving and rejecting new recipes and revisions, staff notification                        |
| `apps/foods/tests/test_foods.py`           | Food search by text and barcode, import filters, `--scan-years` and `--limit`                                   |
| `apps/tracking/tests/test_nutrition.py`    | Entries computed from amount and unit, future dates, meals with notes, daily summary and targets                |
| `apps/tracking/tests/test_weights.py`      | One entry per day, ranges for the chart, weekly averages, paging and week detail                                |
| `apps/stats/tests/test_stats.py`           | Public numbers count only approved recipes and active users; an invalid cookie does not block them              |

---

## Troubleshooting

**`django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment
variable`** — the `.env` file is missing or has no `SECRET_KEY`. See
[Quick start](#quick-start). The same message with `REDIS_URL` means that line is
missing.

**The container stops right after the start** — run `docker compose logs api`.
Compare the `.env` with `.env.template` if a variable is missing. After changing
`POSTGRES_USER` or `POSTGRES_PASSWORD`, the old database volume still holds the
old values; reset it with `docker compose down -v` (this deletes all data).

**`relation "..." does not exist`** — the migrations have not run. Run
`docker compose exec api python manage.py migrate` and check the logs for the
reason they failed at start.

**`Bad Request (400)` on every request, or `DisallowedHost` in the logs** — the
hostname is not in `ALLOWED_HOSTS`. Add it, for example
`ALLOWED_HOSTS=localhost,127.0.0.1`, and restart the containers.

**Every request is redirected to `https://`** — `SECURE_SSL_REDIRECT` is missing
in `.env`, so the production default `True` applies. Copy the HTTPS block from
`.env.template`.

**`403 csrf_failed`** — the header `X-CSRFToken` is missing or does not match
the `csrftoken` cookie. Call `GET /auth/csrf` first and send the cookie and
the header together.

**`401 not_authenticated` on an endpoint that should work** — log in first;
without the cookies every protected endpoint answers `401`. The access token only
lives 15 minutes, so call `POST /auth/refresh` or log in again.

**The login works but the cookies are not sent afterwards** — with
`AUTH_COOKIE_SECURE=True` browsers only send the cookies over HTTPS. Set
`AUTH_COOKIE_SECURE=False` for local development and restart the containers.

**The frontend loads but every request fails** — the origin the frontend is
served from is not in `CORS_ALLOWED_ORIGINS` or `CSRF_TRUSTED_ORIGINS`. The value
has to match protocol, host and port exactly. The requests also have to send
credentials (`credentials: "include"` with `fetch`).

**`403 consent_required` on `/tracking/...`** — the user has not given the
privacy consent. Call `PUT /privacy/consent` with `accepted: true`.

**The food search returns nothing** — no products have been imported yet. See
[Food data](#food-data).

**No e-mails arrive** — with `EMAIL_URL=consolemail://` the e-mails are only
printed in `docker compose logs worker`. In that log, `=3D` stands for `=` and a
`=` at the end of a line joins it with the next line, so copy the link carefully.
With a real mail server, check that the `worker` container has `EMAIL_URL` and
that special characters in the password are URL-encoded. `sendtestemail` (see
[Useful commands](#useful-commands)) tests the connection without the worker.

**Scheduled jobs do not run** — the `beat` container has to run next to the
`worker`. Check `docker compose ps` and `docker compose logs beat`.

**`Bind for 0.0.0.0:8000 failed: port is already allocated`** — another program
uses the port. Stop it or change the left side of the port mapping in
`docker-compose.yml`, for example `"8001:8000"`. The same applies to `5432` and
`6379`.
