"""
Module: src/models/vertex.py
Description:
    Represents a distribution center (vertex v in V) in the logistics network.
"""


class Vertex:
    def __init__(self, vertex_id: str, label: str = "") -> None:
        self.id: str = vertex_id
        self.label: str = label

    def __repr__(self) -> str:
        return f"Vertex({self.id})"
