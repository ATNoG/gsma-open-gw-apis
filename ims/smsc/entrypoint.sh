#!/bin/bash

set -eux -o pipefail

cat <<EOF > /client.password
[client]
password="$DATABASE_PASSWORD"
EOF

mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /usr/local/src/kamailio/utils/kamctl/mysql/standard-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /etc/kamailio_smsc/smsc-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /usr/local/src/kamailio/utils/kamctl/mysql/dialplan-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /usr/local/src/kamailio/utils/kamctl/mysql/presence-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /usr/local/src/kamailio/utils/kamctl/mysql/usrloc-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" smsc < /usr/local/src/kamailio/utils/kamctl/mysql/domain-create.sql || true

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_smsc/smsc.cfg
sed -i 's|ADVERTISE_ADDR|'$ADVERTISE_ADDR'|g' /etc/kamailio_smsc/smsc.cfg
sed -i 's|DATABASE_ADDR|'$DATABASE_ADDR'|g' /etc/kamailio_smsc/smsc.cfg
sed -i 's|DATABASE_USER|'$DATABASE_USER'|g' /etc/kamailio_smsc/smsc.cfg
sed -i 's|DATABASE_PASSWORD|'$DATABASE_PASSWORD'|g' /etc/kamailio_smsc/smsc.cfg

exec kamailio -f /etc/kamailio_smsc/kamailio_smsc.cfg -DD -E -e
