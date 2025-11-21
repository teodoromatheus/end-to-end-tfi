import folium
import pandas as pd
import random

def initialize_map():
    return folium.Map(location=[53.299132, -7.732962], zoom_start=8)


def create_trip_shape(trip_shape:dict[str, list[list[float,float]]], folium_map):

    for trip_id, coords in trip_shape.items():
        folium.PolyLine(
            locations=coords,
            #color="#{:06x}".format(random.randint(0, 0xFFFFFF)),
            color = "#0000FF",
            weight=7,
            tooltip=f"Trip Code: {trip_id}"

        ).add_to(folium_map)

    return folium_map

def create_trip_stops(df:pd.DataFrame, folium_map):

    for _,row in df.iterrows():
        folium.Marker(
            location=[row['stop_lat'],row['stop_lon']],
            tooltip=f"{row['stop_sequence']} | {row['stop_name']} - {row['stop_code']}"
    ).add_to(folium_map)
    
    return folium_map


def create_stop_markers(df_stops:pd.DataFrame, folium_map, start_stop:str, final_stop:str):
    
    START_STOP_LAT_LON = [df_stops['stop_lat'].loc[df_stops.stop_id == start_stop],df_stops['stop_lon'].loc[df_stops.stop_id == start_stop]]
    START_POINT_NAME = df_stops['stop_name'].loc[df_stops.stop_id == start_stop].values

    folium.Marker(
        location=START_STOP_LAT_LON,
        tooltip=f"Start Stop: {START_POINT_NAME} - {start_stop}",
        icon=folium.Icon(color="green", icon="pin-map")
    ).add_to(folium_map)

    FINAL_STOP_LAT_LON = [df_stops['stop_lat'].loc[df_stops.stop_id == final_stop],df_stops['stop_lon'].loc[df_stops.stop_id == final_stop]]
    FINAL_POINT_NAME = df_stops['stop_name'].loc[df_stops.stop_id == final_stop].values

    folium.Marker(
        location=FINAL_STOP_LAT_LON,
        tooltip=f"Final Stop: {FINAL_POINT_NAME} - {final_stop}",
        icon=folium.Icon(color="red", icon="pin-map-fill")
    ).add_to(folium_map)

    return folium_map