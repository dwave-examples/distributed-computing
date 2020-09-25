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
from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler

# Graph partitioning with DQM solver

# Size of the graph
graph_nodes = 16

# Create clique
G = nx.complete_graph(n=graph_nodes)
n_edges = len(G)
num_partitions = 4
partitions = range(num_partitions)

# Initialize the DQM object
dqm = DiscreteQuadraticModel()

# initial value of Lagrange parameter
lagrange = 3

# Load the DQM. Define the variables, and then set biases and weights.
# We set the linear biases to favor lower-numbered colors; this will
# have the effect of minimizing the number of colors used.
# We penalize edge connections by the Lagrange parameter, to encourage
# connected nodes to have different colors.
for p in G.nodes:
    dqm.add_variable(num_partitions, label=p)
for p in G.nodes:
    dqm.set_linear(p, partitions)
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): lagrange for c in partitions})

# Initialize the DQM solver
sampler = LeapHybridDQMSampler(profile='dqm_test')

# Solve the problem using the DQM solver
sampleset = sampler.sample_dqm(dqm)

# get the first solution
sample = sampleset.first.sample
energy = sampleset.first.energy

# Compute the number of links between different partitions
sum_diff = 0
for i, j in G.edges:
    if sampleset.first.sample[i] != sampleset.first.sample[j]:
        sum_diff += 1
print("Solution: ", sample)
print("Solution energy: ", energy)
print("Number of links between partitions: ", sum_diff)
