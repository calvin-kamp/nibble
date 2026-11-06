FROM node:22-alpine AS build

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
# Empty in production, preview_ on the preview environment (same as AUTH_COOKIE_PREFIX)
ARG VITE_COOKIE_PREFIX=
ENV VITE_COOKIE_PREFIX=$VITE_COOKIE_PREFIX

# Without the API URL the app would build but every request would fail
RUN test -n "$VITE_API_BASE_URL"

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build-only

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
