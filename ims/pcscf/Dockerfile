FROM gsma/ims/kamailio:latest

RUN apt install -y curl jq

COPY . /etc/kamailio_pcscf
CMD ["/etc/kamailio_pcscf/entrypoint.sh"]
