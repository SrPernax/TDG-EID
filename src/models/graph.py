# Directed Graph class G = (V, E)
from src.config import MIN_REQUIRED_PATHS
from src.exceptions import EdgeNotFoundError, EmptyVertexIdError, GraphError
from src.models.edge import Edge
from src.models.vertex import Vertex


class DirectedGraph:
    # Directed graph G = (V, E)
    def __init__(self, name: str = "Graph") -> None:
        self.name: str = name
        self.vertices: dict[str, Vertex] = {}
        self.edges: dict[tuple[str, str], Edge] = {}
        self.adj: dict[str, set[str]] = {}

    # Add or update a Vertex in V.
    def add_vertex(self, vertex_id: str, label: str = "") -> Vertex:
        if not vertex_id:
            raise EmptyVertexIdError()

        if vertex_id in self.vertices:
            if label:
                self.vertices[vertex_id].label = label
            return self.vertices[vertex_id]

        vertex = Vertex(vertex_id, label)
        self.vertices[vertex_id] = vertex
        self.adj[vertex_id] = set()
        return vertex

    # Insert a directed Edge(u, v)
    def register_edge(self, u: str, v: str, capacity: int, active: bool = True) -> Edge:
        if u not in self.vertices:
            self.add_vertex(u)
        if v not in self.vertices:
            self.add_vertex(v)

        edge = Edge(u, v, capacity, active)
        self.edges[(u, v)] = edge
        self.adj[u].add(v)
        return edge

    # Return list of all vertex IDs in V
    def get_vertices(self) -> list[str]:
        return list(self.vertices.keys())

    # Return list of Edge objects in E
    def get_edges(self, only_active: bool = False) -> list[Edge]:
        if only_active:
            return [e for e in self.edges.values() if e.active]
        return list(self.edges.values())

    # Return the Edge(u, v) instance if it exists
    def get_edge(self, u: str, v: str) -> Edge | None:
        return self.edges.get((u, v))

    # Return True if directed edge (u, v) exists in E.
    def has_edge(self, u: str, v: str, only_active: bool = False) -> bool:
        edge = self.edges.get((u, v))
        if edge is None:
            return False
        return edge.active if only_active else True

    # Return capacity c(u, v)
    def get_capacity(self, u: str, v: str, only_active: bool = True) -> int:
        edge = self.edges.get((u, v))
        if edge is None or (only_active and not edge.active):
            return 0
        return edge.capacity

    # Return outgoing adjacent vertex IDs from u
    def get_neighbors(self, u: str, only_active: bool = True) -> list[str]:
        if u not in self.adj:
            return []
        return [v for v in self.adj[u] if not only_active or self.edges[(u, v)].active]

    # Check if at least 2 distinct directed paths exist from s to t
    def has_two_distinct_paths(self, s: str, t: str, only_active: bool = True) -> bool:
        if s not in self.vertices or t not in self.vertices or s == t:
            return False

        count = 0
        stack: list[tuple[str, set[str]]] = [(s, {s})]

        while stack:
            u, visited = stack.pop()
            if u == t:
                count += 1
                if count >= MIN_REQUIRED_PATHS:
                    return True
                continue

            for neighbor in self.get_neighbors(u, only_active=only_active):
                if neighbor not in visited:
                    stack.append((neighbor, visited | {neighbor}))

        return False

    # Disable or reactivate an existing route (u, v).
    def toggle_edge(self, u: str, v: str, active: bool | None = None) -> tuple[bool, str]:
        edge = self.edges.get((u, v))
        if edge is None:
            return False, str(EdgeNotFoundError(u, v))
        edge.active = (not edge.active) if active is None else bool(active)
        return True, ""

    # Update capacity of an existing route (u, v)
    def update_capacity(self, u: str, v: str, new_cap: int) -> tuple[bool, str]:
        from src.validators import validate_capacity

        edge = self.edges.get((u, v))
        if edge is None:
            return False, str(EdgeNotFoundError(u, v))
        try:
            validate_capacity(new_cap)
        except GraphError as exc:
            return False, str(exc)
        edge.capacity = new_cap
        return True, ""

    # Add a new route (u, v)
    def add_edge(self, u: str, v: str, cap: int) -> tuple[bool, str]:
        from src.validators import validate_new_edge

        try:
            validate_new_edge(self, u, v, cap)
        except GraphError as exc:
            return False, str(exc)
        self.register_edge(u, v, cap, active=True)
        return True, ""

    # Return an independent deep copy of the graph
    def copy(self) -> "DirectedGraph":
        cloned = DirectedGraph(name=self.name)
        for v in self.vertices.values():
            cloned.add_vertex(v.id, v.label)
        for e in self.edges.values():
            cloned.register_edge(e.u, e.v, e.capacity, e.active)
        return cloned
