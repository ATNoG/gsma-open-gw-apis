#!/bin/bash

set -eux -o pipefail

cat <<EOF > /client.password
[client]
password="$DATABASE_PASSWORD"
EOF

mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" scscf < /usr/local/src/kamailio/utils/kamctl/mysql/standard-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" scscf < /usr/local/src/kamailio/utils/kamctl/mysql/presence-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" scscf < /usr/local/src/kamailio/utils/kamctl/mysql/ims_usrloc_scscf-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" scscf < /usr/local/src/kamailio/utils/kamctl/mysql/ims_dialog-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" scscf < /usr/local/src/kamailio/utils/kamctl/mysql/ims_charging-create.sql || true

if [[ "${DEBUG:-no}" == "yes" ]]; then
	sed -i 's|##!define WITH_DEBUG\b|#!define WITH_DEBUG|g' /etc/kamailio_scscf/scscf.cfg
fi

export IMS_SLASH_DOMAIN=`echo $IMS_DOMAIN | sed 's/\./\\\./g'`

: "${SUBSCRIPTION_EXPIRES_ENV:=3600}"

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_scscf/scscf.xml
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_scscf/scscf.xml

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|ADVERTISE_ADDR|'$ADVERTISE_ADDR'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|IMS_SLASH_DOMAIN|'$IMS_SLASH_DOMAIN'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|DATABASE_ADDR|'$DATABASE_ADDR'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|DATABASE_USER|'$DATABASE_USER'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|DATABASE_PASSWORD|'$DATABASE_PASSWORD'|g' /etc/kamailio_scscf/scscf.cfg
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_scscf/scscf.cfg


exec kamailio -f /etc/kamailio_scscf/kamailio_scscf.cfg -DD -E -e
