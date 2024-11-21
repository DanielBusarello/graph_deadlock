# Graph Reduction

### Developed by Daniel Busarello

To run this program, first install the dependencies from `requirements.txt`.

``` bash
pip install -r requirements.txt
```

Then run `main.py` script.

### Plotting Graph

To plot a node into the graph, use `left mouse button`. You can select if it is a Process or Resource pressing `P` or `R` key.

Resource nodes must have the capacity, so a dialogbox will be shown when adding a Resource node.

To add an edge, use `right mouse button` to select a node, then select the target node. Note that Processes nodes can only be connected to a Resources nodes (vice-versa).

To remove a node from the graph, select the desired node and click with `middle mouse button (scroll)`. It will remove all connections from the node as well.

### Key mappings

`P` - Change node type to Process. <br>
`R` - Change node type to Resource. <br>
`I` - Logs the nodes and edges from the graph. <br>
`X` - Executes the algorithm to remove allocations and Deadlocks (if present). <br>
`C` - Save the current graph. <br>
`V` - Load a graph from a file. <br>
`M` - Move the selected node to current mouse position. <br>

### Loading a Graph file

Using `V` key, it is possible to load a graph from a file. The file must follow the pattern below:

``` json
{
    "nodes": [
        "P1", // Process node name
        "R1 (2)", // Resource node name with the capacity
        ...
    ],
    "edges": [
        [
            "P1",
            "R1 (2)"
        ],
        ...
    ],
    "node_positions": {
        "P1": [
            2.6451612903225805, // Position of the node in the canvas [x, y]
            7.2727272727272725
        ],
        "R1 (2)": [
            7.129032258064516,
            3.7229437229437234
        ],
        ...
    },
    "node_indexes": {
        "process": 1, // Last index of the node name (i.e. P1, P2, ..., Pn - last index is n)
        "resource": 1
    }
}
```