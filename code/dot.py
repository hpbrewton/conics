from conics_parser import parse_edge
import pydot
import sys

def dot_parser(data):
    graph = pydot.graph_from_dot_data(data)
    edges = []
    for edge in graph[0].get_edge_list():
        points = edge.obj_dict['points']
        x = points[0]
        y = points[1]
        l = edge.obj_dict['attributes']['label'][1:-1]
        edge_parts = parse_edge(l)[1:]
        edges.append(['edge', x, *edge_parts, y])
    return edges



