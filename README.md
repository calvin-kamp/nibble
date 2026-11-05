<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="frontend/public/brand/wordmark-dark.svg">
    <img src="frontend/public/brand/wordmark-light.svg" alt="nibble" height="64">
  </picture>
</p>

<p align="center">
  Nutrition tracking and recipe sharing, built as a full-stack web app.<br>
  <a href="https://www.nibble-tracking.de"><strong>www.nibble-tracking.de</strong></a>
</p>

---

nibble is a web app for people who want to keep an eye on what they eat. Users log
their meals, compare them with their daily calorie and macro targets, track their
weight over time and share recipes with the community. The app is in German and
is aimed at users in Germany, Austria and Switzerland.

This repository is a **read-only mirror** of the two project repositories. It is
kept up to date automatically by GitHub Actions whenever `main` changes in either
of them.

| Folder                    | Contents                                   | Details                                    |
| ------------------------- | ------------------------------------------ | ------------------------------------------ |
| [`backend/`](backend/)    | REST API (Django, PostgreSQL, Celery)      | [Backend README](backend/README.md)        |
| [`frontend/`](frontend/)  | Single-page application (Vue 3, TypeScript) | [Frontend README](frontend/README.md)      |

## Features

- **Food diary** – log food by searching or by scanning the barcode with the
  camera, with portions in grams, millilitres or servings
- **Daily targets** – calories and macros from a built-in calculator (BMR/TDEE)
  or entered by hand, compared with what was eaten each day
- **Weight tracking** – daily entries, weekly averages and trend charts
- **Own meals** – combine products into reusable meals and log them in one step
- **Recipes** – browse, filter and save recipes, submit your own with a photo;
  a moderator reviews every recipe before it is published
- **Calorie calculator** – usable without an account
- **Onboarding** – a guided setup for body data, consent and targets
- **Privacy by design** – explicit consent for health data, data export, consent
  withdrawal that deletes all health data, account deletion with a grace period,
  image metadata stripped on upload
- **Accessibility** – keyboard navigation, screen reader labels and a layout that
  works from 320 px up

## Tech stack

**Frontend**

- Vue 3, TypeScript, Vue Router, Pinia
- Tailwind CSS 4 with own design tokens, Reka UI for accessible components
- vee-validate with Zod, Unovis for charts
- Barcode Detector API with a zxing-wasm fallback
- Vite, ESLint, oxlint, Prettier

**Backend**

- Python 3.13, Django 6 and Django REST Framework
- PostgreSQL 17, Redis
- Celery workers and beat for e-mails, account deletion and the weekly food import
- JWT authentication in `HttpOnly` cookies with CSRF protection
- OpenAPI specification, test suite with Django's test runner

**Infrastructure**

- Docker and Docker Compose for local development and production
- Deployed with Coolify; the frontend is served by nginx, the API by gunicorn
- GitHub Actions to mirror both repositories into this one

## Architecture

```
┌──────────────┐   HTTPS / JSON    ┌────────────────┐      ┌──────────────┐
│   Frontend   │ ────────────────► │   Django API   │ ───► │  PostgreSQL  │
│ Vue 3 (SPA)  │ ◄──────────────── │   (gunicorn)   │      └──────────────┘
└──────────────┘  cookies (JWT)    └───────┬────────┘
                                           │ tasks
                                           ▼
                                   ┌────────────────┐      ┌──────────────┐
                                   │ Celery worker  │ ───► │    Redis     │
                                   │   and beat     │      └──────────────┘
                                   └───────┬────────┘
                                           │ weekly import
                                           ▼
                                   ┌────────────────┐
                                   │ Open Food Facts│
                                   │   CSV export   │
                                   └────────────────┘
```

Food data comes from [Open Food Facts](https://world.openfoodfacts.org). Instead
of calling their API on every search, the backend streams the full CSV export once
a week and keeps the products sold in Germany, Austria and Switzerland that have a
name, complete nutrition values and recent scans. Search and barcode lookups then
run against the own database.

## Running it locally

Both parts run on their own; the backend needs only Docker, the frontend needs
Node 22 or newer.

```bash
# Backend – API on http://localhost:8000
cd backend
cp .env.template .env        # fill in the secret keys
docker compose up --build
```

```bash
# Frontend – app on http://localhost:5173
cd frontend
cp .env.template .env.local
npm install
npm run dev
```

The READMEs in [`backend/`](backend/README.md) and [`frontend/`](frontend/README.md)
cover configuration, the food import, tests, deployment and troubleshooting in
detail.

## About this project

nibble was designed and built by **Calvin Kamp** as a portfolio project, from the
idea and the design to the API, the frontend and the deployment.

Food data © Open Food Facts contributors, available under the
[Open Database License](https://opendatacommons.org/licenses/odbl/1-0/).
