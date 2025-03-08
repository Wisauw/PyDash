# IoT Sensor Monitoring Dashboard

A comprehensive system for receiving, storing, and visualizing data from IoT sensors in real-time.

![Dashpreview](https://github.com/Wisauw/PyDash/raw/master/asset/im1.png "Title")


## Features

- **Real-time Data Collection**: Receive sensor data via REST API or MQTT protocol
- **Data Storage**: Persist sensor readings in a SQLite database (configurable for PostgreSQL)
- **Interactive Dashboard**: Visualize sensor data with real-time charts and graphs
- **Alerting System**: Configure thresholds and receive alerts when values exceed normal ranges
- **Data Export**: Download historical sensor data in CSV format
- **Anomaly Detection**: Automatically identify unusual sensor readings

## System Architecture

The system follows a modern architecture with separate backend and frontend components:

- **Backend**: FastAPI application that handles data collection, processing, and storage
- **Frontend**: Streamlit dashboard for visualization and user interaction
- **Database**: SQLite (default) or PostgreSQL for data persistence
- **Communication**: REST API and MQTT for receiving sensor data

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/iot-dashboard.git](https://github.com/Wisauw/PyDash.git)
   cd iot_dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv iot_dashboard_env
   iot_dashboard_env\Scripts\activate

   # On macOS/Linux
   python -m venv iot_dashboard_env
   source iot_dashboard_env/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The application uses environment variables for configuration. You can set these in a `.env` file in the project root:

```env
# Database settings
DATABASE_URL=sqlite:///./iot_data.db

# MQTT settings (optional)
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=sensors/#

# Alert thresholds
TEMPERATURE_MIN=10.0
TEMPERATURE_MAX=30.0
HUMIDITY_MIN=20.0
HUMIDITY_MAX=80.0

# Notification settings (optional)
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EMAIL_FROM=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_TO=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Running the Application

1. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   The API will be available at http://localhost:8000 with API documentation at http://localhost:8000/docs

2. In a separate terminal, start the Streamlit dashboard:
   ```bash
   streamlit run frontend/dashboard.py
   ```
   The dashboard will be available at http://localhost:8501

3. To simulate sensor data for testing, run:
   ```bash
   python backend/sensor_simulator.py
   ```

## API Endpoints

The backend provides the following API endpoints:

- `GET /api/sensors` - Get a list of all sensors
- `GET /api/sensors/{sensor_id}/readings` - Get readings for a specific sensor
- `POST /api/sensors/data` - Submit new sensor data
- `GET /api/alerts` - Get recent alerts
- `GET /api/status` - Check API status

## Project Structure

```
iot_dashboard/
├── backend/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database models and connections
│   ├── mqtt_client.py      # MQTT subscriber
│   ├── main.py             # FastAPI application
│   ├── data_processor.py   # Process and store sensor data
│   ├── alert_system.py     # Alerting mechanisms
│   └── sensor_simulator.py # Test data generator
│
├── frontend/
│   ├── __init__.py
│   ├── dashboard.py        # Streamlit dashboard app
│   ├── charts.py           # Chart components
│   └── utils.py            # Utility functions
│
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## Extending the Project

### Adding New Sensor Types

1. Define threshold values in `config.py`
2. Add alert conditions in `alert_system.py`
3. Update the simulator to generate test data

### Customizing the Dashboard

The dashboard is built with Streamlit and can be easily customized by editing the `frontend/dashboard.py` file. Chart components and utility functions are modular and can be extended.

### Using PostgreSQL Instead of SQLite

For production deployments, PostgreSQL is recommended:

1. Install PostgreSQL and create a database
2. Update the `DATABASE_URL` in your configuration
3. Install the PostgreSQL driver: `pip install psycopg2-binary`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the efficient web framework
- Streamlit for the easy-to-use dashboard capabilities
- Plotly for interactive visualizations
