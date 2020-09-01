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

distance_matrix = [
        [0, 2230, 1631, 1566, 1346, 1352, 1204],
        [2230, 0, 845, 707, 1001, 947, 1484],
        [1631, 845, 0, 627, 773, 424, 644],
        [1566, 707, 627, 0, 302, 341, 1027],
        [1346, 1001, 773, 302, 0, 368, 916],
        [1352, 947, 424, 341, 368, 0, 702],
        [1204, 1484, 644, 1027, 916, 702, 0],
    ]

G = nx.Graph()
row_index = 0
single_index = 0
reverse_edge = {}
for row in distance_matrix:
    for column_index, item in enumerate(row):
        if row_index < column_index:
            G.add_edge(row_index, column_index, weight=item)
            reverse_edge[single_index] = (row_index, column_index)
            single_index += 1
    row_index += 1
N = len(distance_matrix)

# initial value of Lagrange parameter
lagrange = 4000

linear = [(i, j, 0) for i in range(N) for j in range(N)]
# introduce ability to refer to variables by name, and make the third
# variable float
linear = np.asarray(linear, dtype=[('v', np.intc), ('case', np.intc),
                    ('bias', np.float)])

# Set up the linear array - column 1-in-N constraints
# Row 1-in-N conditions are handled by the DQM solver
linear['bias'] = -lagrange * np.ones(N*N)

# define the connectivity dict as the graph
connectivity = np.asarray(G.edges, dtype=[('u', np.intc), ('v', np.intc)])

# Define the quadratic matrix. It also has contributions from the column
# 1-in-N constraints
tsp_objective = np.eye(N).reshape([-1]) * lagrange * 2
quadratic = np.tile(tsp_objective, len(connectivity))

# Include the distance terms in the quadratic matrix
number_of_terms = N * (N-1) // 2
for j in range(number_of_terms):
    for i in range(N*N*j, N*N*(j+1)):
        quadratic[i] += distance_matrix[reverse_edge[j][0]][reverse_edge[j][1]]

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

start = None
print(sample)
route = [None] * N

for key in sample:
    time = sample[key]
    city = key
    route[time] = city

if start is not None and route[0] != start:
    # rotate to put the start in front
    idx = route.index(start)
    route = route[-idx:] + route[:-idx]

if None not in route:
    cost = 0
    for i, j in zip(route, route[1:] + route[:1]):
        cost += distance_matrix[i][j]
    print(route)
    print(cost)
    print(energy)
