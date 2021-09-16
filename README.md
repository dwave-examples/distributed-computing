[![Linux/Mac/Windows build status](
https://circleci.com/gh/dwave-examples/graph-partitioning-dqm.svg?style=svg)](
https://circleci.com/gh/dwave-examples/graph-partitioning-dqm)

# Distributed Computing

In [distributed computing systems](https://en.wikipedia.org/wiki/Distributed_computing), a group of computers work together to achieve
a common goal. For example, a group of computers might work together to deal
with a large data set for analysis. In these types of computing systems, each
computer manages a piece of the problem and interacts with the other computing
systems by passing messages. Each computer handles a subset of the required
operations, and some operations might require inputs computed by a different
computer. By passing a message containing the required input, the operation can
then be completed. These messages might contain information required to
continue the computations, and so can become a bottleneck to efficient
computation. By minimizing the number of messages required between computers we
can also minimize the number of dependencies between the operations performed
on different systems, making the overall computation faster and more efficient
by minimizing waiting time.

## Modeling the Problem as a Graph

To solve this problem, we build a graph or network model. Each operation for
the overall computation is represented by a node or vertex in the graph, and an
edge between nodes indicates that there is a dependency between two operations.
To minimize the number of messages passed, we would like to partition the
operations amongst the available computers so that the number of edges going
between computers (or partitions) is minimized. Additionally, we would also
like to balance the workload across our available computers by partitioning the
operations evenly.

To solve this problem in our graph model, we are looking to partition the set
of nodes into a fixed number of subsets of equal size so that the total number
of edges between subsets is minimized. This is known as the graph
k-partitioning problem. In the case where k = 2, it is straightforward to use
binary variables to indicate the subsets for each operation and solve using a
binary quadratic model, as shown in the [graph partitioning code example](https://github.com/dwave-examples/graph-partitioning). For
k > 2, the problem becomes significantly more complex.

## Usage

To run the demo, type:

```python demo.py```

Additional options are available to select different graphs to run the problem
on. To see the full list of options, type:

```python demo.py -h```

During a successful run of the program, two images are produced and saved. The
first is the original input graph, saved as `input_graph.png`.

![Example Input](readme_imgs/not_partition_yet.png)

The second highlights the partition of the population into groups.

![Example Output](readme_imgs/partition.png)

### Graphs Available

Several different types of graphs or networks are available for this demo using
the options provided. These are all built using NetworkX graph generator
functions, and the details of these functions can be found [here](https://networkx.org/documentation/stable//reference/generators.html#).

- `partition`: Partition graph; specify number of nodes, number of partitions,
  and inter- and intra-partition edge probabilities.
- `internet`: Internet Autonomous System network; specify number of nodes
  between 1,000 and 3,000.
- `rand-reg`: A random d-regular graph; specify number of nodes and value for d.
- `ER`: Erdos-Renyi random graph; specify number of nodes and edge probability.
- `SF`: Barabasi-Albert scale-free graph; specify number of nodes and number of
  edges to add from a new node to any existing nodes.

The default graph is the partition graph on 100 nodes with 4 partitions with
inter-partition edge probability of 0.5 and intra-partition edge probability of
0.001. The largest number of nodes allowed for any graph specified can be at
most 3,000.

## Code Overview

The demo program formulates this graph k-partitioning problem as a constrained
quadratic model (CQM), and solves it using the hybrid CQM solver.

### Variables

The formulation of this problem defines a binary variable x for each pair
(n, k), where n is a node in the graph and k is a partition. If the solution
returns variable (n, k) = 1, then node n is assigned to partition k. Otherwise,
if the solution returns variable (n, k) = 0, then node n is *not* assigned to
partition k.

### Objective

The objective for this problem is to minimize the number of inter-partition
edges. We can formulate this as a binary quadratic expression that needs to be
minimized by considering an arbitrary edge (i, j) between nodes i and j in the
graph. For each partition k, we add the expression
(i, k) + (j, k) - 2\*(i, k)\*(j, k) to decrease the overall cost when i and j
are assigned to the same partition, and increase the overall cost when they
are not. To see how this expression maps to these costs, we examine the
following table which demonstrates the cost of edge (i, j), depending on
whether i and j are each assigned to partition k.

| (i, k) | (j, k) | edge (i,j) | cost |
| :---: | :---: | :---: | :---: |
| 0 | 0 | intra | 0 |
| 0 | 1 | inter | 1 |
| 1 | 0 | inter | 1 |
| 1 | 1 | intra | 0 |

Now that we have an expression to appropriate cost each edge and each
partition, we simply sum over all edges and all partitions to build the
objective function that will minimize the number of inter-partition edges in
the entire graph.

**Objective:** minimize &Sigma;<sub>(i,j)</sub> &Sigma;<sub>k</sub> x<sub>(i,k)</sub> + x<sub>(j,k)</sub> - 2\*x<sub>(i,k)</sub>\*x<sub>(j,k)</sub> 

### Constraints

#### One-Hot Constraint

Each node in our graph must be assigned to exactly one partition, so we must
enforce a one-hot constraint on each node. That is, for each node i, we must
have that the sum of all binary variables associated with i is equal to 1.

**Constraint 1:** &Sigma;<sub>k</sub> x<sub>(i,k)</sub> = 1, for each node i

#### Partition Size Constraint

To efficiently distributed the operational load across computers in our system,
we would like the partitions to have equal size. If N is the total number of
nodes in the graph and k is the number of partitions available, each partition
should have size N/k. We enforce this by requiring that the sum of binary
variables associated with each partition is equal to N/k.

**Constraint 2:** &Sigma;<sub>i</sub> x<sub>(i,p)</sub> = N/k, for each partition p.

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
