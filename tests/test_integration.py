# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import unittest
import os
import sys

from dwave.system import LeapHybridCQMSampler
import networkx as nx

import demo

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestSmoke(unittest.TestCase):
    @unittest.skipIf(os.getenv('SKIP_INT_TESTS'), "Skipping integration test.")
    def test_smoke(self):
        """Run demo.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'demo.py')
        subprocess.check_output([sys.executable, demo_file])

class TestDemo(unittest.TestCase):
    def test_default_soln(self):
        """Check the default solution quality."""

        n = 100
        k = 4
        p_in = 0.5
        p_out = 0.01

        G = nx.random_partition_graph([int(n/k)]*k, p_in, p_out)

        cqm = demo.build_cqm(G, k)

        sampler = LeapHybridCQMSampler()

        sample = demo.run_cqm_and_collect_solutions(cqm, sampler)

        _, partitions = demo.process_sample(sample, G, k, verbose=False)
        self.assertEqual(len(partitions), k)

        # Check that constraints were followed
        nodes = list(G.nodes)
        for key, partition in partitions.items():
            self.assertEqual(len(partition), n/k)
            for node in partition:
                nodes.remove(node)
  
        self.assertFalse(nodes)
