# Graph Partitioning Using A Discrete Quadratic Model

A demo of Graph Partitioning using Leap's hybrid discrete quadratic model (DQM) solver.

![Original Plot](readme_imgs/not_partition_yet.png)

The figure above shows the graph we want to partition.

We want to partition this graph so that there are as few links between
partitions as possible, and so that the partitions have equal size.
This is a [well-known problem](https://en.wikipedia.org/wiki/Graph_partition) which is already in the [D-Wave Collection of Examples](https://github.com/dwave-examples/graph-partitioning). In this repo, we're going to use the D-Wave DQM 
solver.

## Usage

To run the demo:

```bash
python graph_partitioning.py
```

The program will produce a solution which might look like this:

```
Solution:  {0: 4, 1: 0, 2: 2, 3: 4, 4: 4, 5: 1, 6: 3, 7: 1, 8: 0, 9: 4, 10: 3, 11: 1, 12: 2, 13: 3, 14: 3, 15: 0, 16: 1, 17: 2, 18: 1, 19: 3, 20: 2, 21: 2, 22: 0, 23: 3, 24: 4, 25: 0, 26: 2, 27: 1, 28: 0, 29: 4}
Solution energy with offset included:  134.0
Counts in each partition:  [6. 6. 6. 6. 6.]
Number of links between partitions:  67
```

and when the solution is drawn:

![Partition Plot](readme_imgs/partition.png)

we see that the partitions have equal size. The code counts the number of links
between partitions.

## Code Overview
Leap's DQM solver accepts problems expressed in terms of an
Ocean [DiscreteQuadraticModel](https://docs.ocean.dwavesys.com/en/latest/docs_dimod/reference/dqm.html) object.
The DiscreteQuadraticModel has two types of bias:

* linear biases
* quadratic biases

We want to define these two biases so that a low-energy solution found by the DQM solver will correspond to a solution of the graph partitioning problem.

The QUBO has two parts: the objective, and the constraints.
The objective consists of terms which, for each edge in the graph, favor
solutions in which both nodes are in the same partition. This penalizes node
pairs which are in different partitions, and thus we minimize the number
of links between partitions.
The constraints consist of terms which constrain each partition to have the
same number of nodes; this number is the number of nodes divided by the
number of partitions.

### Linear Biases

The linear biases have contributions from both the objective and the
constraints. The contribution from the objective reduces to an expression
involving the degree of each node in the graph.
The contribution from the constraints is a constant for all
entries, and it is included so that the overall energy computation yields
a sensible result.

### Quadratic Biases

The quadratic biases also have contributions from both the objective and the
constraints, and they are summed up in the code. Note that the code needs
to add terms from node pairs which don't have edges between them; that is
done in a separate loop.

## Code Specifics

Let's go through the sections of code in the graph partitioning problem:

* Define the graph
* Initialize the DQM object
* Set the [Lagrange parameter](https://en.wikipedia.org/wiki/Lagrange_multiplier)
* Define the linear biases
* Define the quadratic biases
* Solve the problem using the DQM solver
* Count the number of links between partitions

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
