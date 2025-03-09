ARG ALPINE_VERSION=3.21
ARG GO_VERSION=1.24
ARG COREDNS_VERSION=1.12.0

FROM golang:${GO_VERSION}-alpine${ALPINE_VERSION} AS builder
ARG COREDNS_VERSION

WORKDIR /src
RUN apk add --no-cache git make && \
		git clone https://github.com/coredns/coredns.git . && \
		git checkout v${COREDNS_VERSION}

COPY plugin.cfg plugin.cfg

RUN go get github.com/tmeckel/coredns-finalizer && \
	go generate && \
	go get && \
	make

FROM alpine:${ALPINE_VERSION} AS runtime

RUN apk add --no-cache ca-certificates curl jq bash && \
    update-ca-certificates

COPY --from=builder /src/coredns /coredns

COPY . /opt/dns

WORKDIR /opt/dns
EXPOSE 53 53/udp
ENTRYPOINT ["/opt/dns/entrypoint.sh"]
