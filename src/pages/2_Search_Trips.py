import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import datetime
import folium
from utils.data_loader import load_trips, load_stop_times, load_stops, load_shapes, load_calendar
from components.folium_components import initialize_map, create_trip_shape, create_trip_stops, create_stop_markers
from utils.data_processing import get_trip_shapes, get_trip_stops, search_trips_availables, get_trips_if_exists


@st.cache_data
def load_data():
    return (
        load_stops(),
        load_trips(),
        load_stop_times(),
        load_calendar(),
        load_shapes()
    )

df_stops, df_trips, df_stop_times, df_calendar, df_shapes = load_data()

# if 'start_stop' not in st.session_state:
#     st.session_state.start_stop = ''

# if 'final_stop' not in st.session_state:
#     st.session_state.final_stop = ''

# if 'date' not in st.session_state:
#     st.session_state.


with st.sidebar:
    start_stop = st.selectbox(
        "Select the Start Stop of your trip",
        options=df_stops['stop_id'].unique().tolist()
    )

    final_stop = st.selectbox(
        "Select the Final Stop of your trip",
        options=df_stops['stop_id'].unique().tolist()
    )

    date = st.date_input(
        "Select the date of your trip",
        datetime.date(2025,12,1)
    )


list_trips_available = search_trips_availables(df_trips=df_trips, df_calendar=df_calendar, df_stop_times=df_stop_times, start_stop=start_stop, final_stop=final_stop, date=date)
dict_trip_shape = get_trip_shapes(df_trips=df_trips, df_shapes=df_shapes, trip_id_list=list_trips_available)
list_dates_available = get_trips_if_exists(df_trips=df_trips, df_stop_times=df_stop_times, df_calendar=df_calendar, start_stop=start_stop, final_stop=final_stop, date=date)


st.write("# Select the stops and the date for your trip, then *check* the services available!!!")

if list_dates_available == []:
    st.write(f"There aren't trips that stop by these two stops selected! Try other stops.")
elif (list_dates_available != []) & (list_trips_available != []):
    st.write(f"Trips available for your preference: {list_trips_available}")
elif list_dates_available != []:
    st.write(f"For the date selected there aren't trips, but it is available at these dates below: \n {list_dates_available}")
    

map_search = initialize_map()
map_search = create_stop_markers(df_stops=df_stops, folium_map=map_search, start_stop=start_stop, final_stop=final_stop)
map_search = create_trip_shape(trip_shape=dict_trip_shape, folium_map=map_search)


st_folium(map_search, width=1200, height=700)