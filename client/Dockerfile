# ---------- build stage ----------
FROM node:20-alpine AS build
WORKDIR /app

# Install deps (no node_modules from host)
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Build SvelteKit
COPY . .
COPY .env .env

RUN yarn build

# ---------- runtime stage ----------
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production


# Only prod deps
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production

# Copy the built server
COPY --from=build /app/build ./build

EXPOSE 3000
CMD ["node", "build/index.js"]
