"""
Module: src/core/exceptions.py
Description:
    Custom exception hierarchy for the directed graph model and validators.
"""


class GraphError(ValueError):
    """Base exception for graph model and validation errors."""


class EmptyVertexIdError(GraphError):
    def __init__(self) -> None:
        super().__init__("Vertex ID cannot be empty.")


class CapacityTypeError(GraphError):
    def __init__(self, capacity: object) -> None:
        super().__init__(
            f"Capacity must be an integer, got {type(capacity).__name__}."
        )


class CapacityOutOfBoundsError(GraphError):
    def __init__(self, capacity: int, min_capacity: int, max_capacity: int) -> None:
        super().__init__(
            f"Capacity c(u, v) = {capacity} out of valid range [{min_capacity}, {max_capacity}]."
        )


class SelfLoopError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(f"Self-loops are not allowed: ({u}, {v}).")


class DuplicateEdgeError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(
            f"Duplicate edge is not allowed: ({u}, {v}) already exists."
        )


class ReciprocalEdgeError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(
            f"Reciprocal edge is not allowed: ({v}, {u}) already exists, rejecting ({u}, {v})."
        )


class EdgeNotFoundError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(f"Edge ({u}, {v}) does not exist.")


class VertexNotFoundError(GraphError):
    def __init__(self, vertex_id: str) -> None:
        super().__init__(f"Vertex '{vertex_id}' does not exist in V.")


class SameSourceSinkError(GraphError):
    def __init__(self) -> None:
        super().__init__("Source 's' and sink 't' must be different vertices.")


class InsufficientPathsError(GraphError):
    def __init__(self, s: str, t: str, min_paths: int) -> None:
        super().__init__(
            f"There must be at least {min_paths} distinct directed paths from '{s}' to '{t}'."
        )


class NetworkBoundsError(GraphError):
    def __init__(self, element: str, count: int, min_val: int, max_val: int) -> None:
        super().__init__(
            f"Network {element} count ({count}) out of valid range [{min_val}, {max_val}]."
        )


class IsolatedVertexError(GraphError):
    def __init__(self, vertex_id: str) -> None:
        super().__init__(
            f"Isolated vertices are not allowed: '{vertex_id}' has degree 0."
        )
