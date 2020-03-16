.PHONY: deps clean format lint build

all: clean format lint build

lint:
	golangci-lint run ./...

format:
	go fmt ./...

build:
	mkdir -p ./bin/
	go build -o ./bin/photobomb ./cli/

clean:
	rm -rf ./bin/