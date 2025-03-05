#!/bin/bash

# Code adapted from: https://github.com/herlesupreeth/docker_open5gs/blob/c3c907f5554b37fbbecc7a170280a9ae05e3c4c3/ims_base/rtpengine_init.sh

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

set -eux -o pipefail

: "${DISABLE_KERNEL_FORWARDING:=no}"

if [ -z "${TABLE+x}" ]; then
	if [ "$DISABLE_KERNEL_FORWARDING" = "yes" ]; then
		TABLE="-1"
	else
		TABLE="0" # TODO: Allocate based on free tables
	fi
elif [ "$DISABLE_KERNEL_FORWARDING" = "yes" ]; then
	>&2 echo "DISABLE_KERNEL_FORWARDING and TABLE can't be set at the same time"
	exit 1
fi

# Populate options of the rtpengine cli command
[ -z "${INTERFACE+x}" ] && INTERFACE="$(awk 'END{print $1}' /etc/hosts)"

OPTIONS="--listen-ng=${LISTEN_NG_PORT:-2223} --port-min=${PORT_MIN:-30000} --port-max=${PORT_MAX:-40000} --table=$TABLE --tos=${TOS:-184} --foreground"

if [ -z "${ADVERTISE_ADDR+x}" ]; then
	OPTIONS="$OPTIONS --interface=$INTERFACE"
else
	OPTIONS="$OPTIONS --interface=$INTERFACE!$ADVERTISE_ADDR"
fi

if [ "${NO_FALLBACK:-no}" = "yes" ]; then
	if [ "$DISABLE_KERNEL_FORWARDING" = "yes" ]; then
		>&2 echo "DISABLE_KERNEL_FORWARDING and NO_FALLBACK can't be set at the same time"
		exit 1
	fi

	OPTIONS="$OPTIONS --no-fallback"
fi

exec rtpengine $OPTIONS
