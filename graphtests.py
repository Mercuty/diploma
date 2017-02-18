from igraph import Graph, plot

g=Graph()
g.add_vertices(3)
g.add_edges([(0,1),(1,2)])
layout = g.layout("rt", 2)
plot(g, layout=layout)