"""
Module: src/algorithms/max_flow.py
Description:
    Custom implementation of the Edmonds-Karp Maximum Flow algorithm, residual
    graph construction, Minimum Cut (S, T) identification, and automated
    mathematical verification (capacity constraints, flow conservation at
    intermediate vertices, and strong duality |x| = c(S, T)).
"""

from collections import deque

from src.core.exceptions import SameSourceSinkError, VertexNotFoundError
from src.models.graph import DirectedGraph


def build_residual_graph(graph: DirectedGraph) -> dict[str, dict[str, int]]:
    """Build the initial residual adjacency map from active edges of the graph."""
    residual: dict[str, dict[str, int]] = {v_id: {} for v_id in graph.vertices}

    for edge in graph.get_edges(only_active=True):
        residual[edge.u][edge.v] = edge.capacity
        residual[edge.v].setdefault(edge.u, 0)

    return residual


def _bfs_augmenting_path(residual: dict[str, dict[str, int]], s: str, t: str,) -> tuple[list[str], int] | None:
    """Find a shortest augmenting path from s to t via BFS and its bottleneck capacity."""
    parent: dict[str, str | None] = {s: None}
    queue: deque[str] = deque([s])

    while queue:
        u = queue.popleft()
        if u == t:
            break
        for v, cap in residual.get(u, {}).items():
            if cap > 0 and v not in parent:
                parent[v] = u
                queue.append(v)

    if t not in parent:
        return None

    path: list[str] = []
    curr: str | None = t
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()

    bottleneck = min(
        residual[path[i]][path[i + 1]] for i in range(len(path) - 1)
    )
    return path, bottleneck


def edmonds_karp(graph: DirectedGraph, s: str, t: str) -> dict:
    """Compute maximum flow from s to t using the Edmonds-Karp algorithm."""
    if s not in graph.vertices:
        raise VertexNotFoundError(s)
    if t not in graph.vertices:
        raise VertexNotFoundError(t)
    if s == t:
        raise SameSourceSinkError()

    residual = build_residual_graph(graph)
    iterations: list[dict] = []
    step = 0

    while True:
        found = _bfs_augmenting_path(residual, s, t)
        if found is None:
            break

        path, bottleneck = found
        step += 1

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck

        iterations.append(
            {
                "iteration": step,
                "path": path,
                "bottleneck": bottleneck,
            }
        )

    flows: dict[tuple[str, str], int] = {}
    for edge in graph.get_edges(only_active=False):
        if edge.active:
            flows[(edge.u, edge.v)] = edge.capacity - residual[edge.u][edge.v]
        else:
            flows[(edge.u, edge.v)] = 0

    out_s = sum(flow for (u, _), flow in flows.items() if u == s)
    in_s = sum(flow for (_, v), flow in flows.items() if v == s)
    max_flow_value = out_s - in_s

    return {
        "max_flow": max_flow_value,
        "flows": flows,
        "residual": residual,
        "iterations": iterations,
    }


def find_min_cut(graph: DirectedGraph, residual: dict[str, dict[str, int]], s: str, t: str) -> dict:
    """Identify the minimum cut partition (S, T) and crossing edges from the residual graph."""
    if s not in graph.vertices:
        raise VertexNotFoundError(s)
    if t not in graph.vertices:
        raise VertexNotFoundError(t)
    if s == t:
        raise SameSourceSinkError()

    reachable: set[str] = {s}
    queue: deque[str] = deque([s])

    while queue:
        u = queue.popleft()
        for v, cap in residual.get(u, {}).items():
            if cap > 0 and v not in reachable:
                reachable.add(v)
                queue.append(v)

    s_partition = [v for v in graph.get_vertices() if v in reachable]
    t_partition = [v for v in graph.get_vertices() if v not in reachable]

    cut_edges = [
        (edge.u, edge.v, edge.capacity)
        for edge in graph.get_edges(only_active=True)
        if edge.u in reachable and edge.v not in reachable
    ]
    cut_capacity = sum(cap for _, _, cap in cut_edges)

    return {
        "S": s_partition,
        "T": t_partition,
        "cut_edges": cut_edges,
        "capacity": cut_capacity,
    }


def verify_optimality(graph: DirectedGraph, flows: dict[tuple[str, str], int], max_flow_value: int, min_cut_capacity: int, s: str, t: str) -> dict:
    """
    Verify mathematical optimality conditions on the computed flow and min-cut:
    capacity constraints, flow conservation at intermediate vertices, and strong duality.
    """
    if s not in graph.vertices:
        raise VertexNotFoundError(s)
    if t not in graph.vertices:
        raise VertexNotFoundError(t)
    if s == t:
        raise SameSourceSinkError()

    capacity_details: list[dict] = []
    for edge in graph.get_edges(only_active=False):
        flow = flows.get((edge.u, edge.v), 0)
        ok = (0 <= flow <= edge.capacity) if edge.active else (flow == 0)
        capacity_details.append(
            {
                "edge": (edge.u, edge.v),
                "flow": flow,
                "capacity": edge.capacity,
                "active": edge.active,
                "ok": ok,
            }
        )
    capacity_ok = all(item["ok"] for item in capacity_details)

    conservation_details: list[dict] = []
    for v in graph.get_vertices():
        if v in (s, t):
            continue
        in_flow = sum(flow for (_, dst), flow in flows.items() if dst == v)
        out_flow = sum(flow for (src, _), flow in flows.items() if src == v)
        conservation_details.append(
            {
                "vertex": v,
                "in_flow": in_flow,
                "out_flow": out_flow,
                "ok": in_flow == out_flow,
            }
        )
    conservation_ok = all(item["ok"] for item in conservation_details)

    duality_ok = max_flow_value == min_cut_capacity

    return {
        "is_optimal": capacity_ok and conservation_ok and duality_ok,
        "capacity_ok": capacity_ok,
        "capacity_details": capacity_details,
        "conservation_ok": conservation_ok,
        "conservation_details": conservation_details,
        "duality_ok": duality_ok,
        "max_flow": max_flow_value,
        "min_cut_capacity": min_cut_capacity,
    }
