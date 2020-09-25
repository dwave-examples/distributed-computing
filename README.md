# DQM and Graph Partitioning

A demo of Graph Partitioning using Leap's Discrete Quadratic Model (DQM) solver.

![Original Plot](readme_imgs/not_color_yet.png)

Figure: The graph that we want to color, so that no neighboring nodes have the same color.

We want to color this graph so that no neighboring nodes have the same color. This is a well-known problem (https://en.wikipedia.org/wiki/Graph_coloring) which is already in the D-Wave Collection of Examples (https://github.com/dwave-examples/map-coloring) In this repo, we're going to use the D-Wave DQM solver.

## Usage

To run the demo:

```bash
python graph_coloring.py
```

The program will produce a solution which might look like this:

```
Graph coloring solution:  {0: 0, 1: 1, 2: 2, 3: 0, 4: 1, 5: 0, 6: 1}
Graph coloring solution energy:  5.0
Graph coloring solution validity:  True
```

and when the solution is drawn:

![Color Plot](readme_imgs/color.png)

we see that no neighboring nodes have the same color. The validity check checks that that is the case.

## Code Overview
Leap's DQM solver accepts problems expressed in terms of a DiscreteQuadraticModel object. The DiscreteQuadraticModel contains two dictionaries:

* linear biases
* quadratic biases

We want to define these two dictionaries so that a low-energy solution found by the DQM solver will correspond to a solution of the graph coloring problem.

For this problem, it is easiest to think in terms of ordered pairs (node, color). We will choose colors numbered from 0 to 3, since four colors will color any map in a plane. The nodes will be numbered starting from 0 in the code. For example, the pair (1, 2) corresponds to node 1 and color 2.

### Linear Biases

We set the linear biases in order to use as few colors as possible. We assume 
a very simple relationship: color k will be penalized by an bias k. This will 
encourage the system to use the lowest numbered colors as much as possible, 
which will discourage some colors from being used. 
Here's the table that we use, for this problem:

|Node|Color|Linear Bias|
|----|-----|-----------|
|0|0|0|
|0|1|1|
|0|2|2|
|0|3|3|
|1|0|0|
|1|1|1|
|1|2|2|
...

For 7 nodes, we see that the table in this problem will have 28 rows.

### Quadratic

The quadratic dictionary tells the DQM solver how to penalize variable combinations, between different ordered pairs, that we want to avoid. In this problem, this means implementing the constraint that neighboring nodes, on the graph, should not have the same color.

An example is that since nodes 0 and 1 have an edge, we do not want both node 0 and node 1 to have color 0. We also do not want them both to have color 1, or color 2. We see that there are four combinations that we will need to penalize for nodes 0 and 1. Looking at the graph, we see we will need to do the same thing for nodes 0 and 6; and for 1 and 2; and so on.

To do this, we apply a penalty to all of these combinations, and the penalty's strength is the Lagrange parameter. If the DQM solver does not yield good solutions, we may need to increase the Lagrange parameter.

With a Lagrange penalty of 3, the quadratic dictionary is given by

|Node1|Color1|Node2|Color2|Penalty|
|-----|------|-----|------|-------|
|0|0|1|0|3|
|0|0|1|1|0|
|0|0|1|2|0|
|0|0|1|3|0|
|0|1|1|0|0|
|0|1|1|1|3|
|0|1|1|2|0|
|0|1|1|3|0|
|0|2|1|0|0|
|0|2|1|1|0|
|0|2|1|2|3|
|0|2|1|3|0|
|0|3|1|0|0|
|0|3|1|1|0|
|0|3|1|2|0|
|0|3|1|3|3|
|0|0|6|0|3|
|0|0|6|1|0|
|0|0|6|2|0|
|0|0|6|3|0|
|0|1|6|0|0|
|0|1|6|1|3|
|0|1|6|2|0|
|0|1|6|3|0|
|0|2|6|0|0|
|0|2|6|1|0|
|0|2|6|2|3|
|0|2|6|3|0|
|0|3|6|0|0|
|0|3|6|1|0|
|0|3|6|2|0|
|0|3|6|3|3|
...

You can see that there will be 16 rows for each edge in the problem graph.

## Code Specifics

Let's go through the sections of code in the graph coloring problem:

* Initialize the DQM object
* Define the graph
* Define the linear bias dictionary. The gradient method is used to implement the condition described above, of penalizing color k by bias k
* Define the quadratic dictionary. For each (node1, node2) edge in the graph, define the 16 color combinations, and penalize only the cases which have the same color
* Solve the problem using the DQM solver
* Check that the solution is valid - nodes connected by edges should have different colors

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
