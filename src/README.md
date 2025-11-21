# Streamlit Application for Ireland Transport System

## 1. Table of contents

- [1. Table of contents](#1-table-of-contents)
- [2. Context](#2-context)
- [3. Topics Covered](#3-topics-covered)
- [4. Hands On](#4-hands-on)
    - [4.1 Settings and Structure](#41-settings-and-structure)
    - [4.2 Data Ingestion](#42-data-ingestion)
    - [4.3 Data Transformation](#43-data-transformation)
    - [4.4 Folium Elements](#44-folium-elements)
    - [4.5 Streamlit](#45-streamlit)


## 2. Context

This project is related to the Ireland Public Transportation System and provides data assets regarding routes, trips, stops, and even the availability of services.

This part of the project will guide you through how to work with the data assets, assuming you have already consumed the Static API and stored the `.txt` files in the `data` folder. The goal is to build a dashboard using Streamlit to display geospatial analysis. In the [Hands On](#4-hands-on) section, you will find guidance and useful advice.

## 3. Topics Covered

1. *Python Fundamentals*: Work with different variable types, functions, and learn how to organize your project.
2. *Pandas*: Handle dataframes for ingestion and transformation.
3. *Folium*: Create geospatial analysis using Folium visual elements.
4. *Streamlit*: Build an interactive dashboard to display geospatial insights.

## 4. Hands On

### 4.1 Settings and Structure

As we mentioned, the goal of this part is to create a dashboard using Streamlit. Check out the reference project running this command below:

```bash
streamlit run src/Home.py
```

Now, let's understand the folder's structure and the objective of each `.py` file.

```markdown
src/
│──components/
│      folium_components.py (functions to build Folium Element and add into maps)
│
│──pages/
│       1_Trip_Route.py     (one page of Streamlit App to seek trips routes and stops)
│       2_Search_Trips.py   (second page of Streamlit App to look for trips which stop by your start point and end point)
│
│──utils/
│       data_loader.py      (functions to convert txt files to Dataframe)
│       data_processing.py  (functions to collect specific pieces of information and integrate them with Folium components)
│
└──Home.py
```

### 4.2 Data Ingestion

The data assets we requested from the API are stored as `.txt` files. To make data handling easier, we should convert them into Pandas dataframes.

> #### How to do that?

First, import the pandas library:
```python
import pandas as pd
```

then, we could use `pd.read_csv()` to convert from `.txt` file into pandas dataframe.
```python
df_agency = pd.read_csv(
    '../data/agency.txt',   # path of the file with the format (.txt)
    sep=',',                # type of separator, in this case is comma
    header=0,               # to recognize the first row as header, it is needed to define this parameter header=0
    dtype={                 # parameter to define the type of each column
        "agency_id": "object",
        "agency_name": "object",
        "agency_url": "object",
        "agency_timezone": "object"
    }
)
```

**Additional tip**: Sometimes columns such as dates are not in a standard format (e.g., `yyyymmdd`). In that case, use the `converters` parameter:

```python
df_calendar_dates = pd.read_csv(
    '../data/calendar_dates.txt', 
    sep=',', 
    header=0,
    dtype={
        "service_id": "object",
        "exception_type": "object"
    },
    converters={        
        "date": lambda x: pd.to_datetime(x, format='%Y%m%d') # converters parameter is useful when you need to handle the column before converting. In this case, the column would be date type, but is written 20251001 (yyyymmdd) and we need to clarify the format to convert.
    }
)
```

In `src/utils`, we created `data_loader.py`, where each function loads one `.txt` file and converts it into a dataframe.

Some common checks after loading a dataframe:

```python
display(df.head()) # Show the first 5 rows of the dataframe
display(df.dtypes) # Print the data type for each column
display(df.describe(include='all')) # Calculate and show descriptive values of each column, such as mean, median, frequency, count and others
```

### 4.3 Data Transformation

Below is an example of a transformation function you might use. The idea is to return all stops related to a specific trip.

> #### How to do that?

Inputs:
1) `df_trips`: Dataframe created from `trips.txt`
2) `df_stop_times`: Dataframe created from `stop_times.txt` with all stops of each trip_id.
3) `df_stops`: Dataframe created from stops.txt with stop information, such as latitude and longitude - *important to create visualization with Folium!*.
4) `list_trips_id`: List of trip IDs to filter on

Output: A dataframe with trip and stop information that can later be used with Folium.

```python
def get_trip_stops(df_trips:pd.DataFrame, df_stop_times:pd.DataFrame, df_stops:pd.DataFrame, list_trips_id:list[str]) -> pd.DataFrame:
    return (
        df_trips    # select the dataframe
        .loc[df_trips.trip_id.isin(list_trips_id)] # filter only trip_ids are in the list
        .merge(     # inner join with df_stop_times, using trip_id as key
            df_stop_times[['trip_id','stop_id','stop_sequence','pickup_type','drop_off_type']],
            on='trip_id',
            how='inner'
        )
        .merge(     # inner join with df_stops, using stop_id as key
            df_stops[['stop_id','stop_name','stop_lat','stop_lon','stop_code']],
            on='stop_id',
            how='inner'
        )
        [['trip_id', 'stop_id', 'stop_code', 'stop_name', 'stop_sequence', 'stop_lat', 'stop_lon']] # Finally selecting only collumns that I'll need
    )
```

> #### Small advice for writing readable Pandas code! 

Instead of writing as this way: 

```python
df_new = df.loc['expression'].merge('merge 1').merge('merge 2')[['column1','column2']]
```

try it:

```python
df_new = (
    df
    .loc['expression']
    .merge('merge 1')
    .merge('merge 2')
    [['column1','column2']]
)
```

You can explore all functions inside `src/utils/data_processing.py`.

### 4.4 Folium Elements

Folium is a visualization library designed especially for geospatial analysis! I highly recommend checking its official *[documentation](https://python-visualization.github.io/folium/latest/getting_started.html)*. Below are the main elements used in this project.:

> #### How to create a map?

First is to initialize a map with folium and load in a variable, because after we will add elements on this map (markers, routes and etc).

```python
import folium
m = folium.Map(
    location=[53.299132, -7.732962], # Latitude and Longitude to point. Those lat and lon are for Dublin. 
    zoom_start=8 # You can control the zoom in on this map
)
```

Notice that I loaded this map in the "m" variable.

> #### How to create Markers?

Marker is useful to create specific points on the map. In our case for the stops of the trip!

```python
folium.Marker(
    location=[45.3288, -121.6625],  # Latitude and Longitude of the Marker
    tooltip="Click me!",            # Show this message when you hover it
    popup="Mt. Hood Meadows",       # Show this popup when you click the Marker  
    icon=folium.Icon(icon="cloud"), # You can choose the icon, color and other parameters
).add_to(m)                         # And finally, add this element into "m" (map) variable, using .add_to(m)
```

Tip: There are stops for each `trip_id` in dataframe. One way to iterate dataframe like a list and add all stops is using `.iterrows()`:

```python
for index,row in df.iterrows():                             # Get index and row for each dataframe row
    folium.Marker(                                              
        location=[row['stop_lat'],row['stop_lon']],         # Using row['column'], you can select a specific column and return the value
        popup=f"{row['stop_name']} - {row['stop_code']}",   
        tooltip="Click to see more info"
    ).add_to(m)
```

> #### How to create PolyLine?

Now if we would like to create the shape/route of this trip, we can use folium.PolyLine():

```python
trail_coordinates = [
    (-71.351871840295871, -73.655963711222626),
    (-71.374144382613707, -73.719861619751498),
    (-71.391042575973145, -73.784922248007007),
    (-71.400964450973134, -73.851042243124397),
    (-71.402411391077322, -74.050048183880477)
]                                                  # Creating a list of latitude and longitude pairs

folium.PolyLine(
    trail_coordinates,                             # Adding the list to create shapes 
    tooltip="Coast"                                # Show this message when you hover the line
).add_to(m)                                        # Adding this element into map
```

Notice to create the shape you need to input a list of shapes, and we are working with dataframe. A good way to transform is:

```python
list_lat_lon = df_trip_shape[['shape_pt_lat','shape_pt_lon']].values.to_list()
```

All these folium components we created in `src/components/folium_components.py`.

### 4.5 Streamlit

Finally, we will create a dashboard to visualize the data and provide a smooth and interactive user experience.

For full details, refer to the [Streamlit Official Docs](https://docs.streamlit.io).

> #### Import library

```python
import streamlit as st
from streamlit_folium import st_folium # This function will help us to display interactive folium maps
```

> #### Create Multi-Page App

To use multiple pages in Streamlit:
 - Create a folder named `pages/` in the same directory as your main `app.py`.
 - Each file inside pages/ becomes a new page automatically.

```markdown
src/
│ Home.py
│
└───pages/
       1_Trip_Route.py
       2_Search_Trips.py
```

> #### Displaying Data with st.write()

`st.write()` is Streamlit’s most flexible output function. You can pass:

- dataframes
- markdown
- text
- charts
- Python objects

Example:

```python
st.write("### Stops for the Selected Trip")
st.write(df_trip_stops)
```

Check out this [doc](https://docs.streamlit.io/develop/api-reference/write-magic/st.write)

> #### Using Filters

Filters help users explore subsets of the data and we can use different input widgets for doing it. Check [this doc](https://docs.streamlit.io/develop/api-reference/widgets) out!

Example using the [sidebox](https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox) in a sidebar:

```python
with st.sidebar:                                        # Create a sidebar
    trip_id_selected = st.selectbox(                    # Load value selected into a variable
        "Select the Trip ID below",
        options=df_trips['trip_id'].unique().tolist()   # Display option according to trip_id in df_trips
    )
```

Example using [`st.date_input()`](https://docs.streamlit.io/develop/api-reference/widgets/st.date_input) to input a date:

```python
with st.sidebar:
    date = st.date_input(                               # Load value into a variable
        "Select the date of your trip",                  
        datetime.date(2025,12,1)                        # By default select this date
    )
```

> #### Data Cache

Notice if you're consuming data from a data source (API, Dataframes and etc) and display them on Streamlit, the page won't stop reloading, because you will select/request continuosly!

To solve that, it is a good practice to cache your data. Read this [first topic](https://docs.streamlit.io/get-started/fundamentals/advanced-concepts)!

Check this example how to apply caching decorator:

```python
@st.cache_data              # Caching decorator
def load_data():            # You need to create a function
    return (                # In this case, I will return a list of Dataframes by calling my data_loader.py functions
        load_stops(),
        load_trips(),
        load_stop_times(),
        load_calendar(),
        load_shapes()
    )
```





