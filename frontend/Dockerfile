# build env
FROM node:14.21.3 as build
WORKDIR /app
COPY package*.json ./

ENV API_URL https://python.nomoredomainsrocks.ru

RUN npm ci

COPY . .
RUN npm run build
CMD cp -r /app/build/. /static/
