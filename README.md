# Time Series Forecasting with FastAPI and ARIMA

## Description

A web application for time series forecasting using ARIMA models to predict air passenger traffic. Built with FastAPI for the backend and Bootstrap for the user interface. **Fully dockerized for easy, reproducible deployment.**

## 🎥 Video Demo

Watch the project in action:

👉 [Click here to watch the demo](https://drive.google.com/file/d/1XCULUAZbuw-JpYPYSF90a2d3E63cjTC_/view?usp=sharing)

## Features

- **ARIMA/SARIMAX Predictions**: Time series model to forecast passenger numbers
- **Interactive Web Interface**: Responsive Bootstrap UI
- **CSV Data Upload**: Analyze your own time series data
- **REST API**: Endpoints for integration with other systems
- **Visualizations**: Charts generated with Matplotlib
- **Data Export**: Download predictions in JSON and CSV formats
- **🐳 Docker Containerization**: Effortless deployment with Docker

## Project Architecture

```
fastapi_time_series/
├── app/
│   ├── main.py                 # Main FastAPI application
│   ├── run_app.py              # Startup script with custom messages
│   ├── models/
│   │   ├── __init__.py
│   │   ├── arima_model.py      # ARIMA model management class
│   │   ├── trained_model.pkl   # Trained model (generated)
│   │   └── processed_data.pkl  # Preprocessed data (generated)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── forecast_service.py # Prediction service
│   │   └── custom_data_service.py # Service for custom data
│   └── static/
│       ├── css/
│       │   └── style.css       # Custom styles
│       └── js/
│           └── main.js         # Frontend JavaScript
├── templates/
│   ├── index.html              # Home page
│   ├── results.html            # Results page
│   ├── upload.html             # CSV upload page
│   └── custom_results.html     # Custom data results
├── data/
│   └── AirPassengers.csv       # Air passengers dataset
├── scripts/
│   └── train_model.py          # Model training script
├── Dockerfile                  # 🐳 Docker configuration
├── .dockerignore               # Files ignored by Docker
└── requirements.txt            # Python dependencies
├── air_passenger_forecast_using_arima.ipynb    # Exploratory analysis and model training notebook
```

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine

### 3-Step Launch:

1. **Clone the project**
```bash
git clone <repo-url>
cd fastapi_time_series
```

2. **Build the Docker image**
```bash
docker build -t fastapi-forecast .
```

3. **Run the container**
```bash
docker run --rm -p 8000:8000 fastapi-forecast
```

**🌐 Access the application:** http://localhost:8000
