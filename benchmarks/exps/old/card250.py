# -*- coding: future_fstrings -*-
#
# Copyright 2019 Peifeng Yu <peifeng@umich.edu>
# 
# This file is part of Salus
# (see https://github.com/SymbioticLab/Salus).
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Multi-lane training workloads. See card#250

LaneMgr: disabled
Scheduler: fair
Work conservation: False
Collected data: inference speed over time
"""
from __future__ import absolute_import, print_function, division, unicode_literals

from absl import flags

from benchmarks.driver.runner import Executor
from benchmarks.driver.server.config import presets
from benchmarks.driver.utils import execute
from benchmarks.driver.workload import WTL
from benchmarks.exps import run_seq, maybe_forced_preset, Pause, run_tf, run_tfdist


FLAGS = flags.FLAGS


def case1():
    scfg = maybe_forced_preset(presets.MostEfficient)
    scfg.scheduler = 'rr'
    scfg.disable_wc = True
    scfg.env['SALUS_DISABLE_LANEMGR'] = '1'

    run_seq(scfg.copy(output_dir=FLAGS.save_dir/'case1'),
            WTL.create("inception3", 50, 145),
            Pause(15),
            WTL.create("inception3", 50, 75),
            Pause(15),
            WTL.create("inception3", 50, 35),
            )


def case11():
    scfg = maybe_forced_preset(presets.MostEfficient)
    scfg.scheduler = 'fair'
    scfg.disable_wc = True
    scfg.env['SALUS_DISABLE_LANEMGR'] = '1'

    run_seq(scfg.copy(output_dir=FLAGS.save_dir/'case11'),
            WTL.create("inception3", 50, 58),
            Pause(15),
            WTL.create("inception3", 50, 58),
            Pause(5),
            WTL.create("inception3", 50, 58),
            Pause(5),
            WTL.create("inception3", 50, 58),
            Pause(5),
            WTL.create("inception3", 50, 58),
            )


def case2():
    scfg = maybe_forced_preset(presets.MostEfficient)
    scfg.scheduler = 'pack'
    scfg.logconf = 'log'
    scfg.env['SALUS_DISABLE_SHARED_LANE'] = '1'

    run_seq(scfg.copy(output_dir=FLAGS.save_dir/'case2'),
            WTL.create("inception3eval", 50, 250),
            Pause(10),
            WTL.create("inception3eval", 50, 250),
            Pause(10),
            WTL.create("inception3eval", 50, 250),
            )


def case3():
    scfg = maybe_forced_preset(presets.MostEfficient)
    scfg.scheduler = 'fair'
    scfg.env['SALUS_DISABLE_LANEMGR'] = '1'

    run_seq(scfg.copy(output_dir=FLAGS.save_dir/'case3'),
            WTL.create("inception3eval", 50, 250),
            Pause(10),
            WTL.create("inception3eval", 50, 250),
            Pause(10),
            WTL.create("inception3eval", 50, 250),
            )


def test():
    """Measure TF inference memory usage"""
    wl = WTL.create("inception3eval", 50, 50, executor=Executor.TF)
    wl.env['TF_CPP_MIN_VLOG_LEVEL'] = '1'
    wl.env['TF_CPP_MIN_LOG_LEVEL'] = ''
    outdir = FLAGS.save_dir/'test'/wl.canonical_name
    run_tf(outdir, wl)

    # filter and move file to a more convinent name
    for f in outdir.iterdir():
        with f.with_name('alloc.output').open('w') as file:
            grep = execute(['egrep', r"] (\+|-)", f.name], stdout=file, cwd=str(f.parent))
            grep.wait()
        f.unlink()
        break


def main(argv):
    command = argv[0] if argv else "case1"

    {
        "case1": case1,
        "case11": case11,
        "case2": case2,
        "case3": case3,
        "test": test,
    }[command]()
