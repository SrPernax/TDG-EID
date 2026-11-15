"""
Entry point: app.py
Owner: Member 3
Description:
    Interactive Streamlit application to select source/sink nodes, execute
    the maximum flow and minimum cut calculations, and perform runtime network
    modifications (disable route, update capacity, add connection) without
    editing the source code.
"""

import streamlit as st


def main():
    st.set_page_config(
        page_title="Package Distribution Network Simulator - INFO1158",
        layout="wide",
    )
    st.title("Package Distribution Network Simulator")
    st.info("Base project structure initialized. Module integration pending.")


if __name__ == "__main__":
    main()
