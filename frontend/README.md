# Nibble Frontend

Web app for Nibble: nutrition tracking, weight history and recipes. Vue 3 with
TypeScript, built with Vite and served by nginx in production. It talks to the
Nibble API over HTTP.

- **Framework:** Vue 3, Vue Router, Pinia
- **Styling:** Tailwind CSS 4 with own design tokens (`src/styles/`)
- **Components:** Reka UI, forms with vee-validate and Zod
- **Runtime:** Node 22 for development, nginx in production

---

## Local development

**Requirements:** Node `^22.18.0` or `>=24.12.0` and the backend running on
`http://localhost:8000` (see the backend README).

```bash
npm install
cp .env.template .env.local
npm run dev
```

The app is now available at `http://localhost:5173`.

`.env.local` holds the URL of the API:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Use `localhost` in both places, not `127.0.0.1`. The browser treats
`localhost` and `127.0.0.1` as different sites and then does not send the login
cookies.

The backend `.env` has to allow the app:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173
AUTH_COOKIE_SECURE=False
```

---

## Scripts

| Command              | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `npm run dev`        | Dev server with hot reload on port `5173`    |
| `npm run build`      | Type check and production build into `dist/` |
| `npm run build-only` | Production build without type check          |
| `npm run preview`    | Serves the content of `dist/` locally        |
| `npm run type-check` | Type check with `vue-tsc`                    |
| `npm run lint`       | oxlint and ESLint, both fix what they can    |
| `npm run format`     | Prettier on `src/`                           |

---

## Configuration

| Variable            | Example                   | Purpose                                     |
| ------------------- | ------------------------- | ------------------------------------------- |
| `VITE_API_BASE_URL` | `https://api.example.com` | Base URL of the API, without trailing slash |

Vite writes the value into the JavaScript at build time. Changing it later
needs a new build.

---

## Deployment

The `Dockerfile` builds the app with Node and serves `dist/` with nginx on port
`80`. Pass the API URL as build argument:

```bash
docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t nibble-frontend .
```

The build stops if `VITE_API_BASE_URL` is empty.

`nginx.conf` answers every unknown path with `index.html`, so routes like
`/rezepte` work on reload. Files under `/assets/` carry a content hash in
their name and are cached for one year; `index.html` is never cached, so a new
deploy is picked up on the next page load.

Frontend and API have to run on subdomains of the same domain, for example
`example.com` and `api.example.com`. The backend then needs:

```env
AUTH_COOKIE_DOMAIN=.example.com
CORS_ALLOWED_ORIGINS=https://example.com
CSRF_TRUSTED_ORIGINS=https://example.com
FRONTEND_URL=https://example.com
```

---

## Project layout

```
src/
  features/    One folder per area: api, routes, schema, types, components, views
  layouts/     App shell: header, sidebar, bottom navigation, mobile menu
  shared/      API client, form fields, UI components, composables, utils
  styles/      Design tokens, base styles and component styles
  assets/      Fonts
  router/      Router setup and navigation guards
```
