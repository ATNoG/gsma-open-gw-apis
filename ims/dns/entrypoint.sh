#!/bin/bash

set -eux -o pipefail

KUBE_TOKEN="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
KUBE_NAMESPACE="$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)"

KUBE_API_ROOT="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api"
SERVICE_ENDPOINT="$KUBE_API_ROOT/v1/namespaces/$KUBE_NAMESPACE/services/$RELEASE_NAME-dns"

DNS_IP="$(curl -sSk --fail -H "Authorization: Bearer $KUBE_TOKEN" \
	"$SERVICE_ENDPOINT" | jq -r ".spec.clusterIP")"

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /opt/dns/ims_zone
sed -i 's|DNS_IP|'$DNS_IP'|g' /opt/dns/ims_zone
sed -i 's|RELEASE_NAMESPACE|'$KUBE_NAMESPACE'|g' /opt/dns/ims_zone
sed -i 's|RELEASE_NAME|'$RELEASE_NAME'|g' /opt/dns/ims_zone

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /opt/dns/e164.arpa
# TODO: Retrieve DNS IP from kubeapi
sed -i 's|DNS_IP|'$DNS_IP'|g' /opt/dns/e164.arpa

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' /opt/dns/Corefile

exec /coredns
