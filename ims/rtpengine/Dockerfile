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

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DEB_BUILD_PROFILES="pkg.ngcp-rtpengine.nobcg729"

# Install updates and dependencies needed for install
RUN apt-get update && \
	apt-get -y install git build-essential dkms lsb-release libconfig-tiny-perl \
					   netcat-openbsd nfs-common

# Fetch RTPEngine code
RUN git clone https://github.com/sipwise/rtpengine && \
	cd rtpengine && git checkout mr13.2

# Install build dependencies
RUN cd rtpengine && apt-get -y build-dep .

# Build and install
RUN cd rtpengine && dpkg-buildpackage -b -uc -us && cd .. && \
	dpkg -i *.deb && ldconfig

CMD /mnt/rtpengine/rtpengine_init.sh
