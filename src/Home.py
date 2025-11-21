import streamlit as st

st.set_page_config(
    page_title = "Ireland Transportation"
)

st.write("# Welcome to the Ireland Transportation Dashboard 🚍")

st.markdown("""
            ## Context

            This dashboard shows Ireland Public Transport information, regarding *routes*, *stop points* and even *availability*!

            On the sidebar is available two pages to access:

            1. *Trip Route*:
            Description
            
            2. *Search Trips*:
            Description         
            """)

with st.sidebar:
    st.write('##')