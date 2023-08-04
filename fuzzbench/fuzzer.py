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
import os
import shutil
import subprocess

from fuzzers.aflplusplus import fuzzer as aflplusplus_fuzzer
from fuzzers import utils

def build():
    os.environ['CC'] = 'clang'
    os.environ['CXX'] = 'clang++'

    os.environ['FUZZER_LIB'] = '/libAFLDriver.a'

    build_directory = os.environ['OUT']
    build_flags = os.environ['CFLAGS']

    new_env = os.environ.copy()
    utils.build_benchmark(env=new_env)
    shutil.copy('/afl-hier/afl-fuzz', build_directory)
    if os.path.exists('/afl-hier/afl-qemu-trace'):
        shutil.copy('/afl-hier/afl-qemu-trace', build_directory)
    if os.path.exists('/aflpp_qemu_driver_hook.so'):
        shutil.copy('/aflpp_qemu_driver_hook.so', build_directory)
   

def fuzz(input_corpus, output_corpus, target_binary):
    """Run fuzzer."""
    # Get LLVMFuzzerTestOneInput address.
    nm_proc = subprocess.run([
        'sh', '-c',
        'nm \'' + target_binary + '\' | grep -i \'T afl_qemu_driver_stdin\''
    ],
                             stdout=subprocess.PIPE,
                             check=True)
    target_func = '0x' + nm_proc.stdout.split()[0].decode('utf-8')
    print('[fuzz] afl_qemu_driver_stdin_input() address =', target_func)

    # Fuzzer options for qemu_mode.
    flags = ['-Q', '-c0']

    os.environ['AFL_QEMU_PERSISTENT_ADDR'] = target_func
    os.environ['AFL_ENTRYPOINT'] = target_func
    os.environ['AFL_QEMU_PERSISTENT_CNT'] = '1000000'
    os.environ['AFL_QEMU_DRIVER_NO_HOOK'] = '1'
    os.environ['AFL_USE_MULTI_LEVEL_COV'] = '1'
    os.environ['AFL_USE_HIER_SCHEDULE'] = '1'
    aflplusplus_fuzzer.fuzz(input_corpus,
                            output_corpus,
                            target_binary,
                            flags=flags)
