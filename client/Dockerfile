# ----- build -----
FROM node:20-alpine AS builder
WORKDIR /app
RUN apk add --no-cache libc6-compat

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
COPY .env .env
RUN yarn build

# ----- runtime -----
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
RUN apk add --no-cache libc6-compat

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production --ignore-scripts
COPY --from=builder /app/build ./build

EXPOSE 3000
CMD ["node","build"]
