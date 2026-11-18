from src.models.graph import DirectedGraph
from src.config import (
    MAX_CAPACITY,
    MIN_CAPACITY,
    MIN_REQUIRED_PATHS,
)
from src.exceptions import (
    CapacityOutOfBoundsError,
    CapacityTypeError,
    DuplicateEdgeError,
    EmptyVertexIdError,
    ReciprocalEdgeError,
    SelfLoopError,
)

# Validate that capacity is an integer
def validate_capacity(capacity: int) -> None:
    if isinstance(capacity, bool) or not isinstance(capacity, int):
        raise CapacityTypeError(capacity)
    if not (MIN_CAPACITY <= capacity <= MAX_CAPACITY):
        raise CapacityOutOfBoundsError(capacity)

# Validate edge restrictions before adding to graph
def validate_new_edge(graph: DirectedGraph, u: str, v: str, capacity: int) -> None:
    if not u or not v:
        raise EmptyVertexIdError()
    if u == v:
        raise SelfLoopError(u, v)
    if (u, v) in graph.edges:
        raise DuplicateEdgeError(u, v)
    if (v, u) in graph.edges:
        raise ReciprocalEdgeError(u, v)
    validate_capacity(capacity)

# Validate source s and sink t selection
def validate_source_sink(graph: DirectedGraph, s: str, t: str, only_active: bool = True) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if s not in graph.vertices:
        errors.append(f"Source vertex '{s}' does not exist in V.")
    if t not in graph.vertices:
        errors.append(f"Sink vertex '{t}' does not exist in V.")
    if s == t:
        errors.append("Source 's' and sink 't' must be different vertices.")
    if not errors and not graph.has_two_distinct_paths(s, t, only_active=only_active):
        errors.append(
            f"There must be at least {MIN_REQUIRED_PATHS} distinct directed paths from '{s}' to '{t}'."
        )
    return len(errors) == 0, errors
