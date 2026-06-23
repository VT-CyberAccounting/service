FROM node:22-alpine AS ui-builder

WORKDIR /web
COPY package*.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM nginx:stable-alpine

COPY --from=ui-builder /web/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80