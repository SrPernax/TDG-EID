"""
Module: src/models/graph.py
Description:
    Directed graph G = (V, E) with capacities and live network operations.
"""

from src.core.config import MIN_REQUIRED_PATHS
from src.core.exceptions import EdgeNotFoundError, EmptyVertexIdError
from src.core.validators import validate_capacity, validate_new_edge
from src.models.edge import Edge
from src.models.vertex import Vertex


class DirectedGraph:
    """Directed capacitated graph G = (V, E)."""

    def __init__(self, name: str = "Graph") -> None:
        self.name: str = name
        self.vertices: dict[str, Vertex] = {}
        self.edges: dict[tuple[str, str], Edge] = {}
        self.adj: dict[str, set[str]] = {}

    # --- Vertices ---

    def add_vertex(self, vertex_id: str, label: str = "") -> None:
        """Add or update a Vertex in V."""
        if not vertex_id:
            raise EmptyVertexIdError()

        if vertex_id in self.vertices:
            if label:
                self.vertices[vertex_id].label = label
            return

        self.vertices[vertex_id] = Vertex(vertex_id, label)
        self.adj[vertex_id] = set()

    def get_vertices(self) -> list[str]:
        """Return list of all vertex IDs in V."""
        return list(self.vertices.keys())

    def get_neighbors(self, u: str, only_active: bool = True) -> list[str]:
        """Return outgoing adjacent vertex IDs from u."""
        if u not in self.adj:
            return []
        return [v for v in self.adj[u] if not only_active or self.edges[(u, v)].active]

    # --- Edges ---

    def add_edge(self, u: str, v: str, capacity: int, active: bool = True) -> None:
        """Validate and insert a directed Edge(u, v) into E, creating endpoints if needed."""
        validate_new_edge(self, u, v, capacity)
        if u not in self.vertices:
            self.add_vertex(u)
        if v not in self.vertices:
            self.add_vertex(v)

        self.edges[(u, v)] = Edge(u, v, capacity, active)
        self.adj[u].add(v)

    def get_edges(self, only_active: bool = False) -> list[Edge]:
        """Return list of Edge objects in E."""
        if only_active:
            return [e for e in self.edges.values() if e.active]
        return list(self.edges.values())

    def get_edge(self, u: str, v: str) -> Edge | None:
        """Return the Edge(u, v) instance if it exists."""
        return self.edges.get((u, v))

    def has_edge(self, u: str, v: str, only_active: bool = False) -> bool:
        """Return True if directed edge (u, v) exists in E."""
        edge = self.edges.get((u, v))
        if edge is None:
            return False
        return edge.active if only_active else True

    def get_capacity(self, u: str, v: str, only_active: bool = True) -> int:
        """Return capacity c(u, v), or 0 if missing or inactive."""
        edge = self.edges.get((u, v))
        if edge is None or (only_active and not edge.active):
            return 0
        return edge.capacity

    def toggle_edge(self, u: str, v: str, active: bool | None = None) -> None:
        """Disable or reactivate an existing route (u, v)."""
        edge = self.edges.get((u, v))
        if edge is None:
            raise EdgeNotFoundError(u, v)
        edge.active = (not edge.active) if active is None else bool(active)

    def update_capacity(self, u: str, v: str, new_cap: int) -> None:
        """Update capacity of an existing route (u, v)."""
        edge = self.edges.get((u, v))
        if edge is None:
            raise EdgeNotFoundError(u, v)
        validate_capacity(new_cap)
        edge.capacity = new_cap

    # --- Graph operations ---

    def has_min_distinct_paths(
        self,
        s: str,
        t: str,
        min_paths: int = MIN_REQUIRED_PATHS,
        only_active: bool = True,
    ) -> bool:
        """Check if at least min_paths distinct directed paths exist from s to t."""
        if s not in self.vertices or t not in self.vertices or s == t:
            return False

        count = 0
        stack: list[tuple[str, set[str]]] = [(s, {s})]

        while stack:
            u, visited = stack.pop()
            if u == t:
                count += 1
                if count >= min_paths:
                    return True
                continue

            for neighbor in self.get_neighbors(u, only_active=only_active):
                if neighbor not in visited:
                    stack.append((neighbor, visited | {neighbor}))

        return False

    def copy(self) -> "DirectedGraph":
        """Return an independent deep copy of the graph."""
        cloned = DirectedGraph(name=self.name)
        for v in self.vertices.values():
            cloned.add_vertex(v.id, v.label)
        for e in self.edges.values():
            cloned.add_edge(e.u, e.v, e.capacity, active=e.active)
        return cloned
