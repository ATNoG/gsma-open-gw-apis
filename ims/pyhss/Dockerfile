# BSD 2-Clause License

# Copyright (c) 2020, Supreeth Herle
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

FROM python:3.10.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk update && \
    apk add --no-cache \
        python3-dev \
        build-base \
        pkgconfig \
        libffi-dev \
        openssl-dev \
        git \
        gcc \
        g++ \
        musl-dev \
        linux-headers \
        libxml2-dev \
        libxslt-dev \
        py3-yaml && \
    apk add bash mariadb-dev lksctp-tools-dev redis && \
    pip install --upgrade pip setuptools wheel


# Get pyhss code and install
RUN git clone https://github.com/nickvsnetworking/pyhss /pyhss && \
    cd /pyhss && git checkout tags/1.0.2 && \
	sed -i 's|PyYAML==6.0|PyYAML==6.0.1|g' /pyhss/requirements.txt && \
	python3 -m venv /venv && \
	PATH=/venv/bin:$PATH pip install --no-cache-dir -r /pyhss/requirements.txt

FROM python:3.10.12-alpine AS runtime

COPY --from=builder /venv /venv
COPY --from=builder /pyhss /pyhss
ENV PATH=/venv/bin:$PATH

RUN apk add bash mariadb-dev mariadb-client lksctp-tools-dev redis

COPY . /pyhss

WORKDIR /pyhss

ENTRYPOINT ["/pyhss/entrypoint.sh"]
