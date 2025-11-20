import os
import pandas as pd
import requests
from pathlib import Path
import zipfile
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_files_from_path(directory: str, extension: str) -> list:
    '''
    Returns a list of all files in a directory with a given extension.

    Args:
        directory: str - The directory to search for files.
        extension: str - The extension of the files to search for.

    Returns:
        list - A list of all files in the directory with the given extension.\
    '''

    if not directory:
        raise ValueError("Directory is required")

    if not extension:
        raise ValueError("Extension is required")

    if not os.path.isdir(directory):
        raise ValueError("Directory does not exist")

    filenames = []
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        _, _extension = os.path.splitext(full_path)
        if os.path.isfile(full_path) and _extension == extension:
            filenames.append(full_path)

    logger.info(f"Found {len(filenames)} files with the extension {extension} in the directory {directory}")
    return filenames

def generate_df_from_txt(filename: str) -> pd.DataFrame:
    '''
    Reads a txt file and returns a pandas DataFrame.
    Returns an empty DataFrame if the file is empty or has no data rows.

    Args:
        filename: str - The filename of the txt file to read.

    Returns:
        pd.DataFrame - A pandas DataFrame of the txt file.
    
    Raises:
        ValueError: If filename is not provided.
        FileNotFoundError: If the file does not exist.
        pd.errors.ParserError: If the file cannot be parsed as CSV.
    '''
    if not filename:
        raise ValueError("Filename is required")

    try:
        df = pd.read_csv(filename)
        logger.debug(f"Successfully read {filename} and returned a pandas DataFrame with {len(df)} rows")
        return df

    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise
    
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing {filename}: {e}")
        raise
    
    except pd.errors.EmptyDataError:
        logger.warning(f"File {filename} is empty, returning empty DataFrame")
        return pd.DataFrame()

def get_access_token(refresh_token: str) -> str:
    '''
    Args:
        refresh_token: str - The refresh token for the Mobility Database API.
    
    Returns:
        str - The access token.
    
    Raises:
        ValueError: If refresh_token is not provided or access token not found in response.
        requests.HTTPError: If the API request fails.
    '''
    if not refresh_token:
        raise ValueError("Refresh token is required")
    
    logger.info(f"Generating access token using refresh token: {refresh_token}")
    
    headers = {'Content-Type': 'application/json'}
    data = {'refresh_token': refresh_token}

    response = requests.post(
        url = "https://api.mobilitydatabase.org/v1/tokens",
        headers = headers,
        json = data
        )

    response.raise_for_status() # Raise an exception for HTTP errors, i.e. anything different than 2xx

    token_response = response.json()
    access_token = token_response.get('access_token')

    if not access_token:
        raise ValueError("Access token not found in the response")
    
    logger.info(f"Access token generated successfully: {access_token}")
    return access_token

def extract_zip_from_bytes(zip_content: bytes, extract_path: Path) -> None:
    """
    Extract a zip file from bytes content to a specified directory.

    Args:
        zip_content: bytes - The zip file content as bytes.
        extract_path: Path - The directory path to extract files to.

    Raises:
        ValueError: If zip_content or extract_path is not provided.
        zipfile.BadZipFile: If the content is not a valid zip file.
    """
    if not zip_content:
        raise ValueError("Zip content must be provided")
    
    if not extract_path:
        raise ValueError("Extract path must be provided")
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
            zip_ref.extractall(extract_path)
        logger.info(f"Successfully extracted zip file to: {extract_path}/")
    
    except zipfile.BadZipFile as e:
        logger.error(f"Invalid zip file: {e}")
        raise

def download_gtfs_feed(access_token: str, feed_id: str, extract_dir: str = "data") -> Path:
    '''
    Fetches GTFS feed metadata from Mobility Database API.

    Args:
        access_token: str - The access token for the Mobility Database API.
        feed_id: Feed ID (e.g. 'mdb-2364')
    
    Returns:
        dict: Feed metadata including download URL
    
    Raises:
    ValueError: If access_token is not provided.
    requests.HTTPError: If the API request fails.
    '''

    if not access_token:
        raise ValueError("Access token is required")

    if not feed_id:
        raise ValueError("Feed ID is required")
    
    logger.info(f"Fetching feed metadata for feed ID: {feed_id}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    mobility_url = f"https://api.mobilitydatabase.org/v1/gtfs_feeds/{feed_id}"
    response = requests.get(mobility_url, headers=headers)
    response.raise_for_status()

    feed_data = response.json()

    download_url = (
        feed_data.get('latest_dataset', {}).get('hosted_url') or
        feed_data.get('source_info', {}).get('producer_url')
    )

    if not download_url:
        raise ValueError("No download URL found for feed")
    
    logger.info(f"Feed Name: {feed_data.get('data_type')} - {feed_data.get('provider', 'N/A')}")
    logger.info(f"Feed ID: {feed_data.get('id', 'N/A')}")   
    logger.info(f"Downloading GTFS feed from: {download_url}")
    
    zip_response = requests.get(download_url, stream=True)
    zip_response.raise_for_status()

    extract_path = Path(extract_dir)
    extract_path.mkdir(exist_ok=True)

    extract_zip_from_bytes(zip_response.content, extract_path)

    downloaded_at = feed_data.get('latest_dataset', {}).get('downloaded_at', None)
    timestamp_to_save = downloaded_at if downloaded_at else datetime.now().isoformat()

    timestamp_file = extract_path / "timestamp.txt"
    with open(timestamp_file, 'w') as f:
        f.write(timestamp_to_save)

    if downloaded_at:
        logger.info(f"Download successful! Extracted to: {extract_path} at {downloaded_at}")
    else:
        logger.warning("No downloaded at timestamp available in feed data. Saved current timestamp.")
        logger.info(f"Download successful! Extracted to: {extract_path}/ at {timestamp_to_save}")

    return extract_path


def get_live_data(stop_id: list, api_key: str) -> dict:
    """
    Get live data for a list of stop IDs

    Args:
        stop_id: list - The list of stop IDs to get live data for.
        api_key: str - The API key to use to get live data.

    Returns:
        dict - The live data for the stop IDs.

    Raises:
        ValueError: If stop_id or api_key is not provided.
        requests.HTTPError: If the API request fails.
    """
    if not stop_id:
        raise ValueError("Stop_id must be provided")
    if not api_key:
        raise ValueError("API key must be provided")
    BASE_URL = "http://localhost:7341"
    header = {"X-API-KEY": api_key, "Accept": "application/json"}
    url = f"{BASE_URL}/api/v1/arrivals"
    params = {"stop": stop_id}
    response = requests.get(url, params=params, headers=header)
    logger.info(f"Request data for stop {stop_id}")
    
    # Raise an exception for HTTP errors, i.e. anything different than 2xx
    response.raise_for_status()

    logger.info(f"Live data retrieved successfully for stop IDs: {stop_id}")
    return response.json()


def get_df_from_live_data(response: dict) -> pd.DataFrame:
    """
    Convert live data to a pandas DataFrame.
    Flattens the nested structure where each stop has multiple arrivals.

    Args:
        response: dict - The live data response from the API.
                        Expected format: {stop_id: {'arrivals': [...]}, ...}

    Returns:
        pd.DataFrame - Flattened DataFrame with columns: agency, headsign, 
                      real_time_arrival, route, scheduled_arrival, stop_id

    Raises:
        ValueError: If response is not provided or is not a dictionary.
        KeyError: If response structure is invalid (missing 'arrivals' key).
    """
    if not response:
        raise ValueError("Response must be provided")
    
    if not isinstance(response, dict):
        raise ValueError("Response must be a dictionary")
    
    # Collect all DataFrames first
    all_rows = []
    for stop_id in response.keys():
        # Each stop_id has a list of arrivals
        # Each arrival has information about the agency, route, headsign, 
        # real_time_arrival and scheduled_arrival
        arrivals = response[stop_id].get('arrivals', [])
        if arrivals:
            row = pd.DataFrame(arrivals)
            row['stop_id'] = stop_id
            all_rows.append(row)
    
    if not all_rows:
        logger.warning("No arrivals found in response, returning empty DataFrame")
        return pd.DataFrame()
    
    df = pd.concat(all_rows, ignore_index=True)
    logger.info(f"Created DataFrame with {len(df)} arrivals from {len(response)} stops")
    return df
