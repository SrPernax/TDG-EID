"""
Module: src/models/edge.py
Description:
    Represents a directed transport route (edge e in E) with capacity and active state.
"""


class Edge:
    def __init__(self, u: str, v: str, capacity: int, active: bool = True) -> None:
        self.u: str = u
        self.v: str = v
        self.capacity: int = capacity
        self.active: bool = active

    def __repr__(self) -> str:
        state = "active" if self.active else "inactive"
        return f"Edge({self.u} -> {self.v}, cap={self.capacity}, {state})"
