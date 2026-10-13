# syntax=docker/dockerfile:1
# Web app image, built from the repository root (pnpm workspace):
#   docker build -f web/Dockerfile .

# ---- Build stage: install the workspace and build the Angular app ----
FROM node:22-slim AS build

ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0
# pnpm version from the packageManager field of package.json
RUN corepack enable

WORKDIR /repo

# Dependencies first, in their own layer: code changes do not reinstall them
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/api-client/package.json packages/api-client/
COPY web/package.json web/
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile --filter "@immo-paris/web..."

COPY packages/api-client packages/api-client
COPY web web
RUN pnpm --filter @immo-paris/web build


# ---- Runtime stage: only the build output (the server bundle includes its dependencies) ----
FROM node:22-slim

ENV NODE_ENV=production
WORKDIR /app
COPY --from=build /repo/web/dist/web ./dist/web

# Unprivileged user provided by the Node.js image; files stay owned by root (read-only)
USER node
EXPOSE 4000

# Configuration comes from the environment: PORT, API_BASE_URL, NG_ALLOWED_HOSTS
CMD ["node", "dist/web/server/server.mjs"]
