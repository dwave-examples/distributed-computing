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

from random import random
from collections import defaultdict
import sys

import networkx as nx
import numpy as np
import argparse
import matplotlib
from dimod import Binary, ConstrainedQuadraticModel
from dwave.system import LeapHybridCQMSampler

try:
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib.use("agg")
    import matplotlib.pyplot as plt

# Graph partitioning with CQM solver

def read_in_args(args):
    """Read in user specified parameters."""

    # Set up user-specified optional arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph", default='partition', choices=['partition', 'internet', 'rand-reg', 'ER', 'SF'], help='Graph to partition (default: %(default)s)')
    parser.add_argument("-n", "--nodes", help="Set graph size for graph. (default: %(default)s)", default=100, type=int)
    parser.add_argument("-d", "--degree", help="Set node degree for random regular graph. (default: %(default)s)", default=4, type=int)
    parser.add_argument("-p", "--prob", help="Set graph edge probability for ER graph. Must be between 0 and 1. (default: %(default)s)", default=0.25, type=float)
    parser.add_argument("-i", "--p-in", help="Set probability of edges within groups for partition graph. Must be between 0 and 1. (default: % (default)s)", default=0.5, type=float)
    parser.add_argument("-o", "--p-out", help="Set probability of edges between groups for partition graph. Must be between 0 and 1. (default: % (default)s)", default=0.001, type=float)
    parser.add_argument("-e", "--new-edges", help="Set number of edges from new node to existing node in SF graph. (default: %(default)s)", default=4, type=int)
    parser.add_argument("-k", "--k-partition", help="Set number of partitions to divide graph into. (default: %(default)s)", default=4, type=int)

    return parser.parse_args(args)

def build_graph(args):
    """Builds graph from user specified parameters or use defaults.
    Args:
        Args: User inputs for scenario
    
    Returns:
        G (Graph): The graph to be partitioned
    """
    
    # Build graph using networkx
    if args.k_partition < 2:
        print("\nMust have at least two partitions.\n\tSetting number of partitions to 4.\n")
        args.k_partition = 4
    if args.graph == 'partition':
        if args.nodes < 1:
            print("\nMust have at least one node in the graph.\nSetting size to 100.\n")
        if args.p_in < 0 or args.p_in > 1:
            print("\nProbability must be between 0 and 1. Setting p_in to 0.5.\n")
            args.p_in = 0.5
        if args.p_out < 0 or args.p_out > 1:
            print("\nProbability must be between 0 and 1. Setting p_out to 0.001.\n")
            args.p_out = 0.001
        print("\nBuilding partition graph...")
        k = args.k_partition
        n = int(args.nodes/k)*k
        G = nx.random_partition_graph([int(n/k)]*k, args.p_in, args.p_out)
    elif args.graph == 'internet':
        if args.nodes < 1000 or args.nodes > 3000:
            args.nodes = 1000
            print("\nSize for internet graph must be between 1000 and 3000.\nSetting size to 1000.\n")
        print("\nReading in internet graph of size", args.nodes, "...")
        G = nx.random_internet_as_graph(args.nodes)
    elif args.graph == 'rand-reg':
        if args.nodes < 1:
            print("\nMust have at least one node in the graph.\nSetting size to 100.\n")
        if args.degree < 0 or args.degree >= args.nodes:
            print("\nDegree must be between 0 and n-1. Setting size to min(4, n-1).\n")
            args.degree = min(4, args.nodes-1)
        if args.degree*args.nodes % 2 == 1:
            print("\nRequirement: n*d must be even.\n")
            if args.degree > 0:
                args.degree -= 1
                print("\nSetting degree to", args.degree, "\n")
            elif args.nodes-1 > args.degree:
                args.nodes -= 1
                print("\nSetting nodes to", args.nodes, "\n")
            else:
                print("\nSetting nodes to 1000 and degree to 4.\n")
                args.nodes = 1000
                args.degree = 4
        print("\nGenerating random regular graph...")
        G = nx.random_regular_graph(args.degree, args.nodes)
    elif args.graph == 'ER':
        if args.nodes < 1:
            print("\nMust have at least one node in the graph. Setting size to 1000.\n")
            args.nodes = 1000
        if args.prob < 0 or args.prob > 1:
            print("\nProbability must be between 0 and 1. Setting prob to 0.25.\n")
            args.prob = 0.25
        print("\nGenerating Erdos-Renyi graph...")
        G = nx.erdos_renyi_graph(args.nodes, args.prob)
    elif args.graph == 'SF':
        if args.nodes < 1:
            print("\nMust have at least one node in the graph. Setting size to 1000.\n")
            args.nodes = 1000
        if args.new_edges < 0 or args.new_edges > args.nodes:
            print("\nNumber of edges must be between 1 and n. Setting to 5.\n")
            args.new_edges = 5
        print("\nGenerating Barabasi-Albert scale-free graph...")
        G = nx.barabasi_albert_graph(args.nodes, args.new_edges)
    else:
        print("\nReading in karate graph...")
        G = nx.karate_club_graph()

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
        cqm.add_constraint(sum(v[n]) == 1, label='one-hot-node-{}'.format(n)) 

    # Constraint: Partitions have equal size
    print("\nAdding partition size constraint...")
    for p in partitions:
        # print("\nAdding partition size constraint for partition", p)
        cqm.add_constraint(sum(v[n][p] for n in G.nodes) == (G.number_of_nodes()/k), label='partition-size-{}'.format(p))

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
        sampler: The sampler to be used
    
    Returns:
        best_sample (dict): Best solution found
    """

    # Initialize the solver
    print("\nSending to the solver...")
    
    # Solve the CQM problem using the solver
    sampleset = sampler.sample_cqm(cqm, label='Example - Graph Partitioning')

    # Return the first feasible solution
    first_run = True
    for sample, feas in sampleset.data(fields=['sample','is_feasible']):
        if first_run:
            best_sample = sample
        if feas:
            return sample

    print("\nNo feasible solutions found.\n")
    return best_sample

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
        None. Output is saved as output_graph.png        
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

if __name__ == '__main__':

    args = read_in_args(sys.argv[1:])

    G = build_graph(args)

    k = args.k_partition

    visualize_input_graph(G)

    cqm = build_cqm(G, k)

    # Initialize the CQM solver
    print("\nOptimizing on LeapHybridCQMSampler...")
    sampler = LeapHybridCQMSampler(profile='cqm', solver='hybrid_constrained_quadratic_model_version1_alpha')
    
    sample = run_cqm_and_collect_solutions(cqm, sampler)
    
    if sample is not None:
        soln, partitions = process_sample(sample, G, k)

    visualize_results(G, partitions, soln)