#!/bin/bash

set -eux -o pipefail

# KUBE_TOKEN="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
# KUBE_NAMESPACE="$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)"
#
# KUBE_API_ROOT="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api"
# SERVICE_ENDPOINT="$KUBE_API_ROOT/v1/namespaces/$KUBE_NAMESPACE/services/$RELEASE_NAME-pcscf"
#
# ADVERTISE_SELECTOR='.status.loadBalancer.ingress[0] | if .hostname != null and .hostname != "" then .hostname else .ip end'
#
# while :; do
# 	ADVERTISE_ADDR="$(curl -sSk --fail -H "Authorization: Bearer $KUBE_TOKEN" \
# 		"$SERVICE_ENDPOINT" | jq -r "$ADVERTISE_SELECTOR")"
#
# 	if [ "$ADVERTISE_ADDR" != "null" ]; then
# 		break
# 	fi
#
# 	sleep 1
# done

IPSEC_ADVERTISE_ADDR="$ADVERTISE_ADDR"

cat <<EOF > /client.password
[client]
password="$DATABASE_PASSWORD"
EOF

mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" pcscf < /usr/local/src/kamailio/utils/kamctl/mysql/standard-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" pcscf < /usr/local/src/kamailio/utils/kamctl/mysql/presence-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" pcscf < /usr/local/src/kamailio/utils/kamctl/mysql/ims_usrloc_pcscf-create.sql || true
mysql --defaults-extra-file=/client.password -u "$DATABASE_USER" -h "$DATABASE_ADDR" pcscf < /usr/local/src/kamailio/utils/kamctl/mysql/ims_dialog-create.sql || true

: "${DEPLOY_MODE:=standalone}"

if [[ "$DEPLOY_MODE" == "5G" ]]; then
	sed -i 's|##!define WITH_N5\b|#!define WITH_N5|g' /etc/kamailio_pcscf/pcscf.cfg
elif [[ "$DEPLOY_MODE" == "4G" ]]; then
    sed -i 's|##!define WITH_RX\b|#!define WITH_RX|g' /etc/kamailio_pcscf/pcscf.cfg
fi

if [[ "${DEBUG:-no}" == "yes" ]]; then
	sed -i 's|##!define WITH_DEBUG\b|#!define WITH_DEBUG|g' /etc/kamailio_pcscf/pcscf.cfg
fi

: "${SUBSCRIPTION_EXPIRES_ENV:=3600}"

sed -i 's|IPSEC_ADVERTISE_ADDR|'$IPSEC_ADVERTISE_ADDR'|g' /etc/kamailio_pcscf/pcscf.cfg

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|ADVERTISE_ADDR|'$ADVERTISE_ADDR'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|ADVERTISE_PORT|'$ADVERTISE_PORT'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|DATABASE_ADDR|'$DATABASE_ADDR'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|DATABASE_USER|'$DATABASE_USER'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|DATABASE_PASSWORD|'$DATABASE_PASSWORD'|g' /etc/kamailio_pcscf/pcscf.cfg
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_pcscf/pcscf.cfg

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /etc/kamailio_pcscf/pcscf.xml
sed -i 's|SUBSCRIPTION_EXPIRES_ENV|'$SUBSCRIPTION_EXPIRES_ENV'|g' /etc/kamailio_pcscf/pcscf.xml

sed -i 's|RTPENGINE_IP|'$RELEASE_NAME-rtpengine'|g' /etc/kamailio_pcscf/kamailio_pcscf.cfg

exec kamailio -f /etc/kamailio_pcscf/kamailio_pcscf.cfg -DD -E -e
