"""
Simple entry-level functions that do cool things with realtime and static GTFS data.

This module provides easy-to-use functions for exploring and analyzing
public transit data, combining both static schedule information and real-time updates.

Functions are organized by data source:
1. Static Data Only - Functions that use only static GTFS schedule data
2. Real-Time Data Only - Functions that use only real-time GTFS-RT data
3. Both Static and Real-Time - Functions that combine both data sources
"""

import datetime
from typing import List, Dict, Optional
import pandas as pd
from collections import Counter, defaultdict

import gtfs
import data_utils
import settings


# ============================================================================
# STATIC DATA ONLY FUNCTIONS
# ============================================================================

def find_busiest_stops(api_key: str, stop_numbers: List[str], top_n: int = 10) -> List[Dict]:
    """
    Find the busiest stops from a provided list based on number of scheduled arrivals.
    
    Args:
        api_key: API key for accessing real-time data
        stop_numbers: List of stop numbers to analyze
        top_n: Number of top stops to return (default: 10)
    
    Returns:
        List of dictionaries with stop information and arrival counts
    
    Example:
        >>> busiest = find_busiest_stops("your-api-key", ["1508", "7868", "1234"], top_n=5)
        >>> for stop in busiest:
        ...     print(f"Stop {stop['stop_number']}: {stop['stop_name']} - {stop['arrival_count']} arrivals")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    # Count arrivals per stop
    stop_counts = []
    now = datetime.datetime.now()
    
    for stop_number in stop_numbers:
        try:
            if not gtfs_instance.is_valid_stop_number(stop_number):
                continue
            arrivals = gtfs_instance.get_scheduled_arrivals(
                stop_number,
                now,
                datetime.timedelta(hours=24)
            )
            stop_name = gtfs_instance.get_stop_name(stop_number)
            stop_counts.append({
                'stop_number': stop_number,
                'stop_name': stop_name,
                'arrival_count': len(arrivals)
            })
        except Exception as e:
            continue
    
    # Sort by arrival count and return top N
    stop_counts.sort(key=lambda x: x['arrival_count'], reverse=True)
    return stop_counts[:top_n]


def find_peak_hours(api_key: str, stop_numbers: List[str]) -> List[Dict]:
    """
    Find peak hours when most buses are scheduled to arrive at the given stops.
    
    Args:
        api_key: API key for accessing real-time data
        stop_numbers: List of stop numbers to analyze
    
    Returns:
        List of dictionaries with hour and arrival count
    
    Example:
        >>> peaks = find_peak_hours("your-api-key", ["1508", "7868"])
        >>> for peak in peaks[:5]:
        ...     print(f"{peak['hour']}:00 - {peak['arrival_count']} arrivals")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    now = datetime.datetime.now()
    hour_counts = Counter()
    
    for stop_number in stop_numbers:
        try:
            if not gtfs_instance.is_valid_stop_number(stop_number):
                continue
            arrivals = gtfs_instance.get_scheduled_arrivals(
                stop_number,
                now,
                datetime.timedelta(hours=24)
            )
            
            for arrival in arrivals:
                hour = arrival['scheduled_arrival'].hour
                hour_counts[hour] += 1
        except Exception as e:
            continue
    
    # Convert to list of dicts
    peak_hours = [{'hour': hour, 'arrival_count': count} 
                  for hour, count in hour_counts.most_common()]
    peak_hours.sort(key=lambda x: x['arrival_count'], reverse=True)
    
    return peak_hours


# ============================================================================
# REAL-TIME DATA ONLY FUNCTIONS
# ============================================================================

def get_live_data_dataframe(stop_ids: List[int], api_key: str) -> pd.DataFrame:
    """
    Get live arrival data as a pandas DataFrame for easy analysis.
    
    Args:
        stop_ids: List of stop IDs to query
        api_key: API key for accessing real-time data
    
    Returns:
        pandas DataFrame with arrival information
    
    Example:
        >>> df = get_live_data_dataframe([1508, 7868], "your-api-key")
        >>> print(df.head())
        >>> print(df.groupby('route')['delay_minutes'].mean())
    """
    response = data_utils.get_live_data(stop_ids, api_key)
    df = data_utils.get_df_from_live_data(response)
    
    # Add calculated columns if possible
    if 'scheduled_arrival' in df.columns and 'real_time_arrival' in df.columns:
        df['scheduled_arrival'] = pd.to_datetime(df['scheduled_arrival'])
        df['real_time_arrival'] = pd.to_datetime(df['real_time_arrival'])
        df['delay_minutes'] = (df['real_time_arrival'] - df['scheduled_arrival']).dt.total_seconds() / 60
        df['wait_time_minutes'] = (df['real_time_arrival'] - pd.Timestamp.now()).dt.total_seconds() / 60
    
    return df


def find_cancelled_trips(api_key: str, hours_back: int = 24) -> List[Dict]:
    """
    Find trips that have been cancelled in the real-time feed.
    
    Args:
        api_key: API key for accessing real-time data
        hours_back: How many hours back to check for cancellations (default: 24)
    
    Returns:
        List of dictionaries with cancelled trip information
    
    Example:
        >>> cancelled = find_cancelled_trips("your-api-key")
        >>> print(f"Found {len(cancelled)} cancelled trips")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    gtfs_instance.refresh_live_data()
    
    cancelled_trips = []
    now = datetime.datetime.now()
    cutoff_time = now.timestamp() - (hours_back * 3600)
    
    # Access the store to get cancelled trips
    # Note: This is a simplified version - actual implementation may vary
    # based on how cancellations are stored in the store
    all_trips = gtfs_instance.store.data.get('live_cancelations', {})
    
    for trip_id, cancel_timestamp in all_trips.items():
        if cancel_timestamp > cutoff_time:
            trip_info = gtfs_instance.get_trip_info(trip_id)
            if trip_info:
                cancelled_trips.append({
                    'trip_id': trip_id,
                    'route': trip_info['route'],
                    'headsign': trip_info['headsign'],
                    'cancelled_at': datetime.datetime.fromtimestamp(cancel_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return cancelled_trips


# ============================================================================
# BOTH STATIC AND REAL-TIME DATA FUNCTIONS
# ============================================================================

def get_next_buses_at_stop(stop_number: str, api_key: str, max_results: int = 5) -> List[Dict]:
    """
    Get the next N buses arriving at a specific stop.
    
    Args:
        stop_number: The stop number (as shown on the bus stop)
        api_key: API key for accessing real-time data
        max_results: Maximum number of buses to return (default: 5)
    
    Returns:
        List of dictionaries with bus arrival information
    
    Example:
        >>> buses = get_next_buses_at_stop("1508", "your-api-key")
        >>> for bus in buses:
        ...     print(f"{bus['route']} to {bus['headsign']} arriving at {bus['real_time_arrival']}")
    """
    # Initialize GTFS with static data
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    # Refresh live data
    gtfs_instance.refresh_live_data()
    
    # Get scheduled arrivals
    now = datetime.datetime.now()
    arrivals = gtfs_instance.get_scheduled_arrivals(
        stop_number, 
        now, 
        datetime.timedelta(minutes=60)
    )
    
    # Format results
    stop_name = gtfs_instance.get_stop_name(stop_number)
    results = []
    for arrival in arrivals[:max_results]:
        results.append({
            'stop_number': stop_number,
            'stop_name': stop_name,
            'route': arrival['route'],
            'headsign': arrival['headsign'],
            'agency': arrival['agency'],
            'scheduled_arrival': arrival['scheduled_arrival'].strftime('%H:%M'),
            'real_time_arrival': arrival['real_time_arrival'].strftime('%H:%M') if arrival['real_time_arrival'] else 'N/A',
            'delay_minutes': int((arrival['real_time_arrival'] - arrival['scheduled_arrival']).total_seconds() / 60) 
                if arrival['real_time_arrival'] and arrival['scheduled_arrival'] else None
        })
    
    return results


def compare_scheduled_vs_realtime(stop_number: str, api_key: str) -> Dict:
    """
    Compare scheduled vs real-time arrivals to see delays and on-time performance.
    
    Args:
        stop_number: The stop number to analyze
        api_key: API key for accessing real-time data
    
    Returns:
        Dictionary with statistics about delays and on-time performance
    
    Example:
        >>> stats = compare_scheduled_vs_realtime("1508", "your-api-key")
        >>> print(f"Average delay: {stats['avg_delay_minutes']} minutes")
        >>> print(f"On-time percentage: {stats['on_time_percentage']}%")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    gtfs_instance.refresh_live_data()
    now = datetime.datetime.now()
    arrivals = gtfs_instance.get_scheduled_arrivals(
        stop_number,
        now,
        datetime.timedelta(minutes=60)
    )
    
    delays = []
    on_time_count = 0
    total_with_realtime = 0
    
    for arrival in arrivals:
        if arrival['real_time_arrival'] and arrival['scheduled_arrival']:
            delay_seconds = (arrival['real_time_arrival'] - arrival['scheduled_arrival']).total_seconds()
            delay_minutes = delay_seconds / 60
            delays.append(delay_minutes)
            total_with_realtime += 1
            # Consider on-time if within 2 minutes of scheduled time
            if abs(delay_minutes) <= 2:
                on_time_count += 1
    
    stats = {
        'stop_number': stop_number,
        'stop_name': gtfs_instance.get_stop_name(stop_number),
        'total_arrivals': len(arrivals),
        'arrivals_with_realtime': total_with_realtime,
        'avg_delay_minutes': sum(delays) / len(delays) if delays else None,
        'max_delay_minutes': max(delays) if delays else None,
        'min_delay_minutes': min(delays) if delays else None,
        'on_time_percentage': (on_time_count / total_with_realtime * 100) if total_with_realtime > 0 else 0
    }
    
    return stats


def find_routes_at_stop(stop_number: str, api_key: str) -> List[str]:
    """
    Find all unique routes that serve a specific stop.
    
    Args:
        stop_number: The stop number to query
        api_key: API key for accessing real-time data
    
    Returns:
        List of unique route names
    
    Example:
        >>> routes = find_routes_at_stop("1508", "your-api-key")
        >>> print(f"Routes at this stop: {', '.join(routes)}")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    gtfs_instance.refresh_live_data()
    now = datetime.datetime.now()
    arrivals = gtfs_instance.get_scheduled_arrivals(
        stop_number,
        now,
        datetime.timedelta(hours=24)
    )
    
    routes = list(set([arrival['route'] for arrival in arrivals]))
    return sorted(routes)


def find_most_delayed_routes(api_key: str, stop_numbers: List[str], top_n: int = 10) -> List[Dict]:
    """
    Find routes with the most delays across provided stops.
    
    Args:
        api_key: API key for accessing real-time data
        stop_numbers: List of stop numbers to analyze
        top_n: Number of top routes to return (default: 10)
    
    Returns:
        List of dictionaries with route delay statistics
    
    Example:
        >>> delayed = find_most_delayed_routes("your-api-key", ["1508", "7868"])
        >>> for route in delayed:
        ...     print(f"{route['route']}: avg delay {route['avg_delay_minutes']} min")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    gtfs_instance.refresh_live_data()
    now = datetime.datetime.now()
    
    route_delays = defaultdict(list)
    route_stops = defaultdict(set)  # Track which stops contributed to each route
    
    # Analyze provided stops
    for stop_number in stop_numbers:
        try:
            if not gtfs_instance.is_valid_stop_number(stop_number):
                continue
            arrivals = gtfs_instance.get_scheduled_arrivals(
                stop_number,
                now,
                datetime.timedelta(minutes=60)
            )
            
            for arrival in arrivals:
                if arrival['real_time_arrival'] and arrival['scheduled_arrival']:
                    delay_minutes = (arrival['real_time_arrival'] - arrival['scheduled_arrival']).total_seconds() / 60
                    route_delays[arrival['route']].append(delay_minutes)
                    route_stops[arrival['route']].add(stop_number)
        except Exception as e:
            continue
    
    # Calculate statistics per route
    route_stats = []
    for route, delays in route_delays.items():
        route_stats.append({
            'route': route,
            'avg_delay_minutes': sum(delays) / len(delays),
            'max_delay_minutes': max(delays),
            'sample_size': len(delays),
            'stop_numbers': sorted(list(route_stops[route]))
        })
    
    route_stats.sort(key=lambda x: x['avg_delay_minutes'], reverse=True)
    return route_stats[:top_n]


def get_stop_info(stop_number: str, api_key: str) -> Dict:
    """
    Get comprehensive information about a specific stop.
    
    Args:
        stop_number: The stop number to query
        api_key: API key for accessing real-time data
    
    Returns:
        Dictionary with stop information including name, routes, and next arrivals
    
    Example:
        >>> info = get_stop_info("1508", "your-api-key")
        >>> print(f"Stop: {info['stop_name']}")
        >>> print(f"Routes: {', '.join(info['routes'])}")
    """
    gtfs_instance = gtfs.GTFS(
        live_url=settings.GTFS_LIVE_URL,
        api_key=api_key,
        rebuild_cache=False
    )
    
    gtfs_instance.refresh_live_data()
    now = datetime.datetime.now()
    arrivals = gtfs_instance.get_scheduled_arrivals(
        stop_number,
        now,
        datetime.timedelta(minutes=60)
    )
    
    routes = list(set([arrival['route'] for arrival in arrivals]))
    agencies = list(set([arrival['agency'] for arrival in arrivals]))
    
    next_arrivals = []
    for arrival in arrivals[:5]:
        next_arrivals.append({
            'stop_number': stop_number,
            'route': arrival['route'],
            'headsign': arrival['headsign'],
            'scheduled': arrival['scheduled_arrival'].strftime('%H:%M'),
            'realtime': arrival['real_time_arrival'].strftime('%H:%M') if arrival['real_time_arrival'] else 'N/A'
        })
    
    return {
        'stop_number': stop_number,
        'stop_name': gtfs_instance.get_stop_name(stop_number),
        'routes': sorted(routes),
        'agencies': sorted(agencies),
        'total_arrivals_next_hour': len(arrivals),
        'next_arrivals': next_arrivals
    }


if __name__ == "__main__":
    # Example usage
    print("Example GTFS Functions - Example Usage")
    print("=" * 50)
    
    # Note: You'll need to set your API key
    # api_key = "your-api-key-here"
    
    # Example: Get next buses at a stop
    # buses = get_next_buses_at_stop("1508", api_key, max_results=5)
    # print("\nNext 5 buses at stop 1508:")
    # for bus in buses:
    #     print(f"  {bus['route']} to {bus['headsign']} - {bus['real_time_arrival']}")
    
    print("\nImport this module and use the functions with your API key!")
    print("Example: from example_functions import get_next_buses_at_stop")
