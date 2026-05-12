FROM golang:1.23-alpine
ENV GOTOOLCHAIN=auto
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . .
RUN go mod tidy
RUN go build -o main cmd/main.go
EXPOSE 8080
CMD ["./main"]
