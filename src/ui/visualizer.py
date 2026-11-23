"""
Module: src/ui/visualizer.py
Description:
    Graphviz DOT representation generator for the logistics network, displaying
    distribution centers, route directions, 'flow / capacity' labels, minimum
    cut partition (S, T), and disabled routes.
"""

import graphviz

from src.models.edge import Edge
from src.models.graph import DirectedGraph

FONT_FAMILY = "sans-serif"


def _get_node_attributes(
    vertex_id: str,
    label: str,
    s: str | None,
    t: str | None,
    s_set: set[str],
    t_set: set[str],
) -> dict[str, str]:
    """Return Graphviz visual attributes for a vertex based on its role and cut partition."""
    attrs = {
        "label": vertex_id,
        "tooltip": f"{vertex_id} - {label}" if label else vertex_id,
        "shape": "circle",
        "fixedsize": "true",
        "width": "0.58",
        "style": "filled",
        "fontname": FONT_FAMILY,
        "fontsize": "17",
        "fontcolor": "#F1F5F9",
    }

    if vertex_id == s:
        attrs.update(
            {
                "shape": "doublecircle",
                "width": "0.62",
                "fillcolor": "#132A1E",
                "color": "#34D399",
                "penwidth": "1.8",
            }
        )
    elif vertex_id == t:
        attrs.update(
            {
                "shape": "doublecircle",
                "width": "0.62",
                "fillcolor": "#241734",
                "color": "#A78BFA",
                "penwidth": "1.8",
            }
        )
    elif vertex_id in s_set:
        attrs.update(
            {
                "fillcolor": "#132238",
                "color": "#60A5FA",
                "penwidth": "1.5",
            }
        )
    elif vertex_id in t_set:
        attrs.update(
            {
                "fillcolor": "#2C1F12",
                "color": "#FBBF24",
                "penwidth": "1.5",
            }
        )
    else:
        attrs.update(
            {
                "fillcolor": "#1E242B",
                "color": "#64748B",
                "penwidth": "1.2",
            }
        )

    return attrs


def _get_edge_attributes(
    edge: Edge,
    flows: dict[tuple[str, str], int] | None,
    cut_edge_set: set[tuple[str, str]],
) -> dict[str, str]:
    """Return Graphviz visual attributes for a directed edge."""
    if not edge.active:
        return {
            "label": f" {edge.capacity} (off) ",
            "color": "#475569",
            "fontcolor": "#64748B",
            "style": "dashed",
            "penwidth": "1.1",
            "arrowsize": "0.75",
            "fontname": FONT_FAMILY,
            "fontsize": "12",
        }

    flow = flows.get((edge.u, edge.v), 0) if flows is not None else None
    text = f" {flow} / {edge.capacity} " if flow is not None else f" {edge.capacity} "
    attrs = {
        "label": text,
        "style": "solid",
        "arrowsize": "0.75",
        "fontname": FONT_FAMILY,
        "fontsize": "12",
    }

    if (edge.u, edge.v) in cut_edge_set:
        attrs.update({"color": "#F87171", "fontcolor": "#FCA5A5", "penwidth": "2.2"})
    elif flow is not None and flow == edge.capacity:
        attrs.update({"color": "#60A5FA", "fontcolor": "#93C5FD", "penwidth": "1.6"})
    elif flow is not None and flow > 0:
        attrs.update({"color": "#34D399", "fontcolor": "#6EE7B7", "penwidth": "1.3"})
    else:
        attrs.update({"color": "#475569", "fontcolor": "#94A3B8", "penwidth": "1.0"})

    return attrs


def build_network_digraph(
    graph: DirectedGraph,
    s: str | None = None,
    t: str | None = None,
    flows: dict[tuple[str, str], int] | None = None,
    min_cut: dict | None = None,
) -> graphviz.Digraph:
    """Build a Graphviz Digraph representing the logistics network and flow results."""
    dot = graphviz.Digraph(name=graph.name)
    dot.attr(
        rankdir="LR",
        nodesep="0.45",
        ranksep="0.75",
        bgcolor="transparent",
        fontname=FONT_FAMILY,
    )

    s_set = set(min_cut["S"]) if min_cut else set()
    t_set = set(min_cut["T"]) if min_cut else set()
    cut_edge_set = (
        {(u, v) for u, v, _ in min_cut["cut_edges"]} if min_cut else set()
    )

    for vertex_id, vertex in graph.vertices.items():
        node_attrs = _get_node_attributes(
            vertex_id, vertex.label, s, t, s_set, t_set
        )
        dot.node(vertex_id, **node_attrs)

    for edge in graph.get_edges(only_active=False):
        edge_attrs = _get_edge_attributes(edge, flows, cut_edge_set)
        dot.edge(edge.u, edge.v, **edge_attrs)

    return dot
