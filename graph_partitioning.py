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

from random import random
from collections import defaultdict

import networkx as nx
import numpy as np
import matplotlib
from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler

try:
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib.use("agg")
    import matplotlib.pyplot as plt

# Graph partitioning with DQM solver

# Number of nodes in the graph
num_nodes = 30

# Create a random geometric graph
G = nx.random_geometric_graph(n=num_nodes, radius=0.4, dim=2, seed=518)

# Set up the partitions
num_partitions = 5
partitions = range(num_partitions)

# Initialize the DQM object
print("\nBuilding discrete model...")
dqm = DiscreteQuadraticModel()

# initial value of Lagrange parameter
lagrange = 3

# Define the DQM variables. There is one variable for each node in the graph
# with num_partitions cases, which indicates which of the partitions it belongs
# to.
for i in G.nodes:
    dqm.add_variable(num_partitions, label=i)

constraint_const = lagrange * (1 - (2 * num_nodes / num_partitions))
for i in G.nodes:
    linear_term = constraint_const + (0.5 * np.ones(num_partitions) * G.degree[i])
    dqm.set_linear(i, linear_term)

# Quadratic term for node pairs which do not have edges between them
for p0, p1 in nx.non_edges(G):
    dqm.set_quadratic(p0, p1, {(c, c): (2 * lagrange) for c in partitions})

# Quadratic term for node pairs which have edges between them
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): ((2 * lagrange) - 1) for c in partitions})

# Initialize the DQM solver
print("\nOptimizing on LeapHybridDQMSampler...")
sampler = LeapHybridDQMSampler()

# Solve the problem using the DQM solver
offset = lagrange * num_nodes * num_nodes / num_partitions
sampleset = sampler.sample_dqm(dqm, label='Example - Graph Partitioning DQM')

# get the first solution
sample = sampleset.first.sample
energy = sampleset.first.energy

# Process sample
partitions = defaultdict(list)
for key, val in sample.items():
    partitions[val].append(key)

# Count the nodes in each partition
counts = np.zeros(num_partitions)
for i in sample:
    counts[sample[i]] += 1

# Compute the number of links between different partitions
sum_diff = 0
for i, j in G.edges:
    if sampleset.first.sample[i] != sampleset.first.sample[j]:
        sum_diff += 1

print("\nSolution:")
for i in range(num_partitions):
    print(partitions[i])

print("\nSolution energy with offset included: ", energy + offset)
print("Counts in each partition: ", counts)
print("Number of links between partitions: ", sum_diff)

# Produce visualization of result
print("\nVisualizing output...")

color_list = [(random(), random(), random()) for i in range(num_partitions)]
color_map = [color_list[sample[i]] for i in G.nodes]
nx.draw(G, node_color=color_map)
plt.savefig('graph_partition_result.png')
plt.close()

print("\nImage saved as graph_partition_result.png\n")
