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
from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler

# Graph partitioning on a clique with DQM solver

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
lagrange = 0.1

# Load the DQM. Define the variables, and then set biases and weights.
# There are two terms in the QUBO formulation for graph partitioning on a
# clique. First, we want to minimize the number of links between different
# partitions, and second we want the sizes of the partitions to be the
# same. We handle the first term by favoring links between same
# partitions; this will have the effect of penalizing links between
# partitions, hence minimizing the inter-partition links.
# We accomplish this by putting a negative sign in front of the Lagrange
# parameter in the quadratic term.
# For the second term, we provide biases that favor dividing the nodes into
# the desired number of partitions. We have a choice of how we want to 
# assign the nodes to different partitions. We will fill them in linear 
# order, starting with node 0 into partition 0, node 1 into partition 1, 
# and then start over. We put ones on all biases except these; this will
# favor the particular assignments that we want.

for p in G.nodes:
    dqm.add_variable(num_partitions, label=p)
for p in G.nodes:
    linear_list = np.ones(num_partitions)
    linear_list[p % num_partitions] = 0
    dqm.set_linear(p, linear_list)
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): -lagrange for c in partitions})

# Initialize the DQM solver
sampler = LeapHybridDQMSampler()

# Solve the problem using the DQM solver
sampleset = sampler.sample_dqm(dqm)

# get the first solution
sample = sampleset.first.sample
energy = sampleset.first.energy

# Count the solutions in each partition
counts = np.zeros(num_partitions)
for i in sample:
    counts[sample[i]] += 1

# Compute the number of links between different partitions
sum_diff = 0
for i, j in G.edges:
    if sampleset.first.sample[i] != sampleset.first.sample[j]:
        sum_diff += 1
print("Solution: ", sample)
print("Solution energy: ", energy)
print("Counts in each partition: ", counts)
print("Number of links between partitions: ", sum_diff)
