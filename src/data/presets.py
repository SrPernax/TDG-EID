"""
Module: src/data/presets.py
Description:
    Predefined logistics network configurations and the manual verification test case.
"""

from src.models.graph import DirectedGraph

PRESET_INITIAL = "Main Network"
PRESET_MOD_1 = "Modification 1"
PRESET_MOD_2 = "Modification 2"
PRESET_MANUAL = "Manual Verification Case"


def build_initial_network() -> tuple[DirectedGraph, str, str]:
    """Build Configuration 1: Initial Main Network."""
    graph = DirectedGraph(name=PRESET_INITIAL)

    centers = [
        ("O", "Origin Center"),
        ("A", "North Hub A"),
        ("B", "Central Hub B"),
        ("C", "South Hub C"),
        ("D", "Sorting Plant D"),
        ("E", "Sorting Plant E"),
        ("F", "Sorting Plant F"),
        ("G", "Regional Terminal G"),
        ("H", "Regional Terminal H"),
        ("T", "Destination Center"),
    ]
    for v_id, label in centers:
        graph.add_vertex(v_id, label)

    routes = [
        ("O", "A", 10),
        ("O", "B", 8),
        ("O", "C", 6),
        ("A", "D", 7),
        ("A", "E", 4),
        ("B", "D", 3),
        ("B", "E", 5),
        ("B", "F", 4),
        ("C", "F", 6),
        ("D", "G", 8),
        ("D", "H", 2),
        ("E", "G", 4),
        ("E", "H", 6),
        ("F", "H", 5),
        ("F", "T", 3),
        ("G", "H", 2),
        ("G", "T", 9),
        ("H", "T", 8),
    ]
    for u, v, cap in routes:
        graph.add_edge(u, v, cap)
    return graph, "O", "T"


def build_modification_1() -> tuple[DirectedGraph, str, str]:
    """Build Configuration 2: Disable route (D, G) and reduce capacity of (E, H) to 3."""
    graph, s, t = build_initial_network()
    graph.name = PRESET_MOD_1

    graph.toggle_edge("D", "G", active=False)
    graph.update_capacity("E", "H", 3)

    return graph, s, t


def build_modification_2() -> tuple[DirectedGraph, str, str]:
    """Build Configuration 3: Add direct route (E, T) with cap 6 and increase (H, T) to 11."""
    graph, s, t = build_initial_network()
    graph.name = PRESET_MOD_2

    graph.add_edge("E", "T", 6)
    graph.update_capacity("H", "T", 11)

    return graph, s, t


def build_manual_verification_case() -> tuple[DirectedGraph, str, str]:
    """Build Manual Verification Test Case (6 vertices, 7 edges)."""
    graph = DirectedGraph(name=PRESET_MANUAL)

    centers = [
        ("O", "Origin O"),
        ("A", "Center A"),
        ("B", "Center B"),
        ("C", "Center C"),
        ("D", "Center D"),
        ("T", "Destination T"),
    ]
    for v_id, label in centers:
        graph.add_vertex(v_id, label)

    routes = [
        ("O", "A", 8),
        ("O", "B", 6),
        ("A", "C", 5),
        ("A", "D", 3),
        ("B", "D", 6),
        ("C", "T", 5),
        ("D", "T", 9),
    ]
    for u, v, cap in routes:
        graph.add_edge(u, v, cap)

    return graph, "O", "T"


def get_preset_names() -> list[str]:
    """Return list of available preset names."""
    return [PRESET_INITIAL, PRESET_MOD_1, PRESET_MOD_2, PRESET_MANUAL]


def load_preset(name: str) -> tuple[DirectedGraph, str, str]:
    """Load a preset configuration by name."""
    builders = {
        PRESET_INITIAL: build_initial_network,
        PRESET_MOD_1: build_modification_1,
        PRESET_MOD_2: build_modification_2,
        PRESET_MANUAL: build_manual_verification_case,
    }
    return builders[name]()
