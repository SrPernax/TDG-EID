"""
Module: src/core/validators.py
Description:
    Mathematical validators for edge capacities, new route constraints,
    and source/sink selection in the directed graph model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import MAX_EDGE_CAPACITY, MIN_EDGE_CAPACITY, MIN_REQUIRED_PATHS
from src.core.exceptions import (
    CapacityOutOfBoundsError,
    CapacityTypeError,
    DuplicateEdgeError,
    EmptyVertexIdError,
    InsufficientPathsError,
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
