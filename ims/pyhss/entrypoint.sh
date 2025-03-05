#!/bin/bash

set -eux -o pipefail

sed -i 's|IMS_DOMAIN|'$IMS_DOMAIN'|g' ./config.yaml
sed -i 's|OP_MCC|'$MCC'|g' ./config.yaml
sed -i 's|OP_MNC|'$MNC'|g' ./config.yaml
sed -i 's|DATABASE_ADDR|'$DATABASE_ADDR'|g' ./config.yaml
sed -i 's|DATABASE_USER|'$DATABASE_USER'|g' ./config.yaml
sed -i 's|DATABASE_PASSWORD|'$DATABASE_PASSWORD'|g' ./config.yaml

redis-server --daemonize yes

cd services

python3 apiService.py --host=0.0.0.0 --port=8080 &
python3 diameterService.py &
python3 hssService.py &
wait
