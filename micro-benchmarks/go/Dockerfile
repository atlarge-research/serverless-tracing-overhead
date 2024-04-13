FROM golang:1.21 AS builder

ARG USE_APM=false
ARG GO_FILE_NAME=server

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o $GO_FILE_NAME .

FROM alpine:latest

ARG GO_FILE_NAME=server
ENV GO_FILE_NAME=$GO_FILE_NAME

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/$GO_FILE_NAME .

EXPOSE 5100

RUN ls -la

CMD ./$GO_FILE_NAME