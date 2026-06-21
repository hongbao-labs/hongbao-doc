# Build stage — generate Starlight content from CN/EN, then build the static site.
# NOTE: build context is the REPO ROOT (../hongbao-doc), not web/, so that
# CN/ and EN/ are available to web/scripts/migrate.py.
FROM node:22-alpine AS build

# migrate.py is stdlib-only Python; alpine node image has no python by default
RUN apk add --no-cache python3

WORKDIR /app/web

# Install deps first for layer caching
COPY web/package.json web/package-lock.json* ./
RUN npm ci

# Bring in the doc sources + web app, preserving the repo layout migrate.py
# expects (ROOT = parents[2] of web/scripts/migrate.py == /app).
COPY CN/ /app/CN/
COPY EN/ /app/EN/
COPY web/ /app/web/

# `prebuild` (package.json) runs migrate.py to regenerate web/src/content/docs
# from CN/EN; then astro build emits dist/.
RUN npm run build

# Production stage
FROM nginx:1.27-alpine AS production

COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/web/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
