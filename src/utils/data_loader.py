import pandas as pd
from pathlib import Path

# DATA_DIR = Path("../../data")
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_agency() -> pd.DataFrame:
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
    Convenience function to load all GTFS text files at once.
    Returns a dict of DataFrames.

    You can access the dataframe by its name:
        data_loaded = load_gtfs_data()
        df_agency = data_loaded["agency"]
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