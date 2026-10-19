# Shadow Corp Internal API — Node.js
FROM node:20-alpine

WORKDIR /app

COPY package.json .
RUN npm install --omit=dev

COPY server.js .

# NOT exposing any ports to host — internal network only
EXPOSE 3000

CMD ["node", "server.js"]
