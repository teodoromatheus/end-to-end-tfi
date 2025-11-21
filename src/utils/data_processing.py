import pandas as pd
from typing import Optional
import datetime

def get_trip_shapes(df_trips:pd.DataFrame, df_shapes:pd.DataFrame, trip_id_list:Optional[list[str]]=None) -> dict[str, list[list[float,float]]]:

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