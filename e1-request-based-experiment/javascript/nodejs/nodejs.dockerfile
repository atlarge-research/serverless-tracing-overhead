FROM node:18-slim

ARG TFB_TEST_NAME

COPY ./ ./

RUN npm install

ENV NODE_ENV production

EXPOSE 8080

CMD ["node", "app.js"]
