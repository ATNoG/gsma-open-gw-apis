#!/bin/bash
set -eux -o pipefail

KUBE_TOKEN="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
KUBE_NAMESPACE="$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)"

KUBE_API_ROOT="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api"
SERVICE_ENDPOINT="$KUBE_API_ROOT/v1/namespaces/$KUBE_NAMESPACE/services/$RELEASE_NAME-dns"

DNS_IP="$(curl -sSk --fail -H "Authorization: Bearer $KUBE_TOKEN" \
	"$SERVICE_ENDPOINT" | jq -r ".spec.clusterIP")"

# Patch DNS resolution
RESOLV_BAK="$(mktemp)"
cat /etc/resolv.conf > "$RESOLV_BAK"
sed 's/\(nameserver \)\(.*\)/\1'$DNS_IP'/' "$RESOLV_BAK" > /etc/resolv.conf
