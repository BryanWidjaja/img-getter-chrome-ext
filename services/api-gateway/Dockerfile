FROM golang:1.25-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY protos/ protos/

WORKDIR /app/services/api-gateway
COPY services/api-gateway/ .
RUN CGO_ENABLED=0 go build -o /api-gateway ./cmd

FROM alpine:latest
WORKDIR /root/

COPY --from=builder /api-gateway .

EXPOSE 8000

CMD ["./api-gateway"]