# Nibble Frontend

Web app for Nibble, a service for tracking nutrition and sharing recipes. Users
log the food they eat, compare it with their daily targets, record their weight
and publish recipes. The app is a Vue 3 single-page application that talks to
the Nibble API over HTTP.

- **Framework:** Vue 3 with TypeScript, Vue Router and Pinia
- **Styling:** Tailwind CSS 4 with own design tokens in `src/styles/`
- **Components:** Reka UI (accessible dialogs, menus, selects)
- **Forms:** vee-validate with Zod schemas
- **Charts:** Unovis
- **Barcode scanner:** Barcode Detector API, with zxing-wasm where the browser lacks it
- **Runtime:** Node 22 for development, nginx in production

---

## Table of contents

- [Quick start](#quick-start)
- [Connecting to the backend](#connecting-to-the-backend)
- [Scripts](#scripts)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Project layout](#project-layout)
- [Routes](#routes)
- [Authentication in the app](#authentication-in-the-app)
- [Code quality](#code-quality)
- [Troubleshooting](#troubleshooting)

---

## Quick start

**Requirements:** Node `^22.18.0` or `>=24.12.0` and the Nibble backend running
on `http://localhost:8000` (see the [backend README](../backend/README.md)).

Install the dependencies in the `frontend/` folder:

```bash
npm install
```

Create `.env.local` from the template:

**Windows (PowerShell)**

```powershell
Copy-Item .env.template .env.local
```

**macOS / Linux**

```bash
cp .env.template .env.local
```

Start the dev server:

```bash
npm run dev
```

The app is now available at `http://localhost:5173`.

Every command of this README is run from the project root, the folder that
contains `package.json` (`frontend/`).

---

## Connecting to the backend

The app calls the API directly at the URL in `VITE_API_BASE_URL`. Login tokens
are `HttpOnly` cookies set by the API, so app and API have to run on the same
site:

- Locally both run on `localhost`, only the ports differ (`5173` and `8000`).
- In production both run on subdomains of one domain, for example `example.com`
  and `api.example.com`.

Use `localhost` everywhere, not `127.0.0.1`. The browser treats them as two
different sites and then does not send the login cookies.

The backend `.env` has to allow the app. For local development:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173
AUTH_COOKIE_SECURE=False
```

`AUTH_COOKIE_DOMAIN` stays unset locally.

---

## Scripts

| Command              | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `npm run dev`        | Dev server with hot reload on port `5173`    |
| `npm run build`      | Type check and production build into `dist/` |
| `npm run build-only` | Production build without type check          |
| `npm run preview`    | Serves the content of `dist/` locally        |
| `npm run type-check` | Type check with `vue-tsc`                    |
| `npm run lint`       | oxlint, then ESLint; both fix what they can  |
| `npm run format`     | Prettier on `src/`                           |

---

## Configuration

| Variable            | Example                 | Purpose                                     |
| ------------------- | ----------------------- | ------------------------------------------- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL of the API, without trailing slash |

Locally the value comes from `.env.local`, which git ignores. Vite writes the
value into the JavaScript at build time, so changing it later needs a new build.

---

## Deployment

The `Dockerfile` builds the app with Node and serves the result with nginx on
port `80`. The API URL is passed as build argument:

```bash
docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t nibble-frontend .
docker run -p 8080:80 nibble-frontend
```

The build stops if `VITE_API_BASE_URL` is empty. On a hosting platform such as
Coolify, set the variable as **build** variable; a runtime variable arrives too
late.

`nginx.conf` does three things:

| Rule                     | Effect                                                                                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Fallback to `index.html` | Every path without a file, e.g. `/rezepte`, loads the app, which then shows the page. Without it a reload on any page except `/` answers `404`. |
| `/assets/`               | Cached for one year. Vite puts a content hash into these file names, so a new build gets new names.                                             |
| `index.html`             | Never cached, so a new deploy is picked up on the next page load.                                                                               |

The backend needs these values when the app runs on `https://example.com`:

```env
AUTH_COOKIE_DOMAIN=.example.com
CORS_ALLOWED_ORIGINS=https://example.com
CSRF_TRUSTED_ORIGINS=https://example.com
FRONTEND_URL=https://example.com
```

`AUTH_COOKIE_DOMAIN` lets the app read the CSRF cookie of the API. Without it
every request that changes data answers `403`.

---

## Project layout

```
src/
  features/    One folder per area of the app
  layouts/     App shell: header, sidebar, bottom navigation, mobile menu
  shared/      Code used by several features
    api/         API client (cookies, CSRF header, token refresh, errors)
    forms/       Form fields bound to vee-validate
    ui/          Base components (button, dialog, drawer, card ...)
    composables/ Breakpoints, page title, toasts, multi-step forms
    utils/       Dates, numbers, slugs, downloads
  styles/      Design tokens, base styles and one file per component
  assets/      Fonts
  router/      Router setup and guards
```

Every feature folder follows the same pattern:

| File or folder        | Content                                 |
| --------------------- | --------------------------------------- |
| `<name>.api.ts`       | Requests to the API                     |
| `<name>.routes.ts`    | Routes of the feature                   |
| `<name>.schema.ts`    | Zod schemas of the forms                |
| `<name>.types.ts`     | Types of the API data                   |
| `<name>.store.ts`     | Pinia store, only where state is shared |
| `<name>.utils.ts`     | Helpers without Vue                     |
| `<name>.constants.ts` | Labels and fixed values                 |
| `components/`         | Components used only by this feature    |
| `composables/`        | Composables used only by this feature   |
| `views/`              | Pages                                   |

Features: `account`, `admin`, `auth`, `calorie-calculator`, `dashboard`,
`landing`, `legal`, `meals`, `onboarding`, `recipes`, `tracking`.

Path aliases: `@assets`, `@features`, `@layouts`, `@shared` and `@styles` point
to the folders of the same name in `src/`.

---

## Routes

Paths are German, as is the whole interface.

| Path                                            | Page                     | Access          |
| ----------------------------------------------- | ------------------------ | --------------- |
| `/`                                             | Landing page             | public          |
| `/anmeldung`, `/registrieren`                   | Login, registration      | public          |
| `/passwort-vergessen`                           | Request a password reset | public          |
| `/email-bestaetigen`, `/passwort-zuruecksetzen` | Links from e-mails       | public          |
| `/rezepte`, `/rezepte/:id-:slug`                | Recipe list and detail   | public          |
| `/kalorienrechner`                              | Calorie calculator       | public          |
| `/impressum`, `/datenschutz`, `/agb`            | Legal pages              | public          |
| `/einrichten`                                   | Onboarding               | login           |
| `/uebersicht`                                   | Dashboard                | login           |
| `/rezepte/neu`, `/rezepte/:id-:slug/bearbeiten` | Create and edit recipes  | login           |
| `/konto/...`                                    | Settings                 | login           |
| `/tagebuch/ernaehrung`, `/tagebuch/gewicht`     | Food and weight diary    | login + consent |
| `/mahlzeiten/...`                               | Saved meals              | login + consent |
| `/verwaltung/...`                               | Recipe moderation        | staff           |

The router guard sends guests to `/anmeldung` and back to the requested page
after the login (`?weiter=`). Pages that need the privacy consent redirect to
the dashboard without it; staff pages do the same for other users.

The e-mails of the backend link to `/verify-email` and `/reset-password`. Both
are aliases of the German paths.

---

## Authentication in the app

`src/shared/api/client.ts` handles everything around the login, so feature code
only calls `apiRequest()`:

1. On start the app calls `GET /auth/me` and mounts once it knows whether
   someone is signed in.
2. Every `POST`, `PUT`, `PATCH` and `DELETE` sends the `X-CSRFToken` header. The
   token comes from the `csrftoken` cookie; if it is missing, the client calls
   `GET /auth/csrf` first.
3. On `401` the client calls `POST /auth/refresh` once and repeats the request.
   Parallel requests share one refresh.
4. If the refresh fails, a signed-in user sees a notice and the login page.

Errors arrive as `ApiError` with `status`, `code` and `fieldErrors`, so forms can
show the messages of the API next to the matching field.

---

## Code quality

| Tool         | Config             | Purpose                                                                 |
| ------------ | ------------------ | ----------------------------------------------------------------------- |
| oxlint       | `.oxlintrc.json`   | Fast checks for errors, import cycles and duplicates                    |
| ESLint       | `eslint.config.ts` | Vue and TypeScript rules, accessibility, import order, Tailwind classes |
| Prettier     | `.prettierrc.json` | Formatting: no semicolons, single quotes, 100 characters                |
| EditorConfig | `.editorconfig`    | Tabs, LF line endings, final newline                                    |
| vue-tsc      | `tsconfig.*.json`  | Type check of `.ts` and `.vue` files                                    |

`npm run lint` fixes what it can, including outdated Tailwind classes such as
`break-words` (now `wrap-break-word`). VS Code formats and fixes on save with
the extensions listed in `.vscode/extensions.json`.

---

## Troubleshooting

**Every request fails, the console shows a CORS error** — the origin of the app
is not in `CORS_ALLOWED_ORIGINS` of the backend. The value has to match
protocol, host and port exactly, e.g. `http://localhost:5173`.

**The login works, but the next page shows the login again** — the browser did
not send the cookies. Check that app and API both use `localhost` (not
`127.0.0.1`) and that the backend has `AUTH_COOKIE_SECURE=False` locally.

**`403` on every form, the response says `csrf_failed`** — the app cannot read
the CSRF cookie. In production set `AUTH_COOKIE_DOMAIN=.example.com` in the
backend and add the app's origin to `CSRF_TRUSTED_ORIGINS`.

**Requests go to `undefined/auth/me`** — `VITE_API_BASE_URL` is missing. Create
`.env.local` (see [Quick start](#quick-start)) and restart `npm run dev`. In
production the variable has to be a build variable.

**A reload on a page other than `/` answers `404`** — the server does not fall
back to `index.html`. With the `Dockerfile` this is handled by `nginx.conf`;
other hosts need the same rule.

**The barcode scanner does not open the camera** — browsers allow the camera
only over HTTPS or on `localhost`. Opening the dev server through the network
IP of your machine (e.g. on a phone) does not work without HTTPS.

**`Port 5173 is in use`** — Vite then picks the next free port. Add that origin
to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` of the backend, or stop the
other process.
