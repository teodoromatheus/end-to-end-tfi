import pandas as pd
from typing import Optional
import datetime

def get_trip_shapes(df_trips:pd.DataFrame, df_shapes:pd.DataFrame, trip_id_list:Optional[list[str]]=None) -> dict[str, list[list[float,float]]]:
    """
    Build a dictionary of trip shapes for the given trips.

    Each trip ID is mapped to a list of coordinate pairs representing the ordered
    shape path associated with that trip.

    Args:
        df_trips: DataFrame containing trip metadata, including shape_id.
        df_shapes: DataFrame containing shape points with latitude, longitude,
                   and sequence information.
        trip_id_list: Optional list of trip IDs to filter. If None, all trips
                      in df_trips are processed.

    Returns:
        dict[str, list[list[float, float]]]: Dictionary mapping each trip_id to
        a list of [lat, lon] pairs in the correct drawing order.

    Example:
        >>> shapes = get_trip_shapes(df_trips, df_shapes, ["TRIP001", "TRIP002"])
        >>> shapes["TRIP001"][:3]
        [[53.301, -7.73], [53.302, -7.731], [53.303, -7.732]]
    """

    if trip_id_list is not None:
        df_trip_shape = (
            df_trips
            .loc[df_trips.trip_id.isin(trip_id_list)]
            .merge(
                df_shapes[['shape_pt_lat','shape_pt_lon','shape_pt_sequence','shape_id']],
                on='shape_id',
                how='inner'
            )
            .sort_values(by=['trip_id','shape_pt_sequence'])
        )

    else:
        df_trip_shape = (
            df_trips
            .merge(
                df_shapes[['shape_pt_lat','shape_pt_lon','shape_pt_sequence','shape_id']],
                on='shape_id',
                how='inner'
            )
            .sort_values(by=['trip_id','shape_pt_sequence'])
        )
    
    shape_dict = {}
    for trip_id in trip_id_list:
        lat_lon = df_trip_shape[['shape_pt_lat','shape_pt_lon']].loc[df_trip_shape.trip_id == trip_id].values.tolist()
        shape_dict[trip_id] = lat_lon

    return shape_dict



def get_trip_stops(df_trips:pd.DataFrame, df_stop_times:pd.DataFrame, df_stops:pd.DataFrame, list_trips_id:list[str]) -> pd.DataFrame:
    """
    Retrieve all stops for the specified trip IDs, including coordinates and sequence.

    Args:
        df_trips: DataFrame containing trip IDs and associated metadata.
        df_stop_times: DataFrame containing stop ordering and stop IDs for each trip.
        df_stops: DataFrame containing stop names, coordinates, and codes.
        list_trips_id: List of trip IDs to retrieve stop information for.

    Returns:
        pd.DataFrame: DataFrame containing stop metadata for each trip, ordered by
        stop sequence.

    Example:
        >>> trip_stops = get_trip_stops(df_trips, df_stop_times, df_stops, ["TRIP001"])
        >>> trip_stops.head()
    """
    return (
        df_trips
        .loc[df_trips.trip_id.isin(list_trips_id)]
        .merge(
            df_stop_times[['trip_id','stop_id','stop_sequence','pickup_type','drop_off_type']],
            on='trip_id',
            how='inner'
        )
        .merge(
            df_stops[['stop_id','stop_name','stop_lat','stop_lon','stop_code']],
            on='stop_id',
            how='inner'
        )
        [['trip_id', 'stop_id', 'stop_code', 'stop_name', 'stop_sequence', 'stop_lat', 'stop_lon']]
    )


def search_trips_availables(df_trips:pd.DataFrame, df_stop_times:pd.DataFrame, df_calendar:pd.DataFrame, start_stop:str, final_stop:str, date:datetime.date) -> list[str]: 
    """
    Search for trip IDs available between two stops on a given date.

    The function finds trips that visit both the start and final stops in the
    correct order, and then filters them based on service availability defined
    in the calendar table for the selected date.

    Args:
        df_trips: DataFrame containing trip information.
        df_stop_times: DataFrame containing stop sequences for all trips.
        df_calendar: DataFrame defining which services run on which days.
        start_stop: Stop ID where the journey begins.
        final_stop: Stop ID where the journey ends.
        date: Date object used to check service availability.

    Returns:
        list[str]: List of trip IDs that are valid for the given date and stop pair.

    Example:
        >>> trips = search_trips_availables(df_trips, df_stop_times, df_calendar,
        ...                                 "1508", "7868", datetime.date(2024, 5, 12))
        >>> trips
        ['TRIP001', 'TRIP017']
    """
    name_of_date = date.strftime("%A").lower()
    
    list_trips = (
        df_stop_times
        .query("stop_id == @start_stop or stop_id == @final_stop")
        .assign(rank_column=lambda x: x.groupby('trip_id')['stop_sequence'].rank(method='first'))
        .query("rank_column == 2 and stop_id == @final_stop")
        ['trip_id']
        .drop_duplicates()
    ).to_list()

    trips_available = (
        df_trips
        .loc[df_trips.trip_id.isin(list_trips)]
        .merge(
            df_calendar,
            on='service_id',
            how='inner'
        )
        .query(f"@date >= start_date and @date <= end_date and {name_of_date} == True")
        ['trip_id']
        .drop_duplicates()
    ).to_list()

    return trips_available



def get_trips_if_exists(df_trips:pd.DataFrame, df_stop_times:pd.DataFrame, df_calendar:pd.DataFrame, start_stop:str, final_stop:str, date:datetime.date) -> list[str]:
    """
    Return all dates on which trips between two stops are available.

    Unlike search_trips_availables(), this function returns all calendar dates
    where the route between the stop pair *could* be taken, not just whether
    the trip exists on a specific date.

    Args:
        df_trips: DataFrame containing trip metadata.
        df_stop_times: DataFrame containing stop ordering information.
        df_calendar: DataFrame defining weekday-based service availability.
        start_stop: Stop ID where the trip begins.
        final_stop: Stop ID where the trip ends.
        date: The reference date (used only for weekday matching logic).

    Returns:
        list[str]: List of date strings (YYYY-MM-DD) where at least one matching
        trip is scheduled.

    Example:
        >>> date_list = get_trips_if_exists(df_trips, df_stop_times, df_calendar,
        ...                                 "1508", "7868", datetime.date(2024, 5, 12))
        >>> date_list[:5]
        ['2024-05-10', '2024-05-11', '2024-05-12', ...]
    """
    list_trips = (
        df_stop_times
        .query("stop_id == @start_stop or stop_id == @final_stop")
        .assign(rank_column=lambda x: x.groupby('trip_id')['stop_sequence'].rank(method='first'))
        .query("rank_column == 2 and stop_id == @final_stop")
        ['trip_id']
        .drop_duplicates()
    ).to_list()

    if list_trips == []:
        return []

    else:
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        dates_for_trips = (
            df_trips
            .loc[df_trips.trip_id.isin(list_trips)]
            .merge(
                df_calendar,
                on='service_id',
                how='inner'
            )
            [['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date']]
            .assign(days_available=lambda df: df.apply(lambda x: [col for col in weekdays if x[col] == 1],axis=1))
        )

        dates_for_trips['days'] = dates_for_trips.apply(lambda x: pd.date_range(x.start_date,x.end_date,freq='D'),axis=1)
        df_exploded = dates_for_trips.explode('days')

        df_exploded = df_exploded[
            df_exploded.apply(
                lambda row: row.days.strftime("%A").lower() in row.days_available,
                axis=1
            )
        ]

        return df_exploded['days'].astype(str).drop_duplicates().to_list()