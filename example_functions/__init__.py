"""
Example Functions Package

Simple functions that use realtime and static GTFS data.

Functions are organized by data source:
1. Static Data Only - Functions that use only static GTFS schedule data
2. Real-Time Data Only - Functions that use only real-time GTFS-RT data
3. Both Static and Real-Time - Functions that combine both data sources
"""

from .example_functions import (
    # Static Data Only
    find_busiest_stops,
    find_peak_hours,
    # Real-Time Data Only
    get_live_data_dataframe,
    find_cancelled_trips,
    # Both Static and Real-Time
    get_next_buses_at_stop,
    compare_scheduled_vs_realtime,
    find_routes_at_stop,
    find_most_delayed_routes,
    get_stop_info
)

__all__ = [
    # Static Data Only
    'find_busiest_stops',
    'find_peak_hours',
    # Real-Time Data Only
    'get_live_data_dataframe',
    'find_cancelled_trips',
    # Both Static and Real-Time
    'get_next_buses_at_stop',
    'compare_scheduled_vs_realtime',
    'find_routes_at_stop',
    'find_most_delayed_routes',
    'get_stop_info'
]
