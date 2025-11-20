"""
Test script for example_functions.py
Tests each function one by one with example data.

Tests are organized by data source:
1. Static Data Only - Functions that use only static GTFS schedule data
2. Real-Time Data Only - Functions that use only real-time GTFS-RT data
3. Both Static and Real-Time - Functions that combine both data sources
"""

import sys
import traceback
import os
import inspect
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import modules from project root
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Try to import API key from local_settings
try:
    import local_settings
    API_KEY = local_settings.API_KEY
    print("✓ Loaded API key from local_settings")
except (ImportError, AttributeError):
    # Try to get from environment
    API_KEY = os.environ.get('API_KEY')
    if not API_KEY:
        print("⚠ Warning: No API key found. Please set API_KEY in local_settings.py or as environment variable")
        print("   Some tests may fail without an API key.")
    else:
        print("✓ Loaded API key from environment")

# Import the example functions
from example_functions.example_functions import (
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

# Import GTFS and settings to get stop numbers
import gtfs
import settings

# Get 50 stop numbers from GTFS data
def get_test_stop_numbers(api_key, num_stops=50):
    """Get the busiest stop numbers from GTFS data for the next 60 minutes"""
    try:
        gtfs_instance = gtfs.GTFS(
            live_url=settings.GTFS_LIVE_URL,
            api_key=api_key,
            rebuild_cache=False
        )
        all_stops = list(gtfs_instance.store.data.get('stop_numbers', set()))
        
        # Count arrivals per stop for the next 60 minutes
        stop_counts = []
        now = datetime.now()
        time_window = timedelta(minutes=60)
        
        for stop_number in all_stops:
            try:
                if not gtfs_instance.is_valid_stop_number(stop_number):
                    continue
                arrivals = gtfs_instance.get_scheduled_arrivals(
                    stop_number,
                    now,
                    time_window
                )
                stop_counts.append({
                    'stop_number': stop_number,
                    'arrival_count': len(arrivals)
                })
            except Exception as e:
                continue
        
        # Sort by arrival count (descending) and return top N stop numbers
        stop_counts.sort(key=lambda x: x['arrival_count'], reverse=True)
        selected_stops = [stop['stop_number'] for stop in stop_counts[:num_stops]]
        return selected_stops
    except Exception as e:
        print(f"⚠ Warning: Could not load stop numbers from GTFS data: {e}")
        # Fallback to default stops
        return ["1508", "7868"]

# Initialize test stop numbers (will be set in main() if API_KEY is available)
TEST_STOP_NUMBERS = ["1508", "7868"]  # Default fallback
TEST_STOP_IDS = [1508, 7868]  # For functions that need integer IDs


def test_function(test_number, func_name, func, *args, **kwargs):
    """Helper to test a function and print results"""
    print(f"\n{'='*70}")
    print(f"Test {test_number}: {func_name}")
    print(f"{'='*70}")
    
    # Extract and display function description and arguments from docstring
    docstring = inspect.getdoc(func)
    if docstring:
        lines = docstring.split('\n')
        description_lines = []
        args_section = []
        in_args = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines before we enter Args section
            if not stripped and not in_args:
                continue
            
            # Detect Args section start
            if stripped.startswith('Args:'):
                in_args = True
                continue
            
            # Detect end of Args section (next major section)
            if in_args and (stripped.startswith('Returns:') or stripped.startswith('Example:') or 
                           stripped.startswith('Raises:')):
                break
            
            # If we're in Args section, collect the argument lines
            if in_args:
                if stripped:
                    args_section.append(stripped)
            # Otherwise, collect description lines (before Args section)
            elif not stripped.startswith('Args:') and not stripped.startswith('Returns:') and \
                 not stripped.startswith('Example:') and not stripped.startswith('Raises:'):
                if stripped:
                    description_lines.append(stripped)
        
        # Print description
        if description_lines:
            description = ' '.join(description_lines)
            print(f"\nDescription: {description}")
        
        # Print arguments
        if args_section:
            print(f"\nArguments:")
            for arg_line in args_section:
                print(f"  {arg_line}")
    try:
        result = func(*args, **kwargs)
        print(f"✓ SUCCESS")
        print(f"\nResult type: {type(result)}")
        
        if isinstance(result, list):
            print(f"Result length: {len(result)}")
            if len(result) > 0:
                print(f"\nAll items:")
                print_result_item(result)
        elif isinstance(result, dict):
            print(f"\nResult keys: {list(result.keys())}")
            print_result_item(result)
        else:
            print(f"\nResult: {result}")
        
        return True, result
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        print(f"\nError details:")
        traceback.print_exc()
        return False, None


def print_result_item(item, indent=0):
    """Pretty print a result item"""
    indent_str = "  " * indent
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_result_item(value, indent + 1)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(item, list):
        for i, subitem in enumerate(item):  # Show all items
            print(f"{indent_str}[{i}]:")
            print_result_item(subitem, indent + 1)
    else:
        print(f"{indent_str}{item}")


def main():
    """Run all tests"""
    global TEST_STOP_NUMBERS, TEST_STOP_IDS
    
    if not API_KEY:
        print("\n⚠ No API key available. Some tests will be skipped.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Get 50 stop numbers from GTFS data if API key is available
    if API_KEY:
        print("\nLoading stop numbers from GTFS data...")
        TEST_STOP_NUMBERS = get_test_stop_numbers(API_KEY, num_stops=50)
        # Convert to integers for TEST_STOP_IDS (try to convert all, skip if conversion fails)
        TEST_STOP_IDS = []
        for stop in TEST_STOP_NUMBERS:
            try:
                TEST_STOP_IDS.append(int(stop))
            except (ValueError, TypeError):
                # Skip non-numeric stop numbers
                continue
        print(f"✓ Loaded {len(TEST_STOP_NUMBERS)} stop numbers ({len(TEST_STOP_IDS)} numeric IDs)")
    
    print("\n" + "="*70)
    print("EXAMPLE FUNCTIONS TEST SUITE")
    print("="*70)
    print(f"\nUsing {len(TEST_STOP_NUMBERS)} test stops (showing first 5): {TEST_STOP_NUMBERS[:5]}...")
    print(f"API Key: {'✓ Set' if API_KEY else '✗ Not set'}")
    
    results = {}
    
    # ========================================================================
    # STATIC DATA ONLY FUNCTIONS
    # ========================================================================
    print("\n" + "="*70)
    print("STATIC DATA ONLY FUNCTIONS")
    print("="*70)
    
    # Test 1: find_busiest_stops
    if API_KEY:
        success, result = test_function(
            1,
            "find_busiest_stops",
            find_busiest_stops,
            API_KEY,
            TEST_STOP_NUMBERS,
            top_n=5
        )
        results['find_busiest_stops'] = success
    else:
        print("\n⚠ Skipping find_busiest_stops (no API key)")
        results['find_busiest_stops'] = None
    
    # Test 2: find_peak_hours
    if API_KEY:
        success, result = test_function(
            2,
            "find_peak_hours",
            find_peak_hours,
            API_KEY,
            TEST_STOP_NUMBERS
        )
        results['find_peak_hours'] = success
    else:
        print("\n⚠ Skipping find_peak_hours (no API key)")
        results['find_peak_hours'] = None
    
    # ========================================================================
    # REAL-TIME DATA ONLY FUNCTIONS
    # ========================================================================
    print("\n" + "="*70)
    print("REAL-TIME DATA ONLY FUNCTIONS")
    print("="*70)
    
    # Test 3: get_live_data_dataframe
    # Use first 10 stop IDs to avoid overloading the API
    if API_KEY:
        test_stop_ids = TEST_STOP_IDS[:10] if len(TEST_STOP_IDS) > 10 else TEST_STOP_IDS
        success, result = test_function(
            3,
            "get_live_data_dataframe",
            get_live_data_dataframe,
            test_stop_ids,
            API_KEY
        )
        results['get_live_data_dataframe'] = success
    else:
        print("\n⚠ Skipping get_live_data_dataframe (no API key)")
        results['get_live_data_dataframe'] = None
    
    # Test 4: find_cancelled_trips
    if API_KEY:
        success, result = test_function(
            4,
            "find_cancelled_trips",
            find_cancelled_trips,
            API_KEY,
            hours_back=24
        )
        results['find_cancelled_trips'] = success
    else:
        print("\n⚠ Skipping find_cancelled_trips (no API key)")
        results['find_cancelled_trips'] = None
    
    # ========================================================================
    # BOTH STATIC AND REAL-TIME DATA FUNCTIONS
    # ========================================================================
    print("\n" + "="*70)
    print("BOTH STATIC AND REAL-TIME DATA FUNCTIONS")
    print("="*70)
    
    # Test 5: get_next_buses_at_stop
    if API_KEY:
        success, result = test_function(
            5,
            "get_next_buses_at_stop",
            get_next_buses_at_stop,
            TEST_STOP_NUMBERS[0],
            API_KEY,
            max_results=5
        )
        results['get_next_buses_at_stop'] = success
    else:
        print("\n⚠ Skipping get_next_buses_at_stop (no API key)")
        results['get_next_buses_at_stop'] = None
    
    # Test 6: compare_scheduled_vs_realtime
    if API_KEY:
        success, result = test_function(
            6,
            "compare_scheduled_vs_realtime",
            compare_scheduled_vs_realtime,
            TEST_STOP_NUMBERS[0],
            API_KEY
        )
        results['compare_scheduled_vs_realtime'] = success
    else:
        print("\n⚠ Skipping compare_scheduled_vs_realtime (no API key)")
        results['compare_scheduled_vs_realtime'] = None
    
    # Test 7: find_routes_at_stop
    if API_KEY:
        success, result = test_function(
            7,
            "find_routes_at_stop",
            find_routes_at_stop,
            TEST_STOP_NUMBERS[0],
            API_KEY
        )
        results['find_routes_at_stop'] = success
    else:
        print("\n⚠ Skipping find_routes_at_stop (no API key)")
        results['find_routes_at_stop'] = None
    
    # Test 8: find_most_delayed_routes
    if API_KEY:
        success, result = test_function(
            8,
            "find_most_delayed_routes",
            find_most_delayed_routes,
            API_KEY,
            TEST_STOP_NUMBERS,
            top_n=5
        )
        results['find_most_delayed_routes'] = success
    else:
        print("\n⚠ Skipping find_most_delayed_routes (no API key)")
        results['find_most_delayed_routes'] = None
    
    # Test 9: get_stop_info
    if API_KEY:
        success, result = test_function(
            9,
            "get_stop_info",
            get_stop_info,
            TEST_STOP_NUMBERS[0],
            API_KEY
        )
        results['get_stop_info'] = success
    else:
        print("\n⚠ Skipping get_stop_info (no API key)")
        results['get_stop_info'] = None
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for func_name, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "⊘ SKIPPED"
        print(f"{status:12} {func_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n⚠ Some tests failed. Check the output above for details.")
        sys.exit(1)
    elif passed > 0:
        print("\n✓ All executed tests passed!")
        sys.exit(0)
    else:
        print("\n⚠ No tests were executed (likely due to missing API key)")
        sys.exit(0)


if __name__ == "__main__":
    main()
