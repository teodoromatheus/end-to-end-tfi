# Example Functions

Simple entry-level functions that do cool things with realtime and static GTFS data.

Functions are organized by data source:
1. **Static Data Only** - Functions that use only static GTFS schedule data
2. **Real-Time Data Only** - Functions that use only real-time GTFS-RT data
3. **Both Static and Real-Time** - Functions that combine both data sources

## Directory Contents

This directory contains the following files, each serving a specific purpose:

### Core Implementation Files

#### **`example_functions.py`**
The main module containing all 10 example functions for working with GTFS data. This is the primary implementation file that provides:

- **Purpose**: Core library of functions for querying and analyzing GTFS transit data
- **Functionality**: 
  - Functions for querying bus stops and routes
  - Real-time arrival data processing
  - Scheduled vs real-time comparisons
  - Data analysis utilities (peak hours, delays, cancellations)
  - Stop search and information retrieval

- **Function Organization**:
  - **Static Data Only**:
    1. `find_busiest_stops()` - Find the busiest stops from a provided list based on arrival counts
    2. `find_peak_hours()` - Find peak hours when most buses are scheduled to arrive
    3. `search_stops_by_name()` - Search for stops by name (case-insensitive partial match)
  
  - **Real-Time Data Only**:
    4. `get_live_data_dataframe()` - Get live arrival data as a pandas DataFrame for analysis
    5. `find_cancelled_trips()` - Find trips that have been cancelled in the real-time feed
  
  - **Both Static and Real-Time**:
    6. `get_next_buses_at_stop()` - Get next N buses arriving at a specific stop
    7. `compare_scheduled_vs_realtime()` - Compare scheduled vs real-time arrivals for delay analysis
    8. `find_routes_at_stop()` - Find all unique routes serving a specific stop
    9. `find_most_delayed_routes()` - Find routes with the most delays across provided stops
    10. `get_stop_info()` - Get comprehensive information about a specific stop

- **Dependencies**: 
  - `gtfs` module (from parent directory)
  - `data_utils` module (from parent directory)
  - `settings` module (from parent directory)
  - `pandas`, `datetime`, `collections`

- **Documentation**: Each function includes detailed docstrings with:
  - Parameter descriptions
  - Return value descriptions
  - Usage examples

#### **`__init__.py`**
Package initialization file that makes `example_functions` a proper Python package.

- **Purpose**: Enables the directory to be imported as a Python package
- **Functionality**:
  - Exports all 10 functions from `example_functions.py` for easy importing
  - Defines `__all__` to specify the public API
  - Allows importing functions directly without specifying the submodule
  - Functions are organized by data source in the imports

- **Usage Example**:
  ```python
  from example_functions import get_next_buses_at_stop, find_busiest_stops
  # Instead of: from example_functions.example_functions import get_next_buses_at_stop
  ```

- **Dependencies**: Only imports from `example_functions.py`

### Testing Files

#### **`test_example_functions.py`**
Comprehensive test script that validates all functions in `example_functions.py`.

- **Purpose**: Automated testing suite for all example functions
- **Functionality**:
  - Tests each of the 10 functions with example data
  - Tests are organized by data source (Static Only, Real-Time Only, Both)
  - Uses predefined test stop numbers: `["1508", "7868"]`
  - Loads API key from `local_settings.py` (in parent directory) or environment variables
  - Provides detailed output showing function results
  - Generates a test summary report (passed/failed/skipped counts)
  - Handles errors gracefully with full traceback information
  - Exits with appropriate exit codes (0 for success, 1 for failure)

- **Test Process**:
  1. Loads API key from `local_settings.py` or environment
  2. Imports all functions from `example_functions.example_functions`
  3. Tests each function sequentially, organized by data source
  4. Prints formatted results for each test
  5. Generates final summary report

- **Dependencies**:
  - Imports all functions from `example_functions.example_functions`
  - Requires `local_settings.py` in parent directory with `API_KEY` defined
  - Uses standard library: `sys`, `traceback`, `os`, `pathlib`, `datetime`

### Utility/Example Files

#### **`real_time.py`**
Example/utility script demonstrating how to use the underlying `data_utils` module directly.

- **Purpose**: Standalone example script for understanding the data structure
- **Functionality**:
  - Shows how to fetch live data using `data_utils.get_live_data()`
  - Demonstrates the structure of live data responses
  - Provides examples of working with stop IDs and arrival data
  - Prints formatted JSON output of arrival data

- **Usage**: Can be run directly to see example data:
  ```bash
  python example_functions/real_time.py
  ```

- **Dependencies**:
  - `settings` module
  - `local_settings` module (for API_KEY)
  - `data_utils` module
  - `pandas`, `json`, `logging`

- **Note**: This is a standalone example script and is **not imported or used by other files** in this directory. It serves as a reference for understanding the raw data format that the example functions work with.

## File Relationships

```
example_functions/
├── example_functions.py          (Core implementation - used by all)
├── __init__.py                    (Package wrapper - enables imports)
├── test_example_functions.py      (Tests example_functions.py)
├── real_time.py                   (Standalone example - not used by others)
└── README.md                      (This file)
```

**Dependency Flow**:
- `__init__.py` → imports from `example_functions.py`
- `test_example_functions.py` → imports from `example_functions.example_functions`
- `real_time.py` → standalone, no dependencies on other files in this directory

## Data Sources: Static GTFS vs Real-Time API

The example functions combine two types of data sources to provide comprehensive transit information. Functions are organized by which data sources they use:

### Static GTFS Data

**Location**: Stored in the `data/` directory (parent directory) as GTFS text files:
- `routes.txt` - Route information (route names, agencies)
- `stops.txt` - Stop locations and names
- `stop_times.txt` - Scheduled arrival/departure times
- `trips.txt` - Trip information (route associations, headsigns)
- `calendar.txt` - Service schedules (which days routes operate)
- `calendar_dates.txt` - Service exceptions (holidays, special dates)
- `agency.txt` - Transit agency information

**How it's loaded**:
- The `gtfs.GTFS` class loads static data via `load_static()` method
- Data is cached in memory/Redis for fast access
- Static data provides the baseline schedule information

**Where it's used**:
- **All functions** that use the `gtfs.GTFS` class rely on static data for:
  - Scheduled arrival times
  - Route and stop information
  - Service calendar (which trips run on which days)
  - Stop names and locations
  - Route-to-stop mappings

**Example functions using only static data**:
- `find_busiest_stops()` - Uses static data to count scheduled arrivals per stop
- `find_peak_hours()` - Uses static data to count scheduled arrivals by hour
- `search_stops_by_name()` - Uses static data to search stop names

### Real-Time GTFS-RT API

**Location**: Fetched from the GTFS-RT (Real-Time) API endpoint:
- **API URL**: `settings.GTFS_LIVE_URL` (default: `https://api.nationaltransport.ie/gtfsr/v2/TripUpdates`)
- **Authentication**: Requires API key (set in `local_settings.py` as `API_KEY`)

**How it's accessed**:
There are two ways the functions access real-time data:

1. **Via GTFS class** (most functions):
   ```python
   gtfs_instance = gtfs.GTFS(live_url=settings.GTFS_LIVE_URL, api_key=api_key)
   gtfs_instance.refresh_live_data()  # Fetches and stores real-time updates
   ```
   - Updates the GTFS instance with live trip updates
   - Stores delays, cancellations, and trip modifications
   - Used by: `get_next_buses_at_stop()`, `compare_scheduled_vs_realtime()`, `find_most_delayed_routes()`, etc.

2. **Via data_utils module** (one function):
   ```python
   response = data_utils.get_live_data(stop_ids, api_key)
   ```
   - Directly calls the API and returns raw response
   - Used by: `get_live_data_dataframe()`

**What it provides**:
- Real-time delays (how many seconds late/early)
- Trip cancellations
- Added trips (not in static schedule)
- Modified trip information

**Where it's used**:
- **Functions using only real-time data**:
  - `get_live_data_dataframe()` - Fetches real-time data directly (API already includes scheduled times)
  - `find_cancelled_trips()` - Identifies cancelled trips from real-time feed

- **Functions that combine static + real-time**:
  - `get_next_buses_at_stop()` - Shows both scheduled and real-time arrivals
  - `compare_scheduled_vs_realtime()` - Compares scheduled vs actual times
  - `find_routes_at_stop()` - Uses static data but refreshes real-time data
  - `find_most_delayed_routes()` - Calculates delays from real-time data
  - `get_stop_info()` - Includes real-time arrival information

### How Static and Real-Time Data Are Combined

Most functions use the **GTFS class approach** which intelligently merges both data sources:

1. **Base schedule from static data**: The GTFS class reads scheduled arrival times from `stop_times.txt` and applies the service calendar to determine which trips should run.

2. **Real-time updates applied**: After calling `refresh_live_data()`, the GTFS class:
   - Applies delays to scheduled times: `real_time_arrival = scheduled_arrival + delay_seconds`
   - Filters out cancelled trips
   - Includes added trips (trips not in static schedule but present in real-time feed)

3. **Unified result**: Functions like `get_scheduled_arrivals()` return results with both:
   - `scheduled_arrival` - From static GTFS data
   - `real_time_arrival` - Calculated from static + real-time delay

**Example data flow**:
```
Static Data (routes.txt, stop_times.txt) 
    ↓
GTFS class loads and caches
    ↓
get_scheduled_arrivals() gets base schedule
    ↓
refresh_live_data() fetches real-time updates
    ↓
Real-time delays applied to scheduled times
    ↓
Result: Both scheduled_arrival and real_time_arrival in response
```

### Data Requirements

- **Static data**: Must be downloaded and present in `data/` directory
  - Download with: `python gtfs.py --download`
  - Located at: `data/routes.txt`, `data/stops.txt`, etc.

- **Real-time data**: Requires:
  - Valid API key (set in `local_settings.py` or environment)
  - Network access to the GTFS-RT API endpoint
  - API endpoint configured in `settings.GTFS_LIVE_URL`

## Quick Start

1. **Activate the virtual environment** (from project root):
   ```bash
   source factored_env/bin/activate
   ```

2. **Run all tests**:
   ```bash
   python example_functions/test_example_functions.py
   ```

3. **Use as a Python module**:
   ```python
   from example_functions import get_next_buses_at_stop
   
   buses = get_next_buses_at_stop("1508", api_key="your-key", max_results=5)
   ```

## Available Functions

### Static Data Only
1. **`find_busiest_stops`** - Find busiest stops from a list
2. **`find_peak_hours`** - Find peak hours for stops
3. **`search_stops_by_name`** - Search stops by name

### Real-Time Data Only
4. **`get_live_data_dataframe`** - Get live data as pandas DataFrame
5. **`find_cancelled_trips`** - Find cancelled trips

### Both Static and Real-Time
6. **`get_next_buses_at_stop`** - Get next N buses at a stop
7. **`compare_scheduled_vs_realtime`** - Compare delays and on-time performance
8. **`find_routes_at_stop`** - Find all routes serving a stop
9. **`find_most_delayed_routes`** - Find routes with most delays
10. **`get_stop_info`** - Get comprehensive stop information

## Documentation

For detailed usage examples:
- See function docstrings in `example_functions.py` (each function has examples)
- See test examples in `test_example_functions.py` (shows how each function is called with parameters)

## Usage as Python Module

You can import and use these functions in your Python code:

```python
from example_functions import get_next_buses_at_stop

buses = get_next_buses_at_stop("1508", api_key="your-key", max_results=5)
```

Or import multiple functions:

```python
from example_functions import (
    get_next_buses_at_stop,
    find_busiest_stops,
    compare_scheduled_vs_realtime
)
```

## Requirements

All functions require:
- An API key (set in `local_settings.py` as `API_KEY` or as environment variable)
- Access to the GTFS data files in the parent `data/` directory
- Dependencies from `requirements.txt` in the project root
- Virtual environment activated (see Quick Start)
