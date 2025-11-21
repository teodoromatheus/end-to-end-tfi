import pandas as pd
from pathlib import Path

# DATA_DIR = Path("../../data")
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_agency() -> pd.DataFrame:
    """
    Load GTFS agency information from agency.txt.

    Returns:
        pd.DataFrame: DataFrame containing agency metadata such as ID, name, URL, and timezone.

    Example:
        >>> agency_df = load_agency()
        >>> agency_df.head()
    """
    return pd.read_csv(
        DATA_DIR / "agency.txt",
        sep=",",
        header=0,
        dtype={
            "agency_id": "object",
            "agency_name": "object",
            "agency_url": "object",
            "agency_timezone": "object"
        }
    )


def load_calendar_dates() -> pd.DataFrame:
    """
    Load GTFS calendar exception dates from calendar_dates.txt.

    Returns:
        pd.DataFrame: DataFrame containing service exceptions with parsed dates.

    Example:
        >>> cal_dates = load_calendar_dates()
        >>> cal_dates.head()
    """
    return pd.read_csv(
        DATA_DIR / "calendar_dates.txt",
        sep=",",
        header=0,
        dtype={
            "service_id": "object",
            "exception_type": "object"
        },
        converters={
            "date": lambda x: pd.to_datetime(x, format="%Y%m%d")
        }
    )


def load_calendar() -> pd.DataFrame:
    """
    Load GTFS service availability from calendar.txt.

    Returns:
        pd.DataFrame: DataFrame containing service schedules, including weekdays and valid date ranges.

    Example:
        >>> calendar_df = load_calendar()
        >>> calendar_df.head()
    """
    return pd.read_csv(
        DATA_DIR / "calendar.txt",
        sep=",",
        header=0,
        dtype={
            "service_id": "object",
            "monday": "bool",
            "tuesday": "bool",
            "wednesday": "bool",
            "thursday": "bool",
            "friday": "bool",
            "saturday": "bool",
            "sunday": "bool"
        },
        converters={
            "start_date": lambda x: pd.to_datetime(x, format="%Y%m%d"),
            "end_date": lambda x: pd.to_datetime(x, format="%Y%m%d")
        }
    )


def load_routes() -> pd.DataFrame:
    """
    Load GTFS route information from routes.txt.

    Returns:
        pd.DataFrame: DataFrame containing details about all transit routes.

    Example:
        >>> routes = load_routes()
        >>> routes[['route_id', 'route_short_name']].head()
    """
    return pd.read_csv(
        DATA_DIR / "routes.txt",
        sep=",",
        header=0,
        dtype={
            "route_id": "object",
            "agency_id": "object",
            "route_short_name": "object",
            "route_long_name": "object",
            "route_desc": "object",
            "route_type": "object",
            "route_url": "object",
            "route_color": "object",
            "route_text_color": "object"
        }
    )


def load_shapes() -> pd.DataFrame:
    """
    Load GTFS route shapes from shapes.txt.

    Returns:
        pd.DataFrame: DataFrame containing shape points with latitude, longitude,
                      sequence order, and distance traveled.

    Example:
        >>> shapes = load_shapes()
        >>> shapes.sort_values("shape_pt_sequence").head()
    """
    return pd.read_csv(
        DATA_DIR / "shapes.txt",
        sep=",",
        header=0,
        dtype={
            "shape_id": "object",
            "shape_p_lat": "float64",
            "shape_p_lon": "float64",
            "shape_pt_sequence": "int64",
            "shape_dist_traveled": "float64"
        }
    )


def load_stop_times() -> pd.DataFrame:
    """
    Load GTFS stop-time sequences from stop_times.txt.

    Returns:
        pd.DataFrame: DataFrame containing stop sequences, pickup/drop-off types,
                      and associated trip IDs.

    Example:
        >>> stop_times = load_stop_times()
        >>> stop_times[['trip_id', 'stop_id']].head()
    """
    return pd.read_csv(
        DATA_DIR / "stop_times.txt",
        sep=",",
        header=0,
        dtype={
            "trip_id": "object",
            "stop_id": "object",
            "stop_sequence": "int64",
            "stop_headsign": "object",
            "pickup_type": "bool",
            "drop_off_type": "bool",
            "timepoint": "int64"
        }
    )


def load_stops() -> pd.DataFrame:
    """
    Load GTFS stop metadata from stops.txt.

    Returns:
        pd.DataFrame: DataFrame containing stop coordinates, names, codes, and related fields.

    Example:
        >>> stops = load_stops()
        >>> stops[['stop_id', 'stop_name']].head()
    """
    return pd.read_csv(
        DATA_DIR / "stops.txt",
        sep=",",
        header=0,
        dtype={
            "stop_id": "object",
            "stop_code": "object",
            "stop_name": "object",
            "stop_desc": "object",
            "stop_lat": "float64",
            "stop_lon": "float64",
            "zone_id": "object",
            "stop_url": "object",
            "location_type": "object",
            "parent_station": "object"
        }
    )


def load_trips() -> pd.DataFrame:
    """
    Load GTFS trip information from trips.txt.

    Returns:
        pd.DataFrame: DataFrame containing trip IDs, associated routes, shapes, headsigns, and more.

    Example:
        >>> trips = load_trips()
        >>> trips[['trip_id', 'route_id']].head()
    """
    return pd.read_csv(
        DATA_DIR / "trips.txt",
        sep=",",
        header=0,
        dtype={
            "route_id": "object",
            "service_id": "object",
            "trip_id": "object",
            "trip_headsign": "object",
            "trip_short_name": "object",
            "direction_id": "object",
            "block_id": "object",
            "shape_id": "object"
        }
    )


def load_all_data() -> dict[str, pd.DataFrame]:
    """
    Load all GTFS files into a dictionary of DataFrames.

    Returns:
        dict[str, pd.DataFrame]: A dictionary mapping GTFS component names
        (e.g., "routes", "stops", "trips") to their respective DataFrames.

    Example:
        >>> data = load_all_data()
        >>> data.keys()
        dict_keys(['agency', 'calendar_dates', 'calendar', 'routes',
                   'shapes', 'stop_times', 'stops', 'trips'])
    """
    return {
        "agency": load_agency(),
        "calendar_dates": load_calendar_dates(),
        "calendar": load_calendar(),
        "routes": load_routes(),
        "shapes": load_shapes(),
        "stop_times": load_stop_times(),
        "stops": load_stops(),
        "trips": load_trips(),
    }