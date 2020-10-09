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

![eq1](https://latex.codecogs.com/gif.latex?%5Clarge%20objective%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29)

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

![eq2](https://latex.codecogs.com/gif.latex?%5Clarge%20constraint%20%3D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%20-%20%5Cfrac%7BN%7D%7BK%7D%20%5Cright%20%29%5E2)

This will have its minimum when each partition has `N`/`K`  nodes.

We bring the objective and constraints together by multiplying the 
constraints by ![](https://latex.codecogs.com/gif.latex?%5Clarge%20%5Cgamma),
 the [Lagrange parameter](https://en.wikipedia.org/wiki/Lagrange_multiplier).

![eq3](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%20-%20%5Cfrac%7BN%7D%7BK%7D%20%5Cright%20%29%5E2)

There are algebraic simplifications that can be performed on this sum.
Multiplying the second term out, we find:

![eq4](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%20%5Cright%20%29%5E2%20&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%28-2%5Cfrac%7BN%7D%7Bk%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%29%20&plus;%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%5E2%7D%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D)

and then the last term is the energy offset, which gives us:

![eq5](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%7D%20&plus;%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%20%5Cright%20%29%5E2%20&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%28-2%5Cfrac%7BN%7D%7Bk%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%29)

and expanding the squared sum,

![eq6](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%7D%20&plus;%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Cleft%20%28%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7Dx_%7Bik%7D%20&plus;%202%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20%5Csum%5Climits_%7Bj%3Ei%7D%5Climits%5E%7BN%7D%20x_%7Bik%7Dx_%7Bjk%7D%20%5Cright%20%29%20&plus;%20%5Cgamma%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%28-2%5Cfrac%7BN%7D%7Bk%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20x_%7Bik%7D%29)

and we can merge the linear terms,

![eq7](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%7D%20&plus;%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%20-%202x_%7Bik%7D%20x_%7Bjk%7D%29&plus;%20%5Cgamma%20%281%20-%202%5Cfrac%7BN%7D%7BK%7D%29%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7Dx_%7Bik%7D%20&plus;%202%5Cgamma%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20%5Csum%5Climits_%7Bj%3Ei%7D%5Climits%5E%7BN%7D%20x_%7Bik%7Dx_%7Bjk%7D)

and we can move the quadratic terms together,

![eq8](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%7D%20&plus;%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7D%28x_%7Bik%7D%20&plus;%20x_%7Bjk%7D%29%20&plus;%20%5Cgamma%20%281%20-%202%5Cfrac%7BN%7D%7BK%7D%29%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7Dx_%7Bik%7D%20-%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7Dx_%7Bik%7D%20x_%7Bjk%7D%20&plus;%202%5Cgamma%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20%5Csum%5Climits_%7Bj%3Ei%7D%5Climits%5E%7BN%7D%20x_%7Bik%7Dx_%7Bjk%7D)

Now, the second term in the QUBO can be simplified if we realize that variables such as ![](https://latex.codecogs.com/gif.latex?%5Clarge%20x_%7Bik%7D) will
appear as many times as node `i` appears in the graph, which is the
degree of node `i` in the graph. Our QUBO thus reduces to:

![eq9](https://latex.codecogs.com/gif.latex?%5Clarge%20QUBO%20%3D%20%5Cgamma%5Cfrac%7BN%5E2%7D%7BK%7D%20&plus;%20%5Cfrac%7B1%7D%7B2%7D%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7Ddegree%28i%29x_%7Bik%7D%20&plus;%20%5Cgamma%20%281%20-%202%5Cfrac%7BN%7D%7BK%7D%29%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7Dx_%7Bik%7D%20-%20%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%20%5Csum%5Climits_%7Bi%2Cj%5Cepsilon%20E%7Dx_%7Bik%7D%20x_%7Bjk%7D%20&plus;%202%5Cgamma%5Csum%5Climits_%7Bk%3D1%7D%5Climits%5E%7BK%7D%5Csum%5Climits_%7Bi%3D1%7D%5Climits%5E%7BN%7D%20%5Csum%5Climits_%7Bj%3Ei%7D%5Climits%5E%7BN%7D%20x_%7Bik%7Dx_%7Bjk%7D)

Leap's DQM solver accepts problems expressed in terms of an
Ocean [DiscreteQuadraticModel](https://docs.ocean.dwavesys.com/en/latest/docs_dimod/reference/dqm.html) object.
The DiscreteQuadraticModel has two types of bias:

* linear biases
* quadratic biases

We want to define these two biases so that a low-energy solution found by the DQM solver will correspond to a solution of the graph partitioning problem.

The QUBO has five terms. The first term is the energy offset, as mentioned
earlier. The second and third terms are linear biases, and the fourth and
fifth terms are quadratic biases.

### Linear Biases

The linear biases have contributions from both the objective and the
constraints. The contribution from the objective, the second term in the QUBO,
 reduced earlier to an expression involving the degree of each node in the 
graph. The contribution from the constraints, the third term in the QUBO,
is a constant for all nodes and partitions.

### Quadratic Biases

The quadratic biases also have contributions from both the objective and the
constraints. The fourth term in the QUBO, from the objective, applies only
to edges in the graph. The fifth term in the QUBO, from the constraints,
applies to all nodes. Therefore, in the code, the quadratic bias calculations
need to distiguish node pairs which are not edges from those which are edges.

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
