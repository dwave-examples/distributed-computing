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

The code implements a QUBO formulation of this problem, which is suitable for implementing for the DQM solver.

The answer that we are looking for is a partition of the nodes in the graph, so
we will assign a DQM variable for each node, i.e. variable `x_i_k` denotes
whether node `i` is in subset `k` or not.

The objective function that we want should minimize the number of 
links between different partitions. To
count how many links between different partitions we have, 
given a partition of the nodes (assignment of our binary variables), 
we start with a single edge. We begin by considering the possibilities
if this edge is in, or not in, partition `k`. The table below shows the
four possibilities. We want either both nodes to be in partition `k`, or 
neither node to be in partition `k`. To accomplish this, we assign a 1
in the edge column if one node is in partition `k` and the other node is not.

| x_i_k | x_j_k | edge (i,j) |
| :---: | :---: | :---: |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

ZOIB
From this table, we see that we can use the expression `x_i+x_j-2x_ix_j`
to calculate the edge column in our table.  Now for our entire graph, our
objective function can be written as shown below, where the sum is over all
edges in the graph, denoted by E.

![QUBO](readme_imgs/QUBO.png)

Next we need to consider our constraint:  Subset 0 and Subset 1 must have the
same sizes.  We can measure the size of Subset 1 by summing up our binary
variables.  To ensure the two subsets have the same size, we enforce a
constraint that Subset 1 has size equal to half of all nodes in the graph.  We
first consider how to represent this constraint mathematically using our chosen
binary variables, and use the following equality to represent our constraint,
where V represents the set of all nodes in the graph.

![Constraint 1](readme_imgs/constraint_1.png)

For a QUBO, we need our constraints to be represented by mathematical
expressions that are satisfied at their minimum value.  For this constraint, we
can use the following expression that has a minimum value of 0 that occurs when
Subset 1 has size exactly `|V|/2`.

![Constraint 2](readme_imgs/constraint_2.png)

To simplify this expression and determine the coefficients for our QUBO
equation, we first multiply out the expression.

![Constraint 3](readme_imgs/constraint_3.png)

Next we can simplify this expression down to linear and quadratic terms for our
QUBO.  Recall that for binary variables we can replace any squared term with a
linear term (since 0^2=0 and 1^2=1), and we can remove any constant terms in
our QUBO.  This results in the following final expression for our constraint.

![Constraint 4](readme_imgs/constraint_4.png)

To combine our objective and constraints into a single QUBO expression, we
simply add together the objective function and our constraint (multiplied by
gamma, the Lagrange parameter).

![Final QUBO](readme_imgs/final_QUBO.png)

In the code, we create the Q matrix for this QUBO as a dictionary iteratively,
looping over the edges and nodes in our graph just as we see in the summation
of our QUBO expression.

This demo generates an Erdos-Renyi random graph using the `networkx` package
for our problem instance [[1]](#1). There are three parameters to be set by the user
in this code:  chain strength, number of reads, and gamma.  Since this is a
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
