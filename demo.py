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

"""Graph partitioning with CQM solver."""

from random import random
from collections import defaultdict
import sys

import networkx as nx
import numpy as np
import click
import matplotlib
from dimod import Binary, ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler

try:
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib.use("agg")
    import matplotlib.pyplot as plt



def build_graph(graph, nodes, degree, prob, p_in, p_out, new_edges, k_partition):
    """Builds graph from user specified parameters or use defaults.
    
    Args:
        See @click decorator before main.

    Returns:
        G (Graph): The graph to be partitioned
    """
    
    k = k_partition

    if k * nodes > 5000:
        raise ValueError("Problem size is too large.")
    elif nodes % k != 0:
        raise ValueError("Number of nodes must be divisible by k.")

    # Build graph using networkx
    if graph == 'partition':
        print("\nBuilding partition graph...")
        G = nx.random_partition_graph([int(nodes/k)]*k, p_in, p_out)

    elif graph == 'internet':
        print("\nReading in internet graph of size", nodes, "...")
        G = nx.random_internet_as_graph(nodes)

    elif graph == 'rand-reg':
        if degree >= nodes:
            raise ValueError("degree must be less than number of nodes")
        if degree * nodes % 2 == 1:
            raise ValueError("degree * nodes must be even")
        print("\nGenerating random regular graph...")
        G = nx.random_regular_graph(degree, nodes)

    elif graph == 'ER':
        print("\nGenerating Erdos-Renyi graph...")
        G = nx.erdos_renyi_graph(nodes, prob)

    elif graph == 'SF':
        if new_edges > nodes:
            raise ValueError("Number of edges must be less than number of nodes")
        print("\nGenerating Barabasi-Albert scale-free graph...")
        G = nx.barabasi_albert_graph(nodes, new_edges)

    else:
        # Should not be reachable, due to click argument validation
        raise ValueError(f"Unexpected graph type: {graph}")

    return G


# Visualize the input graph
def visualize_input_graph(G):
    """Visualize the graph to be partitioned.
    Args:
        G (Graph): Input graph to be partitioned
    
    Returns:
        None. Image saved as input_graph.png.
    """

    pos = nx.random_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=20, node_color='r', edgecolors='k')
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), style='solid', edge_color='#808080')
    plt.draw()
    plt.savefig('input_graph.png')
    plt.close()


def build_cqm(G, k):
    """Build the CQM.
    Args:
        G (Graph): Input graph to be partitioned
        k (int): Number of partitions to be used
    
    Returns:
        cqm (ConstrainedQuadraticModel): The CQM for our problem
    """

    # Set up the partitions
    partitions = range(k)

    # Initialize the CQM object
    print("\nBuilding constrained quadratic model...")
    cqm = ConstrainedQuadraticModel()

    # Add binary variables, one for each node and each partition in the graph
    print("\nAdding variables....")
    v = [[Binary(f'v_{i},{k}') for k in partitions] for i in G.nodes]   

    # One-hot constraint: each node is assigned to exactly one partition
    print("\nAdding one-hot constraints...")
    for n in G.nodes:
        # print("\nAdding one-hot for node", n)
        cqm.add_constraint(quicksum(v[n]) == 1, label='one-hot-node-{}'.format(n)) 

    # Constraint: Partitions have equal size
    print("\nAdding partition size constraint...")
    for p in partitions:
        # print("\nAdding partition size constraint for partition", p)
        cqm.add_constraint(quicksum(v[n][p] for n in G.nodes) == G.number_of_nodes()/k, label='partition-size-{}'.format(p))

    # Objective: minimize edges between partitions
    print("\nAdding objective...")
    min_edges = []
    for i,j in G.edges:
        for p in partitions:
            min_edges.append(v[i][p]+v[j][p]-2*v[i][p]*v[j][p])
    cqm.set_objective(sum(min_edges))

    return cqm


def run_cqm_and_collect_solutions(cqm, sampler):
    """Send the CQM to the sampler and return the best sample found.
    Args:
        cqm (ConstrainedQuadraticModel): The CQM for our problem
        sampler: The CQM sampler to be used. Must have sample_cqm function.
    
    Returns:
        dict: The first feasible solution found
    """

    # Initialize the solver
    print("\nSending to the solver...")
    
    # Solve the CQM problem using the solver
    sampleset = sampler.sample_cqm(cqm, label='Example - Graph Partitioning')

    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)

    # Return the first feasible solution
    if not len(feasible_sampleset):
        print("\nNo feasible solution found.\n")
        return None

    return feasible_sampleset.first.sample


def process_sample(sample, G, k, verbose=True):
    """Interpret the sample found in terms of our graph.
    Args:
        sample (dict): Sample to be used
        G (graph): Original input graph
        k (int): Number of partitions
        verbose (bool): Trigger to print output to command-line
    
    Returns:
        soln (list): List of partitions, indexed by node
        partitions (dict): Each item is partition: [nodes in partition]
    """

    partitions = defaultdict(list)
    soln = [-1]*G.number_of_nodes()

    for node in G.nodes:
        for p in range(k):
            if sample[f'v_{node},{p}'] == 1:
                partitions[p].append(node)
                soln[node] = p

    # Count the nodes in each partition
    counts = np.zeros(k)
    for i in partitions:
        counts[i] += len(partitions[i])

    # Compute the number of links between different partitions
    sum_diff = 0
    for i, j in G.edges:
        if soln[i] != soln[j]:
            sum_diff += 1

    if verbose:
        print("Counts in each partition: ", counts)
        print("Number of links between partitions: ", sum_diff)
        print("Number of links within partitions:", len(G.edges)-sum_diff)

    return soln, partitions


def visualize_results(G, partitions, soln):
    """Visualize the partition.
    Args:
        G (graph): Original input graph
        partitions (dict): Each item is partition: [nodes in partition]
        soln (list): List of partitions, indexed by node
    
    Returns:
        None. Output is saved as output_graph.png.        
    """

    print("\nVisualizing output...")

    # Build hypergraph of partitions
    hypergraph = nx.Graph()
    hypergraph.add_nodes_from(partitions.keys())
    pos_h = nx.circular_layout(hypergraph, scale=2.)

    # Place nodes within partition
    pos_full = {}
    assignments = {node: soln[node] for node in range(len(soln))}
    for node, partition in assignments.items():
        pos_full[node] = pos_h[partition]

    pos_g = {}
    for _, nodes in partitions.items():
        subgraph = G.subgraph(nodes)
        pos_subgraph = nx.random_layout(subgraph)
        pos_g.update(pos_subgraph)

    # Combine hypergraph and partition graph positions
    pos = {}
    for node in G.nodes():
        pos[node] = pos_full[node] + pos_g[node]
    nx.draw_networkx_nodes(G, pos, node_size=40, node_color=soln, edgecolors='k')

    # Draw good and bad edges in different colors
    bad_edges = [(u, v) for u, v in G.edges if soln[u] != soln[v]]
    good_edges = [(u,v) for u, v, in G.edges if soln[u] == soln[v]]

    nx.draw_networkx_edges(G, pos, edgelist=good_edges, style='solid', edge_color='#7f7f7f')
    nx.draw_networkx_edges(G, pos, edgelist=bad_edges, style='solid', edge_color='k')

    # Save the output image
    plt.draw()
    output_name = 'output_graph.png'
    plt.savefig(output_name)

    print("\tOutput stored in", output_name)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-g", "--graph", type=click.Choice(['partition', 'internet', 'rand-reg', 'ER', 'SF']),
              help="Graph to partition.", default='partition', show_default=True)
@click.option("-n", "--nodes", help="Set graph size for graph.", default=100, type=click.IntRange(1),
              show_default=True)
@click.option("-d", "--degree", help="Set node degree for random regular graph.", default=4,
              type=click.IntRange(1), show_default=True)
@click.option("-p", "--prob", help="Set graph edge probability for ER graph. Must be between 0 and 1.",
              type=click.FloatRange(0, 1), default=0.25, show_default=True)
@click.option("-i", "--p-in", help="Set probability of edges within groups for partition graph. Must be between 0 and 1.",
              type=click.FloatRange(0, 1), default=0.5, show_default=True)
@click.option("-o", "--p-out", help="Set probability of edges between groups for partition graph. Must be between 0 and 1.",
              type=click.FloatRange(0, 1), default=0.001, show_default=True)
@click.option("-e", "--new-edges", help="Set number of edges from new node to existing node in SF graph.",
              default=4, type=click.IntRange(1), show_default=True)
@click.option("-k", "--k-partition", help="Set number of partitions to divide graph into.", default=4,
              type=click.IntRange(2), show_default=True)
def main(graph, nodes, degree, prob, p_in, p_out, new_edges, k_partition):

    G = build_graph(graph, nodes, degree, prob, p_in, p_out, new_edges, k_partition)

    visualize_input_graph(G)

    cqm = build_cqm(G, k_partition)

    # Initialize the CQM solver
    print("\nOptimizing on LeapHybridCQMSampler...")
    sampler = LeapHybridCQMSampler()
    
    sample = run_cqm_and_collect_solutions(cqm, sampler)
    
    if sample is not None:
        soln, partitions = process_sample(sample, G, k_partition)

        visualize_results(G, partitions, soln)


if __name__ == '__main__':
    main()
