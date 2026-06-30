FROM node:22-alpine AS base

WORKDIR /app
COPY package*.json ./
RUN npm install

FROM base AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
COPY . .
RUN npm run build

FROM alpine:3.20 AS prod
WORKDIR /app
COPY --from=build /app/dist /app/dist
CMD ["tail", "-f", "/dev/null"]
