#!/bin/bash

set -eux -o pipefail

cat <<EOF > /client.password
[client]
password="$DATABASE_PASSWORD"
EOF

mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" icscf < /usr/local/src/kamailio/misc/examples/ims/icscf/icscf.sql || true

cat <<EOF | mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" icscf 
INSERT IGNORE INTO nds_trusted_domains (id, trusted_domain)
VALUES (1, '$IMS_DOMAIN');

INSERT IGNORE INTO s_cscf (id, name, s_cscf_uri)
VALUES (1, 'S-CSCF by DNS', 'sip:scscf.$IMS_DOMAIN:6060')
RETURNING id;

INSERT IGNORE INTO s_cscf_capabilities (id_s_cscf, capability)
VALUES (1, 0), (1, 1);
EOF

if [[ "${DEBUG:-no}" == "yes" ]]; then
	sed -i 's|##!define WITH_DEBUG\b|#!define WITH_DEBUG|g' /etc/kamailio_icscf/icscf.cfg
fi

: "${SUBSCRIPTION_EXPIRES_ENV:=3600}"

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_icscf/icscf.xml
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_icscf/icscf.xml

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_icscf/icscf.cfg
sed -i 's|ADVERTISE_ADDR|'$ADVERTISE_ADDR'|g' /etc/kamailio_icscf/icscf.cfg
sed -i 's|DATABASE_ADDR|'$DATABASE_ADDR'|g' /etc/kamailio_icscf/icscf.cfg
sed -i 's|DATABASE_USER|'$DATABASE_USER'|g' /etc/kamailio_icscf/icscf.cfg
sed -i 's|DATABASE_PASSWORD|'$DATABASE_PASSWORD'|g' /etc/kamailio_icscf/icscf.cfg
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_icscf/icscf.cfg

exec kamailio -f /etc/kamailio_icscf/kamailio_icscf.cfg -DD -E -e
