"""
Module: src/core/validators.py
Description:
    Mathematical validators for edge capacities, new route constraints,
    and source/sink selection in the directed graph model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import (
    MAX_EDGE_CAPACITY,
    MAX_INITIAL_EDGES,
    MAX_INITIAL_VERTICES,
    MAX_MANUAL_VERTICES,
    MIN_EDGE_CAPACITY,
    MIN_INITIAL_EDGES,
    MIN_INITIAL_VERTICES,
    MIN_MANUAL_VERTICES,
    MIN_REQUIRED_PATHS,
)
from src.core.exceptions import (
    CapacityOutOfBoundsError,
    CapacityTypeError,
    DuplicateEdgeError,
    EmptyVertexIdError,
    InsufficientPathsError,
    IsolatedVertexError,
    NetworkBoundsError,
    ReciprocalEdgeError,
    SameSourceSinkError,
    SelfLoopError,
    VertexNotFoundError,
)

if TYPE_CHECKING:
    from src.models.graph import DirectedGraph


def validate_capacity(capacity: int) -> None:
    """Validate that capacity is an integer within [MIN_EDGE_CAPACITY, MAX_EDGE_CAPACITY]."""
    if isinstance(capacity, bool) or not isinstance(capacity, int):
        raise CapacityTypeError(capacity)
    if not (MIN_EDGE_CAPACITY <= capacity <= MAX_EDGE_CAPACITY):
        raise CapacityOutOfBoundsError(capacity, MIN_EDGE_CAPACITY, MAX_EDGE_CAPACITY)


def validate_new_edge(graph: DirectedGraph, u: str, v: str, capacity: int) -> None:
    """Validate model restrictions before adding edge (u, v) to the graph."""
    if not u or not v:
        raise EmptyVertexIdError()
    if u == v:
        raise SelfLoopError(u, v)
    if (u, v) in graph.edges:
        raise DuplicateEdgeError(u, v)
    if (v, u) in graph.edges:
        raise ReciprocalEdgeError(u, v)
    validate_capacity(capacity)


def validate_source_sink(
    graph: DirectedGraph,
    s: str,
    t: str,
    only_active: bool = True,
) -> None:
    """Validate source s and sink t existence, distinctness, and minimum directed paths."""
    if s not in graph.vertices:
        raise VertexNotFoundError(s)
    if t not in graph.vertices:
        raise VertexNotFoundError(t)
    if s == t:
        raise SameSourceSinkError()
    if not graph.has_min_distinct_paths(
        s, t, min_paths=MIN_REQUIRED_PATHS, only_active=only_active
    ):
        raise InsufficientPathsError(s, t, MIN_REQUIRED_PATHS)


def _validate_no_isolated_vertices(graph: DirectedGraph) -> None:
    """Verify that every vertex v in V has at least one incident edge."""
    connected: set[str] = set()
    for edge in graph.get_edges(only_active=False):
        connected.add(edge.u)
        connected.add(edge.v)
    for v_id in graph.get_vertices():
        if v_id not in connected:
            raise IsolatedVertexError(v_id)


def validate_initial_network(graph: DirectedGraph) -> None:
    """Validate initial bounds (10 <= |V| <= 12, 15 <= |E| <= 20) and no isolated vertices."""
    num_v = len(graph.get_vertices())
    num_e = len(graph.get_edges(only_active=True))
    if not (MIN_INITIAL_VERTICES <= num_v <= MAX_INITIAL_VERTICES):
        raise NetworkBoundsError("vertex", num_v, MIN_INITIAL_VERTICES, MAX_INITIAL_VERTICES)
    if not (MIN_INITIAL_EDGES <= num_e <= MAX_INITIAL_EDGES):
        raise NetworkBoundsError("edge", num_e, MIN_INITIAL_EDGES, MAX_INITIAL_EDGES)
    _validate_no_isolated_vertices(graph)


def validate_manual_network(graph: DirectedGraph) -> None:
    """Validate manual case bounds (4 <= |V| <= 6) and no isolated vertices."""
    num_v = len(graph.get_vertices())
    if not (MIN_MANUAL_VERTICES <= num_v <= MAX_MANUAL_VERTICES):
        raise NetworkBoundsError("vertex", num_v, MIN_MANUAL_VERTICES, MAX_MANUAL_VERTICES)
    _validate_no_isolated_vertices(graph)
