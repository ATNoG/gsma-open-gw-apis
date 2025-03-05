FROM alpine:3.21

RUN apk add --no-cache rtpengine bash && mkdir -p /opt/rtpengine

COPY entrypoint.sh /opt/rtpengine/entrypoint.sh

ENTRYPOINT ["/opt/rtpengine/entrypoint.sh"]
