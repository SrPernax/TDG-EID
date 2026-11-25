"""
Module: app.py
Description:
    Interactive Streamlit application to select scenarios, choose source/sink
    vertices, apply live network modifications, execute maximum flow and
    minimum cut calculations, visualize the logistics network, inspect
    mathematical verification tables, and compare network configurations.
"""

import streamlit as st

from src.algorithms import edmonds_karp, find_min_cut, verify_optimality
from src.core.config import MAX_EDGE_CAPACITY, MIN_EDGE_CAPACITY
from src.core.exceptions import GraphError
from src.core.validators import validate_source_sink
from src.data import get_preset_names, load_preset
from src.data.presets import PRESET_INITIAL, PRESET_MOD_1, PRESET_MOD_2
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
    st.session_state.modification_error = None
    st.session_state.modification_success = None
    _recalculate()


def _on_scenario_change() -> None:
    """Handle scenario dropdown changes cleanly via Streamlit callback."""
    _load_scenario(st.session_state.scenario_select)


def _on_reset_scenario() -> None:
    """Reset the active scenario via callback before widgets are instantiated."""
    _load_scenario(st.session_state.selected_preset)


def _init_session_state() -> None:
    """Initialize Streamlit session state with the default network scenario."""
    if "graph" not in st.session_state:
        default_preset = get_preset_names()[0]
        st.session_state.scenario_select = default_preset
        _load_scenario(default_preset)


def _render_toggle_route_section() -> None:
    """Render sidebar controls to enable or disable any existing route."""
    graph = st.session_state.graph
    edges = graph.get_edges(only_active=False)
    if not edges:
        st.info("No routes available in the current network.")
        return

    edge_keys = [(edge.u, edge.v) for edge in edges]

    def _format_toggle_label(key: tuple[str, str]) -> str:
        edge = graph.get_edge(key[0], key[1])
        status = "Active" if edge and edge.active else "Disabled"
        cap = edge.capacity if edge else 0
        return f"{key[0]} → {key[1]} (cap: {cap}, {status})"

    selected_key = st.selectbox(
        "Select route",
        options=edge_keys,
        format_func=_format_toggle_label,
        key="toggle_route_select",
    )
    selected_edge = graph.get_edge(selected_key[0], selected_key[1])
    if selected_edge is None:
        return

    action_label = "Disable Route" if selected_edge.active else "Enable Route"
    if st.button(action_label, key="toggle_route_btn", use_container_width=True):
        try:
            new_state = not selected_edge.active
            graph.toggle_edge(selected_edge.u, selected_edge.v, active=new_state)
            _recalculate()
            state_text = "enabled" if new_state else "disabled"
            st.session_state.modification_error = None
            st.session_state.modification_success = (
                f"Route ({selected_edge.u} → {selected_edge.v}) {state_text}."
            )
            st.rerun()
        except GraphError as exc:
            st.session_state.modification_error = str(exc)
            st.session_state.modification_success = None


def _render_modify_capacity_section() -> None:
    """Render sidebar controls to modify the capacity (1..12) of an existing route."""
    graph = st.session_state.graph
    edges = graph.get_edges(only_active=False)
    if not edges:
        st.info("No routes available in the current network.")
        return

    edge_keys = [(edge.u, edge.v) for edge in edges]

    def _format_capacity_label(key: tuple[str, str]) -> str:
        edge = graph.get_edge(key[0], key[1])
        cap = edge.capacity if edge else 0
        return f"{key[0]} → {key[1]} (current: {cap})"

    selected_key = st.selectbox(
        "Select route",
        options=edge_keys,
        format_func=_format_capacity_label,
        key="capacity_route_select",
    )
    selected_edge = graph.get_edge(selected_key[0], selected_key[1])
    if selected_edge is None:
        return

    new_cap = st.slider(
        "New capacity (pkg/h)",
        min_value=MIN_EDGE_CAPACITY,
        max_value=MAX_EDGE_CAPACITY,
        value=selected_edge.capacity,
        step=1,
        key=f"cap_slider_{selected_edge.u}_{selected_edge.v}_{selected_edge.capacity}",
    )

    if st.button("Update Capacity", key="update_cap_btn", use_container_width=True):
        try:
            graph.update_capacity(selected_edge.u, selected_edge.v, int(new_cap))
            _recalculate()
            st.session_state.modification_error = None
            st.session_state.modification_success = (
                f"Updated capacity of ({selected_edge.u} → {selected_edge.v}) "
                f"to {new_cap} pkg/h."
            )
            st.rerun()
        except GraphError as exc:
            st.session_state.modification_error = str(exc)
            st.session_state.modification_success = None


def _render_add_route_section() -> None:
    """Render sidebar form to add a new directed route (u, v) with capacity validation."""
    graph = st.session_state.graph
    vertices = graph.get_vertices()

    with st.form("add_route_form"):
        origin_u = st.selectbox("Origin (u)", options=vertices, key="add_route_u")
        dest_v = st.selectbox("Destination (v)", options=vertices, key="add_route_v")
        capacity = st.slider(
            "Capacity (pkg/h)",
            min_value=MIN_EDGE_CAPACITY,
            max_value=MAX_EDGE_CAPACITY,
            value=5,
            step=1,
            key="add_route_cap",
        )
        submitted = st.form_submit_button("Add Route", use_container_width=True)
        if submitted:
            try:
                graph.add_edge(origin_u, dest_v, int(capacity))
                _recalculate()
                st.session_state.modification_error = None
                st.session_state.modification_success = (
                    f"Added route ({origin_u} → {dest_v}) with capacity {capacity} pkg/h."
                )
                st.rerun()
            except GraphError as exc:
                st.session_state.modification_error = str(exc)
                st.session_state.modification_success = None


def _render_modification_controls() -> None:
    """Render live network modification forms and validation feedback in the sidebar."""
    st.sidebar.divider()
    st.sidebar.subheader("Live Network Editor")

    with st.sidebar.expander("Enable / Disable Route", expanded=False):
        _render_toggle_route_section()

    with st.sidebar.expander("Modify Route Capacity", expanded=False):
        _render_modify_capacity_section()

    with st.sidebar.expander("Add New Route", expanded=False):
        _render_add_route_section()

    if st.session_state.get("modification_error"):
        st.sidebar.error(st.session_state.modification_error)
    elif st.session_state.get("modification_success"):
        st.sidebar.success(st.session_state.modification_success)

    st.sidebar.button(
        "Reset Scenario",
        key="reset_scenario_btn",
        use_container_width=True,
        on_click=_on_reset_scenario,
    )


def _render_sidebar() -> None:
    """Render scenario selector, source/sink form, and live network editor."""
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

    _render_modification_controls()


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


def _render_edges_table() -> None:
    """Render the edge flow/residual/min-cut table and Edmonds-Karp iteration log."""
    graph = st.session_state.graph
    flow_result = st.session_state.flow_result
    cut_result = st.session_state.cut_result

    if not flow_result or not cut_result:
        st.info("Select a valid source and sink with at least 2 distinct paths to view route results.")
        return

    flows = flow_result["flows"]
    residual = flow_result["residual"]
    cut_edge_set = {(u, v) for u, v, _ in cut_result["cut_edges"]}

    rows: list[dict] = []
    for edge in graph.get_edges(only_active=False):
        key = (edge.u, edge.v)
        flow = flows.get(key, 0)
        res_cap = residual[edge.u][edge.v] if edge.active else 0
        rows.append(
            {
                "Route (u → v)": f"{edge.u} → {edge.v}",
                "Status": "Active" if edge.active else "Disabled",
                "Flow x(u, v)": flow,
                "Capacity c(u, v)": edge.capacity,
                "Residual Capacity": res_cap,
                "Min Cut (S → T)": "Yes" if key in cut_edge_set else "No",
            }
        )

    st.subheader("Route Flow and Residual Capacity")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    iterations = flow_result.get("iterations", [])
    with st.expander(f"Edmonds-Karp Augmenting Paths ({len(iterations)} iterations)", expanded=False):
        if not iterations:
            st.info("No augmenting paths were found (max flow is 0).")
        else:
            iter_rows: list[dict] = []
            cumulative = 0
            for item in iterations:
                cumulative += item["bottleneck"]
                iter_rows.append(
                    {
                        "Iteration": item["iteration"],
                        "Augmenting Path": " → ".join(item["path"]),
                        "Bottleneck (Δ)": item["bottleneck"],
                        "Cumulative Flow": cumulative,
                    }
                )
            st.dataframe(iter_rows, use_container_width=True, hide_index=True)


def _render_verification_view() -> None:
    """Render mathematical optimality checks and flow conservation table per intermediate vertex."""
    graph = st.session_state.graph
    verification = st.session_state.verification_result

    if not verification:
        st.info("Select a valid source and sink with at least 2 distinct paths to view verification.")
        return

    st.subheader("Mathematical Optimality Verification")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Capacity Constraints",
        "PASS" if verification["capacity_ok"] else "FAIL",
        delta="0 <= x(u, v) <= c(u, v)",
        delta_color="off",
    )
    col2.metric(
        "Flow Conservation",
        "PASS" if verification["conservation_ok"] else "FAIL",
        delta="Inflow = Outflow (v ∈ V \\ {s, t})",
        delta_color="off",
    )
    col3.metric(
        "Strong Duality",
        "PASS" if verification["duality_ok"] else "FAIL",
        delta=f"|x| = {verification['max_flow']} vs c(S, T) = {verification['min_cut_capacity']}",
        delta_color="off",
    )

    st.markdown("#### Flow Conservation at Intermediate Vertices")
    conservation_rows: list[dict] = []
    for item in verification["conservation_details"]:
        v_id = item["vertex"]
        label = graph.vertices[v_id].label if v_id in graph.vertices else ""
        conservation_rows.append(
            {
                "Vertex (v)": v_id,
                "Center": label or v_id,
                "Inflow Σ x(u, v)": item["in_flow"],
                "Outflow Σ x(v, w)": item["out_flow"],
                "Balance (In - Out)": item["in_flow"] - item["out_flow"],
                "Check": "OK" if item["ok"] else "FAIL",
            }
        )
    st.dataframe(conservation_rows, use_container_width=True, hide_index=True)

    with st.expander("Capacity Constraint Audit per Route", expanded=False):
        cap_rows: list[dict] = []
        for item in verification["capacity_details"]:
            u, v = item["edge"]
            cap_rows.append(
                {
                    "Route (u → v)": f"{u} → {v}",
                    "Status": "Active" if item["active"] else "Disabled",
                    "Flow x(u, v)": item["flow"],
                    "Capacity c(u, v)": item["capacity"],
                    "Check": "OK" if item["ok"] else "FAIL",
                }
            )
        st.dataframe(cap_rows, use_container_width=True, hide_index=True)


def _compute_comparison_data() -> list[dict]:
    """Run max-flow, min-cut, and optimality verification on the three main configurations."""
    scenarios = [
        (PRESET_INITIAL, "Base network (|V|=10, |E|=18)"),
        (PRESET_MOD_1, "Disable (D → G); reduce (E → H) from 6 to 3"),
        (PRESET_MOD_2, "Add (E → T) with cap 6; increase (H → T) from 8 to 11"),
    ]
    results: list[dict] = []
    base_max_flow: int | None = None

    for preset_name, description in scenarios:
        g, s, t = load_preset(preset_name)
        flow_res = edmonds_karp(g, s, t)
        cut_res = find_min_cut(g, flow_res["residual"], s, t)
        ver_res = verify_optimality(
            g,
            flow_res["flows"],
            flow_res["max_flow"],
            cut_res["capacity"],
            s,
            t,
        )
        if base_max_flow is None:
            base_max_flow = flow_res["max_flow"]

        delta = flow_res["max_flow"] - base_max_flow
        results.append(
            {
                "name": preset_name,
                "description": description,
                "vertices": len(g.get_vertices()),
                "active_edges": len(g.get_edges(only_active=True)),
                "total_edges": len(g.get_edges(only_active=False)),
                "max_flow": flow_res["max_flow"],
                "delta": delta,
                "min_cut_capacity": cut_res["capacity"],
                "S": cut_res["S"],
                "T": cut_res["T"],
                "cut_edges": cut_res["cut_edges"],
                "iterations": len(flow_res["iterations"]),
                "is_optimal": ver_res["is_optimal"],
            }
        )

    return results


def _render_comparison_view() -> None:
    """Render side-by-side comparison of Main Network, Modification 1, and Modification 2."""
    st.subheader("Configuration Comparison (Main Network vs. Modifications)")
    results = _compute_comparison_data()

    cols = st.columns(len(results))
    for col, item in zip(cols, results):
        with col:
            st.markdown(f"#### {item['name']}")
            st.caption(item["description"])
            delta_str = (
                "Baseline"
                if item["name"] == PRESET_INITIAL
                else f"{item['delta']:+d} pkg/h vs Initial"
            )
            delta_color = "off" if item["name"] == PRESET_INITIAL else "normal"
            st.metric(
                "Max Flow |x|",
                f"{item['max_flow']} pkg/h",
                delta=delta_str,
                delta_color=delta_color,
            )
            st.metric("Min Cut c(S, T)", f"{item['min_cut_capacity']} pkg/h")
            st.markdown(
                f"**Active Routes:** `{item['active_edges']} / {item['total_edges']}`  \n"
                f"**Set S:** `{{{', '.join(item['S'])}}}`  \n"
                f"**Set T:** `{{{', '.join(item['T'])}}}`  \n"
                f"**Cut Edges:** `{', '.join(f'{u} → {v} ({c})' for u, v, c in item['cut_edges'])}`  \n"
                f"**Optimality:** `{'Verified' if item['is_optimal'] else 'Failed'}`"
            )

    st.divider()
    st.markdown("#### Side-by-Side Summary Table")
    summary_rows = [
        {
            "Configuration": item["name"],
            "Vertices |V|": item["vertices"],
            "Routes (Active / Total)": f"{item['active_edges']} / {item['total_edges']}",
            "Max Flow |x|": item["max_flow"],
            "Delta vs Initial": "0 (base)" if item["name"] == PRESET_INITIAL else f"{item['delta']:+d}",
            "Min Cut c(S, T)": item["min_cut_capacity"],
            "Partition S": "{" + ", ".join(item["S"]) + "}",
            "Partition T": "{" + ", ".join(item["T"]) + "}",
            "Cut Edges (S → T)": ", ".join(f"{u}→{v}({c})" for u, v, c in item["cut_edges"]),
            "Iterations": item["iterations"],
            "Optimality": "Verified" if item["is_optimal"] else "Failed",
        }
        for item in results
    ]
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)


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

    tab_graph, tab_routes, tab_verify, tab_compare = st.tabs(
        [
            "Network Graph",
            "Routes & Iterations",
            "Optimality Verification",
            "Scenario Comparison",
        ]
    )

    with tab_graph:
        _render_network_view()
    with tab_routes:
        _render_edges_table()
    with tab_verify:
        _render_verification_view()
    with tab_compare:
        _render_comparison_view()


if __name__ == "__main__":
    main()
