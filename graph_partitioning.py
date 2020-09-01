# Copyright 2020 D-Wave Systems Inc.
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

import networkx as nx
import numpy as np
from dqmclient import solve

# Graph partitioning with DQM solver

# Size of the graph
graph_nodes = 40

# Create clique
G = nx.complete_graph(n=graph_nodes)
n_edges = len(G)
num_partitions = 2

# initial setup of linear list
linear = [(i, j, 0) for i in range(n_edges) for j in range(num_partitions)]

# introduce ability to refer to variables by name, and make the third
# variable float
linear = np.asarray(linear, dtype=[('v', np.intc), ('case', np.intc),
                    ('bias', np.float)])

# the gradient will be used as the bias. Start at zero and go up to the
# number of partitions, in steps. This will favor lowest-numbered partitions 
# and penalize higher-numbered partitions. We're assuming a linear relationship
# as a first guess.
gradient = np.linspace(0, num_partitions - 1, num_partitions)
linear['bias'] = np.tile(gradient, n_edges)

# define the connectivity dict as the graph
connectivity = np.asarray(G.edges, dtype=[('u', np.intc), ('v', np.intc)])

# value of Lagrange parameter
lagrange = 3

# We use an identity matrix to help set up the quadratic. Whenever
# (node, partition) is the same - the on-diagonal terms - we penalize it with
# strength 'lagrange'.
# All other terms are zero.
partitioning_objective = np.eye(num_partitions).reshape([-1]) * lagrange
quadratic = np.tile(partitioning_objective, len(connectivity))

# DQM solver parameters
num_reads = 10
num_sweeps = 10

# use dqmclient's solve to get to the solver
sampleset = solve(linear, connectivity, quadratic,
                  num_reads=num_reads, num_sweeps=num_sweeps,
                  profile='dqm_prod', connection_close=True)

# get the first solution
sample = sampleset.first.sample
energy = sampleset.first.energy

print("Number of nodes in one set is {}, in the other, {}. \nEnergy is {}.".format(sum(sampleset.first.sample.values()), graph_nodes - sum(sampleset.first.sample.values()), sampleset.first.energy))

# Compute the number of links between different partitions
sum_diff = 0
for i, j in G.edges:
    if sampleset.first.sample[i] != sampleset.first.sample[j]:
        sum_diff += 1
print("Graph coloring solution: ", sample)
print("Graph coloring solution energy: ", energy)
print("Graph coloring solution validity: ", sum_diff)
