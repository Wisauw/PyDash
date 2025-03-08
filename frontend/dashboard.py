import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import io
import json
import sys
import os
import random
cache_buster = random.randint(1, 1000000)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from frontend.utils import predict_next_values
except ImportError:
    # fallback
    def predict_next_values(df, value_column="value", time_column="timestamp", periods=24):
        """Simple prediction function as fallback"""
        if len(df) < 10 or df.empty:
            return pd.DataFrame()
        #simple lm
        x = range(len(df))
        y = df[value_column].values
 
        n = len(x)
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean

        future_x = range(len(df), len(df) + periods)
        future_y = [slope * i + intercept for i in future_x]

        last_time = df[time_column].max()
        if len(df) > 1:
            avg_delta = (df[time_column].max() - df[time_column].min()) / (len(df) - 1)
            future_times = [last_time + (i+1) * avg_delta for i in range(periods)]
        else:
            future_times = [last_time + pd.Timedelta(hours=i+1) for i in range(periods)]
        
        predictions = pd.DataFrame({
            time_column: future_times,
            value_column: future_y,
            'predicted': True
        })
        
        return predictions

# Set page config
st.set_page_config(
    page_title="IoT Sensor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API URL
API_URL = "http://localhost:8000/api"

# Fetch data from API
def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# Sensor readings to df
def readings_to_dataframe(readings):
    if not readings:
        return pd.DataFrame()
    
    df = pd.DataFrame(readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


if 'show_predictions' not in st.session_state:
    st.session_state.show_predictions = False


st.title("IoT Sensor Monitoring Dashboard")
st.markdown("""
This dashboard displays real-time data from IoT sensors.
Monitor temperature, humidity, and other sensor readings with interactive charts.
""")

# Sidebar controls
with st.sidebar:
    st.header("Dashboard Controls")
    
    # Advanced options
    st.subheader("Options")
    
    # predictions
    st.session_state.show_predictions = st.checkbox(
        "Show Predictions", 
        value=st.session_state.show_predictions,
        help="Enable to show predicted future values based on current data trend"
    )
    
    st.divider()
    
    # Get all sensors 
    sensors = fetch_data("sensors")
    sensor_options = {s["sensor_id"]: f"{s['name']} ({s['location']})" for s in sensors}
    
    # Sensor
    st.subheader("Sensor Selection")
    if not sensor_options:
        st.warning("No sensors found. Make sure your backend is running and sensor data is being sent.")
        selected_sensor_id = None
    else:
        selected_sensor_id = st.selectbox(
            "Select Sensor",
            options=list(sensor_options.keys()),
            format_func=lambda x: sensor_options.get(x, x),
        )
    
    # Time range
    st.subheader("Time Range")
    time_range = st.selectbox(
        "Select Period",
        options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
        index=2
    )
    
    # Map time range 
    time_ranges = {
        "Last Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
        "Last 7 Days": 24*7,
        "Last 30 Days": 24*30
    }
    
    hours = time_ranges[time_range]
   # Updated timezone-aware version:
    from datetime import datetime, timedelta, timezone

    # Use timezone-aware objects
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

# Main content area
if selected_sensor_id:
    # Fetch data
    params = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "limit": 1000
    }
    readings = fetch_data(f"sensors/{selected_sensor_id}/readings", params)
    df = readings_to_dataframe(readings)
    
    if df.empty:
        st.warning(f"No data available for the selected sensor and time range.")
    else:
        # Get sensor info for the sensor
        selected_sensor = next((s for s in sensors if s["sensor_id"] == selected_sensor_id), None)
        
        # Display current value in a big metric
        current_value = df.iloc[0]["value"] if not df.empty else 0
        current_unit = df.iloc[0]["unit"] if not df.empty and 'unit' in df.columns else ""
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"Current {selected_sensor['sensor_type'].capitalize()}", 
                value=f"{current_value} {current_unit}",
                delta=f"{current_value - df.iloc[1]['value']:.2f}" if len(df) > 1 else None
            )
        
        with col2:
            st.metric(
                label="Average",
                value=f"{df['value'].mean():.2f} {current_unit}"
            )
        
        with col3:
            st.metric(
                label="Min/Max",
                value=f"{df['value'].min():.2f} / {df['value'].max():.2f} {current_unit}"
            )
        
        # Apply predictions 
        if st.session_state.show_predictions:
            predictions_df = predict_next_values(df)
            # Only add predictions if we have data
            if not predictions_df.empty:
                # Create a combined dataframe with both actual and predicted data
                combined_df = pd.concat([
                    df.assign(predicted=False), 
                    predictions_df
                ]).reset_index(drop=True)
                
                # Create time series chart with predictions
                st.subheader(f"📈 {selected_sensor['sensor_type'].capitalize()} over Time (with Predictions)")
                
                fig = go.Figure()
                
                # Add actual data
                fig.add_trace(go.Scatter(
                    x=df["timestamp"],
                    y=df["value"],
                    mode="lines",
                    name="Actual Data"
                ))
                
                # Add predicted data
                fig.add_trace(go.Scatter(
                    x=predictions_df["timestamp"],
                    y=predictions_df["value"],
                    mode="lines",
                    line=dict(dash="dash", color="orange"),
                    name="Prediction"
                ))
                
                # Update layout
                fig.update_layout(
                    title=f"{selected_sensor['name']} in {selected_sensor['location']}",
                    xaxis_title="Time",
                    yaxis_title=f"{selected_sensor['sensor_type'].capitalize()} ({current_unit})",
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
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough data for predictions. Need at least 10 data points.")
                
                # Regular chart without predictions
                st.subheader(f"📈 {selected_sensor['sensor_type'].capitalize()} over Time")
                fig = px.line(
                    df, 
                    x="timestamp", 
                    y="value",
                    title=f"{selected_sensor['name']} in {selected_sensor['location']}",
                    labels={"timestamp": "Time", "value": f"{selected_sensor['sensor_type'].capitalize()} ({current_unit})"}
                )
                
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
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            # Regular chart without predictions
            st.subheader(f"📈 {selected_sensor['sensor_type'].capitalize()} over Time")
            fig = px.line(
                df, 
                x="timestamp", 
                y="value",
                title=f"{selected_sensor['name']} in {selected_sensor['location']}",
                labels={"timestamp": "Time", "value": f"{selected_sensor['sensor_type'].capitalize()} ({current_unit})"}
            )
            
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
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export option
        if st.button("Export Data to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_sensor_id}_{start_time.date()}_{end_time.date()}.csv",
                mime="text/csv"
            )

# Alerts section
st.subheader("⚠️ Recent Alerts")
alerts = fetch_data("alerts", {"hours": hours, "limit": 10})

if alerts:
    alert_df = pd.DataFrame(alerts)
    alert_df['timestamp'] = pd.to_datetime(alert_df['timestamp'])
    
    # Display alerts in a table
    st.dataframe(
        alert_df[['sensor_id', 'timestamp', 'value', 'threshold', 'message']],
        use_container_width=True
    )
else:
    st.info("No alerts in the selected time period.")

# Footer
st.markdown("---")
st.markdown("IoT Sensor Dashboard - Real-time monitoring system")