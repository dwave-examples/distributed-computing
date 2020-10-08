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

# Graph partitioning with DQM solver

# Number of nodes in the graph
num_nodes = 30

# Create a random geometric graph
G = nx.random_geometric_graph(n=num_nodes, radius=0.4, dim=2, seed=518)

# Set up the partitions
num_partitions = 5
partitions = range(num_partitions)

# Initialize the DQM object
dqm = DiscreteQuadraticModel()

# initial value of Lagrange parameter
lagrange = 10

# Define the DQM variables. We need to define all of them first because there
# are not edges between all the nodes; hence, there may be quadratic terms
# between nodes which don't have edges connecting them.
for p in G.nodes:
    dqm.add_variable(num_partitions, label=p)

constraint_const = lagrange * (1 - (2 * num_nodes / num_partitions))
for p in G.nodes:
    # Compose the linear term as a sum of the constraint contribution and
    # the objective contribution
    linear_term = constraint_const + (0.5 * np.ones(num_partitions) * G.degree[p])
    dqm.set_linear(p, linear_term)

# Quadratic term for node pairs which do not have edges between them
for p0, p1 in nx.non_edges(G):
    dqm.set_quadratic(p0, p1, {(c, c): (2 * lagrange) for c in partitions})

# Quadratic term for node pairs which have edges between them
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): ((2 * lagrange) - 1) for c in partitions})

# Initialize the DQM solver
sampler = LeapHybridDQMSampler()

# Solve the problem using the DQM solver
offset = lagrange * num_nodes * num_nodes / num_partitions
sampleset = sampler.sample_dqm(dqm)

# get the first solution
sample = sampleset.first.sample
energy = sampleset.first.energy

# Count the nodes in each partition
counts = np.zeros(num_partitions)
for i in sample:
    counts[sample[i]] += 1

# Compute the number of links between different partitions
sum_diff = 0
for i, j in G.edges:
    if sampleset.first.sample[i] != sampleset.first.sample[j]:
        sum_diff += 1
print("Solution: ", sample)
print("Solution energy with offset included: ", energy + offset)
print("Counts in each partition: ", counts)
print("Number of links between partitions: ", sum_diff)
