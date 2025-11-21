# import os, sys
# sys.path.append(os.path.abspath(".."))

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import folium
from utils.data_loader import load_trips, load_stop_times, load_stops, load_shapes
from components.folium_components import initialize_map, create_trip_shape, create_trip_stops
from utils.data_processing import get_trip_shapes, get_trip_stops

# Load Dataframes and cache them to optimize
@st.cache_data
def load_data():
    return (
        load_trips(),
        load_stop_times(),
        load_stops(),
        load_shapes()
    )

df_trips, df_stop_times, df_stops, df_shapes = load_data()


# Initialize session_state for trip_id selection
if 'trip_id_session' not in st.session_state:
    st.session_state.trip_id_session = '3001_1'


# Add SelectBox to use as a filter
with st.sidebar:
    trip_id_selected = st.selectbox(
        "Select the Trip ID below",
        options=df_trips['trip_id'].unique().tolist()
    )


# Update trip_id variable only if the user choose another trip_id in the SelectBox
if trip_id_selected != st.session_state.trip_id_session:
    st.session_state.trip_id_session = trip_id_selected


# Update Routes about the trip_id selected
trip_shape = get_trip_shapes(df_trips=df_trips, df_shapes=df_shapes, trip_id_list=[st.session_state.trip_id_session])
df_trip_stops = get_trip_stops(df_trips=df_trips, df_stop_times=df_stop_times, df_stops=df_stops, list_trips_id=[st.session_state.trip_id_session])

map_trip = initialize_map()
map_trip = create_trip_shape(trip_shape=trip_shape, folium_map=map_trip)
map_trip = create_trip_stops(df=df_trip_stops, folium_map=map_trip)

# Write a title
st.write(f"# Trip Route for {trip_id_selected}")

# Write the map with trip_id route/markers
st_folium(map_trip, width=1200, height=700)