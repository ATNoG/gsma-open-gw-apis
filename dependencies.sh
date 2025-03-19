#!/bin/bash

set -e

VENV_DIR="fastapi-env"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    echo "Ambiente virtual '$VENV_DIR' criado."
fi

source $VENV_DIR/bin/activate

pip3 install --upgrade pip

pip3 install fastapi uvicorn

echo "Dependências instaladas com sucesso!"

exec bash
