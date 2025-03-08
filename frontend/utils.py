"""
Utility functions for the IoT Sensor Dashboard
"""
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import io
import json


def fetch_data(api_url, endpoint, params=None):
    """
    Fetch data from the API
    
    Args:
        api_url (str): Base URL for the API
        endpoint (str): API endpoint to fetch
        params (dict): Parameters for the request
        
    Returns:
        dict or list: The JSON response from the API
    """
    try:
        response = requests.get(f"{api_url}/{endpoint}", params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {endpoint}: {e}")
        return []


def readings_to_dataframe(readings):
    """
    Convert a list of sensor readings to a Pandas DataFrame
    
    Args:
        readings (list): List of sensor readings dictionaries
        
    Returns:
        pd.DataFrame: DataFrame with properly formatted data
    """
    if not readings:
        return pd.DataFrame()
    
    df = pd.DataFrame(readings)
    
    # Convert timestamp strings to datetime objects
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df


def generate_summary_stats(df, value_column="value"):
    """
    Generate summary statistics for sensor readings
    
    Args:
        df (pd.DataFrame): DataFrame with sensor readings
        value_column (str): Column containing the sensor values
        
    Returns:
        dict: Dictionary containing statistics
    """
    if df.empty:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "std": None
        }
    
    return {
        "count": len(df),
        "mean": float(df[value_column].mean()),
        "median": float(df[value_column].median()),
        "min": float(df[value_column].min()),
        "max": float(df[value_column].max()),
        "std": float(df[value_column].std())
    }


def detect_anomalies(df, value_column="value", window=20, sigma=3):
    """
    Detect anomalies in sensor data using a moving average and standard deviation
    
    Args:
        df (pd.DataFrame): DataFrame containing sensor readings
        value_column (str): Column name for the values
        window (int): Size of the moving window
        sigma (float): Number of standard deviations for threshold
        
    Returns:
        pd.DataFrame: Original DataFrame with additional 'anomaly' column
    """
    if len(df) < window or df.empty:
        # Not enough data for detection
        if not df.empty:
            df['anomaly'] = False
        return df
    
    # Create a copy of the dataframe
    result = df.copy()
    
    # Calculate rolling statistics
    rolling_mean = df[value_column].rolling(window=window).mean()
    rolling_std = df[value_column].rolling(window=window).std()
    
    # Define upper and lower bounds
    upper_bound = rolling_mean + sigma * rolling_std
    lower_bound = rolling_mean - sigma * rolling_std
    
    # Mark anomalies
    result['anomaly'] = (df[value_column] > upper_bound) | (df[value_column] < lower_bound)
    
    # Fill NaN values (first window-1 rows) with False
    result['anomaly'] = result['anomaly'].fillna(False)
    
    return result


def export_to_csv(df, filename=None):
    """
    Export DataFrame to CSV string
    
    Args:
        df (pd.DataFrame): DataFrame to export
        filename (str): Optional filename
        
    Returns:
        tuple: (csv_string, filename)
    """
    if df.empty:
        return "", "empty_data.csv"
    
    # Generate CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_data_{timestamp}.csv"
    
    return csv_string, filename


def predict_next_values_advanced(df, value_column="value", time_column="timestamp", periods=24):
    """
    Advanced prediction of future values using more sophisticated algorithms
    """
    if len(df) < 10 or df.empty:  # Need enough data for prediction
        return pd.DataFrame()
    
    # Import additional libraries for better predictions
    from statsmodels.tsa.arima.model import ARIMA
    
    # Ensure the data is sorted by time
    df = df.sort_values(by=time_column)
    
    # Prepare data for ARIMA model
    values = df[value_column].values
    
    # Fit ARIMA model - adjust parameters as needed
    model = ARIMA(values, order=(5,1,0))
    model_fit = model.fit()
    
    # Forecast future values
    forecast = model_fit.forecast(steps=periods)
    
    # Generate future timestamps
    last_time = df[time_column].max()
    time_delta = (df[time_column].max() - df[time_column].min()) / len(df)
    future_times = [last_time + (i+1) * time_delta for i in range(periods)]
    
    # Create a DataFrame with the predictions
    predictions = pd.DataFrame({
        time_column: future_times,
        value_column: forecast,
        'predicted': True
    })
    
    return predictions


def process_alert_data(alerts):
    """
    Process alert data for display
    
    Args:
        alerts (list): List of alert dictionaries
        
    Returns:
        pd.DataFrame: Processed DataFrame of alerts
    """
    if not alerts:
        return pd.DataFrame()
    
    df = pd.DataFrame(alerts)
    
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        now = pd.Timestamp.now(tz=df['timestamp'].dt.tz)
        df['time_ago'] = (now - df['timestamp']).apply(format_timedelta)
    
    if 'sensor_id' in df.columns:
        df['sensor'] = df['sensor_id'].apply(lambda x: x.replace('_', ' ').title())
    
    return df


def format_timedelta(td):
    """
    Format a timedelta into a human-readable string like "5 minutes ago"
    
    Args:
        td (timedelta): The timedelta object
        
    Returns:
        str: Human readable string
    """
    seconds = td.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"


def group_sensors_by_type(sensors):
    """
    Group sensors by their type
    
    Args:
        sensors (list): List of sensor dictionaries
        
    Returns:
        dict: Dictionary with sensor types as keys and lists of sensor IDs as values
    """
    if not sensors:
        return {}
    
    sensor_groups = {}
    
    for sensor in sensors:
        sensor_type = sensor.get('sensor_type', '')
        sensor_id = sensor.get('sensor_id', '')
        
        if sensor_type and sensor_id:
            if sensor_type not in sensor_groups:
                sensor_groups[sensor_type] = []
            
            sensor_groups[sensor_type].append(sensor_id)
    
    return sensor_groups


def group_sensors_by_location(sensors):
    """
    Group sensors by their location
    
    Args:
        sensors (list): List of sensor dictionaries
        
    Returns:
        dict: Dictionary with locations as keys and lists of sensor IDs as values
    """
    if not sensors:
        return {}
    
    location_groups = {}
    
    for sensor in sensors:
        location = sensor.get('location', '')
        sensor_id = sensor.get('sensor_id', '')
        
        if location and sensor_id:
            if location not in location_groups:
                location_groups[location] = []
            
            location_groups[location].append(sensor_id)
    
    return location_groups