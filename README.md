# Energy Forecast Application

This application visualizes energy consumption forecasts using various machine learning models.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Features

- Interactive visualization of energy consumption forecasts
- Support for multiple fuel types and forecasting models
- SQLite database storage for forecast results
- Real-time graph updates

## Data

The application uses the following data sources:
- Historical energy consumption data
- Forecasts from multiple models (ARIMA, Linear Regression, Random Forest, LSTM)

## Models

The application includes forecasts from the following models:
- ARIMA
- Linear Regression
- Random Forest
- LSTM 