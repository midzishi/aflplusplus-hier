# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG parent_image
FROM $parent_image

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        python3-setuptools \
        automake \
        unzip \
        apt-utils \
        apt-transport-https \
        ca-certificates \
        cmake \
        git \
        flex \
        bison \
        libglib2.0-dev \
        libpixman-1-dev \
        cargo \
        libgtk-3-dev \
	libtool \
	libtool-bin \
        # for QEMU mode
        ninja-build \
        gcc-$(gcc --version|head -n1|sed 's/\..*//'|sed 's/.* //')-plugin-dev \
        libstdc++-$(gcc --version|head -n1|sed 's/\..*//'|sed 's/.* //')-dev

# Download afl++-hier.
RUN git clone https://github.com/midzishi/aflplusplus-hier /afl-hier && \
    cd /afl-hier && \
    git checkout 116d437b6497287f753bcd23150d49e4f8d9c03e || \
    true

# Build without Python support as we don't need it.
# Set AFL_NO_X86 to skip flaky tests.
RUN cd /afl-hier && \
    unset CFLAGS && unset CXXFLAGS && \
    AFL_NO_X86=1 CC=clang make && \
    cd qemu_mode && CPU_TARGET=x86_64 ./build_qemu_support.sh && cd .. && \
    make -C examples/aflpp_driver && \
    cp examples/aflpp_driver/libAFLQemuDriver.a /libAFLDriver.a && \
    cp examples/aflpp_driver/aflpp_qemu_driver_hook.so /
