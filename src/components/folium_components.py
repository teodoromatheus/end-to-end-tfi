import folium
import pandas as pd
import random

def initialize_map():
    """
    Initialize a Folium map centered on a default geographic location.

    Returns:
        folium.Map: A Folium map object centered on Ireland with a preset zoom level.

    Example:
        >>> m = initialize_map()
        >>> m  # Display map in a Jupyter environment
    """
    return folium.Map(location=[53.299132, -7.732962], zoom_start=8)


def create_trip_shape(trip_shape:dict[str, list[list[float,float]]], folium_map):
    """
    Draw trip shapes (polylines) on a Folium map.

    Args:
        trip_shape: Dictionary where keys are trip IDs and values are lists of [lat, lon] coordinate pairs.
        folium_map: The Folium map object to draw the shapes onto.

    Returns:
        folium.Map: The updated map with polyline shapes added.

    Example:
        >>> shapes = {"TRIP001": [[53.1, -7.2], [53.2, -7.3]]}
        >>> m = initialize_map()
        >>> m = create_trip_shape(shapes, m)
    """

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
    """
    Add stop markers for a specific trip to a Folium map.

    Args:
        df: DataFrame containing trip stop information with columns
            ['stop_lat', 'stop_lon', 'stop_sequence', 'stop_name', 'stop_code'].
        folium_map: The Folium map to populate with stop markers.

    Returns:
        folium.Map: The map updated with markers for each stop in the trip.

    Example:
        >>> m = initialize_map()
        >>> m = create_trip_stops(df_trip_stops, m)
    """

    for _,row in df.iterrows():
        folium.Marker(
            location=[row['stop_lat'],row['stop_lon']],
            tooltip=f"{row['stop_sequence']} | {row['stop_name']} - {row['stop_code']}"
    ).add_to(folium_map)
    
    return folium_map


def create_stop_markers(df_stops:pd.DataFrame, folium_map, start_stop:str, final_stop:str):
    """
    Mark the start and final stops of a route on a Folium map.

    Args:
        df_stops: DataFrame containing stop metadata with columns such as
            ['stop_id', 'stop_lat', 'stop_lon', 'stop_name'].
        folium_map: The map onto which start and end markers will be added.
        start_stop: The stop_id for the starting stop of the journey.
        final_stop: The stop_id for the final stop of the journey.

    Returns:
        folium.Map: The updated map with start and end stop markers added.

    Example:
        >>> m = initialize_map()
        >>> m = create_stop_markers(df_stops, m, "1508", "7868")
    """
    
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