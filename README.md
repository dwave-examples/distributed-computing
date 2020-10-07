# DQM and Graph Partitioning

A demo of Graph Partitioning using Leap's Discrete Quadratic Model (DQM) solver.

![Original Plot](readme_imgs/not_partition_yet.png)

Figure: The graph that we want to partition, with the following goals:
as few edges between partitions as possible, and equal-sized partitions.

We want to partition this graph so that there are as few edges between
partitions as possible, and so that the partitions have equal size.
This is a well-known problem (https://en.wikipedia.org/wiki/Graph_partition) which is already in the D-Wave Collection of Examples (https://github.com/dwave-examples/graph-partitioning) In this repo, we're going to use the D-Wave DQM 
solver.

## Usage

To run the demo:

```bash
python graph_partitioning.py
```

The program will produce a solution which might look like this:

```
Solution:  {0: 0, 1: 1, 2: 2, 3: 3, 4: 0, 5: 1, 6: 2, 7: 3, 8: 0, 9: 1, 10: 2, 11: 3, 12: 0, 13: 1, 14: 2, 15: 3}
Solution energy:  -2.400000000000001
Counts in each partition:  [4. 4. 4. 4.]
Number of links between partitions:  96
```

and when the solution is drawn:

![Partition Plot](readme_imgs/partition.png)

we see that the partitions have equal size. The code counts the number of links
between partitions.

## Code Overview
Leap's DQM solver accepts problems expressed in terms of an
Ocean [`DiscreteQuadraticModel`] (https://docs.ocean.dwavesys.com/en/latest/docs_dimod/reference/dqm.html) object.
The DiscreteQuadraticModel contains two dictionaries:

* linear biases
* quadratic biases

We want to define these two dictionaries so that a low-energy solution found by the DQM solver will correspond to a solution of the graph partitioning problem.

For this problem, it is easiest to think in terms of ordered pairs (node, partition). We will choose partitions numbered from 0 to 3. The nodes will be numbered starting from 0 in the code. For example, the pair (1, 2) corresponds to node 1 and partition 2.

### Linear Biases

We set the linear biases in order to divide the nodes across the partitions
as equally as possible. For example, for 16 nodes, and 4 partitions, we want
to have 4 nodes in each partition. One way to do this is to put positive 
linear bias on every (node, partition) combination, except for particular
pairs that we want to favor. We start by putting bias 0 on 
(node 0, partition 0), and bias 0 on (node 1, partition 1), until we have
reached all the partitions, and then we start over with node 0, node 1, etc.
This "round robin" approach will favor putting an equal number of nodes
in all the partitions.

### Quadratic

The quadratic dictionary tells the DQM solver how to penalize variable 
combinations, between different ordered pairs, that we want to avoid. 
In this problem, this means implementing the constraint that we should have
as few links between partitions as possible.

To accomplish this, we favor links between same partitions. We put a 
negative bias on all same partition-links; and we put zero bias on links 
between different partitions. The Lagrange parameter controls the strength
of that bias.

## Code Specifics

Let's go through the sections of code in the graph partitioning problem:

* Define the graph
* Initialize the DQM object
* Set the Lagrange parameter
* Introduce the problem variables.
* Define the linear bias dictionary. The gradient method is used to implement the condition described above, of penalizing color k by bias k
* Define the quadratic dictionary. For each (node1, node2) edge in the graph, define the 16 color combinations, and penalize only the cases which have the same color
* Solve the problem using the DQM solver
* Count the number of links between partitions

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
