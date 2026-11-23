"""
Module: app.py
Description:
    Interactive Streamlit application to select scenarios, choose source/sink
    vertices, execute maximum flow and minimum cut calculations, and visualize
    the logistics network.
"""

import streamlit as st

from src.algorithms import edmonds_karp, find_min_cut, verify_optimality
from src.core.exceptions import GraphError
from src.core.validators import validate_source_sink
from src.data import get_preset_names, load_preset
from src.ui import build_network_digraph


def _recalculate() -> None:
    """Validate source/sink and recompute max flow, min cut, and optimality checks."""
    graph = st.session_state.graph
    s = st.session_state.source
    t = st.session_state.sink

    try:
        validate_source_sink(graph, s, t)
    except GraphError as exc:
        st.session_state.validation_error = str(exc)
        st.session_state.flow_result = None
        st.session_state.cut_result = None
        st.session_state.verification_result = None
        return

    flow_result = edmonds_karp(graph, s, t)
    cut_result = find_min_cut(graph, flow_result["residual"], s, t)
    verification_result = verify_optimality(
        graph,
        flow_result["flows"],
        flow_result["max_flow"],
        cut_result["capacity"],
        s,
        t,
    )

    st.session_state.validation_error = None
    st.session_state.flow_result = flow_result
    st.session_state.cut_result = cut_result
    st.session_state.verification_result = verification_result


def _load_scenario(preset_name: str) -> None:
    """Load a preset into session state and run initial calculations."""
    graph, s, t = load_preset(preset_name)
    st.session_state.selected_preset = preset_name
    st.session_state.graph = graph
    st.session_state.source = s
    st.session_state.sink = t
    st.session_state.source_select = s
    st.session_state.sink_select = t
    _recalculate()


def _on_scenario_change() -> None:
    """Handle scenario dropdown changes cleanly via Streamlit callback."""
    _load_scenario(st.session_state.scenario_select)


def _init_session_state() -> None:
    """Initialize Streamlit session state with the default network scenario."""
    if "graph" not in st.session_state:
        default_preset = get_preset_names()[0]
        st.session_state.scenario_select = default_preset
        _load_scenario(default_preset)


def _render_sidebar() -> None:
    """Render scenario selector and source/sink recalculation form."""
    st.sidebar.header("Control Panel")

    st.sidebar.selectbox(
        "Scenario",
        options=get_preset_names(),
        key="scenario_select",
        on_change=_on_scenario_change,
    )

    vertices = st.session_state.graph.get_vertices()

    with st.sidebar.form("source_sink_form"):
        selected_s = st.selectbox("Source (s)", options=vertices, key="source_select")
        selected_t = st.selectbox("Sink (t)", options=vertices, key="sink_select")
        submitted = st.form_submit_button(
            "Recalculate", type="primary", use_container_width=True
        )
        if submitted:
            st.session_state.source = selected_s
            st.session_state.sink = selected_t
            _recalculate()


def _render_metrics() -> None:
    """Render top-level KPI metrics and min-cut partition summary."""
    graph = st.session_state.graph
    flow_result = st.session_state.flow_result
    cut_result = st.session_state.cut_result
    verification = st.session_state.verification_result

    active_count = len(graph.get_edges(only_active=True))
    total_count = len(graph.get_edges(only_active=False))
    used_count = (
        sum(1 for f in flow_result["flows"].values() if f > 0)
        if flow_result
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Max Flow |x|",
        f"{flow_result['max_flow']} pkg/h" if flow_result else "—",
    )
    col2.metric(
        "Min Cut c(S, T)",
        f"{cut_result['capacity']} pkg/h" if cut_result else "—",
    )
    col3.metric(
        "Active Routes",
        f"{active_count} / {total_count}",
        delta=f"{used_count} with flow" if flow_result else None,
        delta_color="off",
    )
    col4.metric(
        "Optimality",
        "Verified" if (verification and verification["is_optimal"]) else "—",
    )

    if cut_result:
        s_str = ", ".join(cut_result["S"])
        t_str = ", ".join(cut_result["T"])
        cut_str = ", ".join(
            f"{u} → {v} ({cap})" for u, v, cap in cut_result["cut_edges"]
        )
        st.markdown(
            f"**Partition S:** `{{{s_str}}}` &nbsp;|&nbsp; "
            f"**Partition T:** `{{{t_str}}}`  \n"
            f"**Min Cut Edges (S → T):** `{cut_str}`"
        )


def _render_legend() -> None:
    """Render a clean, refined visual legend for nodes and edges."""
    badge = (
        "display:inline-block; padding:3px 9px; border-radius:6px; "
        "font-size:13px; font-weight:500; margin:3px 6px 3px 0;"
    )
    st.markdown(
        f"""
        <div style="margin-top: 10px; font-family: Inter, Segoe UI, Roboto, sans-serif;">
            <div style="margin-bottom: 6px;">
                <strong style="font-size:13px; color:#CBD5E1; margin-right:8px;">Nodes:</strong>
                <span style="{badge} background:#132A1E; color:#F1F5F9; border:1.5px solid #34D399;">Source (s)</span>
                <span style="{badge} background:#241734; color:#F1F5F9; border:1.5px solid #A78BFA;">Sink (t)</span>
                <span style="{badge} background:#132238; color:#F1F5F9; border:1.5px solid #60A5FA;">Set S (reachable)</span>
                <span style="{badge} background:#2C1F12; color:#F1F5F9; border:1.5px solid #FBBF24;">Set T (sink side)</span>
            </div>
            <div>
                <strong style="font-size:13px; color:#CBD5E1; margin-right:8px;">Routes (flow / capacity):</strong>
                <span style="{badge} background:transparent; color:#FCA5A5; border:1.5px solid #F87171;">Min Cut (S → T)</span>
                <span style="{badge} background:transparent; color:#93C5FD; border:1.5px solid #60A5FA;">Saturated</span>
                <span style="{badge} background:transparent; color:#6EE7B7; border:1.5px solid #34D399;">Active flow</span>
                <span style="{badge} background:transparent; color:#94A3B8; border:1px solid #475569;">Unused (0 flow)</span>
                <span style="{badge} background:transparent; color:#64748B; border:1.5px dashed #475569;">Disabled</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_custom_styles() -> None:
    """Apply clean Inter styling to Graphviz SVGs and make selectboxes pure dropdowns."""
    st.markdown(
        """
        <style>
        [data-testid="stGraphVizChart"] svg .node text {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 17px !important;
            font-weight: 600 !important;
        }
        [data-testid="stGraphVizChart"] svg .edge text {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 12px !important;
            font-weight: 500 !important;
        }
        [data-testid="stSelectbox"] div[data-baseweb="select"],
        [data-testid="stSelectbox"] div[data-baseweb="select"] * {
            cursor: pointer !important;
            user-select: none !important;
        }
        [data-testid="stSelectbox"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_network_view() -> None:
    """Render the interactive Graphviz network diagram and legend."""
    _inject_custom_styles()
    graph = st.session_state.graph
    flow_result = st.session_state.flow_result
    cut_result = st.session_state.cut_result

    dot = build_network_digraph(
        graph,
        s=st.session_state.source,
        t=st.session_state.sink,
        flows=flow_result["flows"] if flow_result else None,
        min_cut=cut_result,
    )
    st.graphviz_chart(dot, use_container_width=True)
    _render_legend()


def main() -> None:
    """Launch the interactive Streamlit simulator interface."""
    st.set_page_config(
        page_title="Package Distribution Network Simulator - INFO1158",
        layout="wide",
    )
    _init_session_state()
    _render_sidebar()

    st.title("Package Distribution Network Simulator")
    st.subheader(st.session_state.graph.name)

    if st.session_state.validation_error:
        st.error(st.session_state.validation_error)

    _render_metrics()
    _render_network_view()


if __name__ == "__main__":
    main()
