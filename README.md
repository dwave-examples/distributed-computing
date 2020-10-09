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
As noted earlier, the Graph Partitioning problem is in the [D-Wave Collection of Examples](https://github.com/dwave-examples/graph-partitioning), but there it is formulated for 2 partitions. In this repo, we're going to use the D-Wave DQM solver, and the formulation will be for `K` partitions.

The code implements a QUBO formulation of this problem, which is suitable for implementing on the DQM solver.

The answer that we are looking for is a partition of the nodes in the graph, so
we will assign a DQM variable for each node, i.e. variable 
![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7Bik%7D)
denotes whether node `i` is in subset `k` or not.

The objective function that we want should minimize the number of 
links between different partitions. To
count how many links between different partitions we have, 
given a partition of the nodes (assignment of our binary variables), 
we start with a single edge. We begin by considering the possibilities
if this edge is in, or not in, partition `k`. The table below shows the
four possibilities. We want either both nodes to be in partition `k`, or 
neither node to be in partition `k`. To accomplish this, we assign a 1
in the edge column if one node is in partition `k` and the other node is not.

| ![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7Bik%7D) | ![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7Bjk%7D) | edge (i,j) |
| :---: | :---: | :---: |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

From this table, we see that we can use the expression 
![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202%20x_%7Bik%7Dx_%7Bjk%7D)
to calculate the edge column in our table. Note that if we use this expression,
over all partitions and all edges, we will maximize the number of edges
between nodes in each partition, and that will minimize the number of links
between different partitions. Thus, for the entire graph, our objective
function can be written as shown below:

![eq1](https://latex.codecogs.com/gif.latex?objective%20%3D%20%5Cfrac%7B1%7D%7B2%7D%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%20%7B%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202%20x_%7Bik%7D%20x_%7Bjk%7D%29%7D)

where we have divided by 2 to avoid double-counting when a pair of nodes
is between partitions.

Next we need to consider our constraint:  Each partition must have the
same size.  We can measure the size of partition `k` by summing up our binary
variables associated with partition `k` (for example, 
![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7B1k%7D),
![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7B2k%7D), ...).
To ensure that all of the partitions have the same size, we enforce a
constraint that partition `k` has size equal to `N`/`K`, where `N` is the number
of nodes in the graph and `K` is the number of partitions.
We represent this constraint mathematically using our chosen
binary variables as follows:

![eq2](https://latex.codecogs.com/gif.latex?%5Clarge%20constraint%20%3D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bnodes%7D%20x_%7Bik%7D%20-%20%5Cfrac%7BN%7D%7BK%7D%20%5Cright%20%29%5E2)

This will have its minimum when each partition has `N`/`K`  nodes.

We bring the objective and constraints together by multiplying the 
constraints by ![](https://latex.codecogs.com/gif.latex?%5Clarge%20%5Cgamma),
 the [Lagrange parameter](https://en.wikipedia.org/wiki/Lagrange_multiplier).

![eq3](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bnodes%7D%20x_%7Bik%7D%20-%20%5Cfrac%7BN%7D%7BK%7D%20%5Cright%20%29%5E2)

There are algebraic simplifications that can be performed on this sum.
Multiplying the second term out, we find:

![eq4](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bnodes%7D%20x_%7Bik%7D%20%5Cright%20%29%5E2%20&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%28-2%5Cfrac%7BN%7D%7Bk%7D%5Csum%5Climits_%7Bnodes%7D%20x_%7Bik%7D%29%20&plus;%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%5E2%7D%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D)

QUBO = (&gamma; N^2 / K) + 0.5 * sum_partitions(k) sum_edges(E) `x_i_k+x_j_k-2x_i_kx_j_k`
 + &gamma; sum_partitions(k) ( sum_nodes(x_i_k) ) ^ 2
 + &gamma; sum_partitions(k) ( -2N/K sum_nodes(x_i_k) )

and expanding the squared sum,

QUBO = (&gamma; N^2 / K) + 0.5 * sum_partitions(k) sum_edges(E) `x_i_k+x_j_k-2x_i_kx_j_k`
 + &gamma; sum_partitions(k) ( sum_nodes(x_i_k) + 2 sum_nodes_ij (x_i_k) x_j_k )
 + &gamma; sum_partitions(k) ( -2N/K sum_nodes(x_i_k) )

In the code, we create the Q matrix for this QUBO as a dictionary iteratively,
looping over the edges and nodes in our graph just as we see in the summation
of our QUBO expression.

This demo generates an Erdos-Renyi random graph using the `networkx` package
for our problem instance [[1]](#1). There are three parameters to be set by the user
in this code:  chain strength, number of reads, and $\gamma$.  Since this is a
relatively large problem, we set a large number of reads (`num_reads = 1000`).
ZOIB
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
