"""
Chart components for the IoT Sensor Dashboard
This module provides reusable chart components for visualizing sensor data
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta


def create_time_series_chart(df, value_column="value", time_column="timestamp", 
                             title=None, y_label=None, unit=""):
    """
    Create a time series chart for sensor data
    
    Args:
        df (pd.DataFrame): DataFrame containing sensor data
        value_column (str): Column name for the sensor values
        time_column (str): Column name for the timestamps
        title (str): Chart title
        y_label (str): Y-axis label
        unit (str): Unit of measurement
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    if df.empty:
        # Create an empty figure with a message if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis=dict(title="Time"),
            yaxis=dict(title=y_label if y_label else "Value")
        )
        fig.add_annotation(
            text="No data available for the selected time range",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create time series chart
    fig = px.line(
        df, 
        x=time_column, 
        y=value_column,
        title=title,
        labels={time_column: "Time", value_column: f"{y_label if y_label else 'Value'} ({unit})"}
    )
    
    # Add range selector and slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        hovermode="x unified"
    )
    
    return fig


def create_gauge_chart(value, min_value, max_value, title, unit=""):
    """
    Create a gauge chart for displaying current sensor value
    
    Args:
        value (float): Current value to display
        min_value (float): Minimum value for the gauge
        max_value (float): Maximum value for the gauge
        title (str): Chart title
        unit (str): Unit of measurement
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    # Define threshold ranges based on sensor type from title
    if "temperature" in title.lower():
        # Temperature thresholds
        ranges = [
            (min_value, min_value + (max_value - min_value) * 0.3, "blue"),  # Cold
            (min_value + (max_value - min_value) * 0.3, min_value + (max_value - min_value) * 0.7, "green"),  # Normal
            (min_value + (max_value - min_value) * 0.7, max_value, "red")  # Hot
        ]
    elif "humidity" in title.lower():
        # Humidity thresholds
        ranges = [
            (min_value, 30, "red"),  # Too dry
            (30, 60, "green"),  # Comfortable
            (60, max_value, "blue")  # Too humid
        ]
    else:
        # Generic ranges split into three equal parts
        third = (max_value - min_value) / 3
        ranges = [
            (min_value, min_value + third, "blue"),
            (min_value + third, min_value + 2 * third, "green"),
            (min_value + 2 * third, max_value, "red")
        ]
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [min_value, max_value], "tickwidth": 1},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [r[0], r[1]], "color": r[2]} for r in ranges
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": value
            }
        },
        number={"suffix": f" {unit}", "font": {"size": 24}}
    ))
    
    fig.update_layout(height=250)
    
    return fig


def create_heatmap(df, sensor_ids, time_column="timestamp", value_column="value", 
                   title="Sensor Data Heatmap"):
    """
    Create a heatmap for comparing multiple sensors over time
    
    Args:
        df (pd.DataFrame): DataFrame containing data for multiple sensors
        sensor_ids (list): List of sensor IDs to include
        time_column (str): Column name for timestamps
        value_column (str): Column name for values
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    if df.empty or not sensor_ids:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(title="No data available for heatmap")
        fig.add_annotation(
            text="No data available for the selected sensors",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Resample data to create regular time intervals (hourly)
    df[time_column] = pd.to_datetime(df[time_column])
    df.set_index(time_column, inplace=True)
    
    # Create a pivot table for the heatmap
    sensor_id_column = "sensor_id"  # Adjust if your column name is different
    pivot_df = df.pivot_table(
        index=pd.Grouper(freq='H'),  # Group by hour
        columns=sensor_id_column,
        values=value_column,
        aggfunc='mean'  # Use mean for multiple values in same hour
    )
    
    # Filter for selected sensors only
    pivot_df = pivot_df[sensor_ids]
    
    # Create heatmap
    fig = px.imshow(
        pivot_df.T,  # Transpose to have sensors on y-axis
        labels=dict(x="Time", y="Sensor", color="Value"),
        title=title,
        color_continuous_scale="Viridis"
    )
    
    # Update layout
    fig.update_layout(height=400)
    
    return fig


def create_histogram(df, value_column="value", title=None, bins=20, unit=""):
    """
    Create a histogram for sensor value distribution
    
    Args:
        df (pd.DataFrame): DataFrame containing sensor data
        value_column (str): Column name for values
        title (str): Chart title
        bins (int): Number of bins for histogram
        unit (str): Unit of measurement
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    if df.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(title="No data available for histogram")
        fig.add_annotation(
            text="No data available for the selected time range",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create histogram
    fig = px.histogram(
        df, 
        x=value_column,
        nbins=bins,
        title=title,
        labels={value_column: f"Value ({unit})"},
        opacity=0.8
    )
    
    # Add a curve of the distribution
    fig.update_layout(
        bargap=0.1,
        xaxis_title=f"Value ({unit})",
        yaxis_title="Count"
    )
    
    return fig


def create_comparison_chart(df, sensor_groups, time_column="timestamp", value_column="value", 
                           group_column="sensor_id", title="Sensor Comparison"):
    """
    Create a chart comparing multiple sensor groups
    
    Args:
        df (pd.DataFrame): DataFrame containing data for multiple sensors
        sensor_groups (dict): Dictionary mapping group names to lists of sensor IDs
        time_column (str): Column name for timestamps
        value_column (str): Column name for values
        group_column (str): Column containing the sensor ID or group
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    if df.empty or not sensor_groups:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(title="No data available for comparison")
        fig.add_annotation(
            text="No data available for the selected sensors",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Convert timestamps to datetime
    df[time_column] = pd.to_datetime(df[time_column])
    
    # Create figure
    fig = go.Figure()
    
    # Add a line for each sensor group
    for group_name, sensors in sensor_groups.items():
        # Filter for sensors in this group
        group_df = df[df[group_column].isin(sensors)]
        
        if not group_df.empty:
            # Resample to hourly data
            group_df.set_index(time_column, inplace=True)
            hourly_data = group_df.groupby(pd.Grouper(freq='H'))[value_column].mean().reset_index()
            
            # Add line to chart
            fig.add_trace(go.Scatter(
                x=hourly_data[time_column],
                y=hourly_data[value_column],
                mode='lines',
                name=group_name
            ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        legend_title="Sensor Group"
    )
    
    return fig
