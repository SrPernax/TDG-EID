# Custom exceptions for the directed graph model and validators
from src.config import MAX_CAPACITY, MIN_CAPACITY


class GraphError(ValueError):
    """Base exception for graph model and validation errors."""

class EmptyVertexIdError(GraphError):
    def __init__(self) -> None:
        super().__init__("Vertex ID cannot be empty.")

class CapacityTypeError(GraphError):
    def __init__(self, capacity: object) -> None:
        super().__init__(f"Capacity must be an integer, got {type(capacity).__name__}.")

class CapacityOutOfBoundsError(GraphError):
    def __init__(self, capacity: int) -> None:
        super().__init__(
            f"Capacity c(u, v) = {capacity} out of valid range [{MIN_CAPACITY}, {MAX_CAPACITY}]."
        )

class SelfLoopError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(f"Self-loops are not allowed: ({u}, {v}).")

class DuplicateEdgeError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(f"Duplicate edge is not allowed: ({u}, {v}) already exists.")

class ReciprocalEdgeError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(
            f"Reciprocal edge is not allowed: ({v}, {u}) already exists, rejecting ({u}, {v})."
        )

class EdgeNotFoundError(GraphError):
    def __init__(self, u: str, v: str) -> None:
        super().__init__(f"Edge ({u}, {v}) does not exist.")
