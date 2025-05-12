import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, jsonify, send_file, request
import sqlite3
import os
from TER import forecast_results, df_actual
import json
import numpy as np
import io
import matplotlib.pyplot as plt
from utils.metrics import get_all_metrics, get_metrics_by_fuel, get_latest_metrics_by_fuel

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('forecasts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fuel_type TEXT NOT NULL,
            model_name TEXT NOT NULL,
            forecast_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def save_forecast_to_db(fuel_type, model_name, forecast_data):
    conn = sqlite3.connect('forecasts.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forecasts (fuel_type, model_name, forecast_data)
        VALUES (?, ?, ?)
    ''', (fuel_type, model_name, json.dumps(forecast_data.tolist())))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forecasts')
def get_forecasts():
    conn = sqlite3.connect('forecasts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forecasts ORDER BY created_at DESC')
    forecasts = c.fetchall()
    conn.close()
    
    return jsonify([{
        'id': f[0],
        'fuel_type': f[1],
        'model_name': f[2],
        'forecast_data': json.loads(f[3]),
        'created_at': f[4]
    } for f in forecasts])

@app.route('/api/save_forecasts')
def save_forecasts():
    for fuel in forecast_results:
        for model_name, forecast in forecast_results[fuel].items():
            save_forecast_to_db(fuel, model_name, forecast)
    return jsonify({'status': 'success'})

@app.route('/plot')
def plot():
    fuel_type = request.args.get('fuel')
    if not fuel_type:
        return "Specify 'fuel' query param", 400

    models = ['ARIMA', 'Linear Regression', 'Random Forest', 'LSTM']
    colors = ['red', 'green', 'purple', 'orange']
    linestyles = ['--', '--', '--', '--']
    forecast_dict = forecast_results.get(fuel_type, {})
    if not forecast_dict:
        return "No forecast found", 404

    # Фактические данные (2005-2020)
    actual = df_actual[df_actual['Топливо'] == fuel_type]
    actual_years = actual['Год'].values
    actual_values = actual['Валовое потребление ТЭР'].values

    years_forecast = list(range(2021, 2021 + 10))

    fig, ax = plt.subplots(figsize=(10, 6))
    # Фактические данные
    ax.plot(actual_years, actual_values, label=f'{fuel_type} (фактическое)', color='blue')
    # Прогнозы (непрерывные линии: факт + прогноз)
    for idx, model in enumerate(models):
        forecast = forecast_dict.get(model)
        if forecast is not None:
            years_full = list(actual_years) + years_forecast
            values_full = list(actual_values) + list(forecast)
            ax.plot(years_full, values_full, label=f'{fuel_type} ({model})', color=colors[idx], linestyle=linestyles[idx])
    ax.set_title(f'Прогноз потребления {fuel_type} на 2021-2030', fontsize=14)
    ax.set_xlabel('Год', fontsize=12)
    ax.set_ylabel('Потребление ТЭР', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return send_file(img, mimetype='image/png')

@app.route('/plot3d')
def plot3d():
    model = request.args.get('model')
    if model not in ['ARIMA', 'Linear Regression', 'Random Forest', 'LSTM']:
        return "Specify model param: ARIMA, Linear Regression, Random Forest, LSTM", 400

    years_past = np.arange(2005, 2021)
    years_future = np.arange(2021, 2031)
    years = np.concatenate((years_past, years_future))
    fuels = df_actual['Топливо'].unique()
    colormaps = {'ARIMA': 'viridis', 'Linear Regression': 'plasma', 'Random Forest': 'cividis', 'LSTM': 'magma'}

    Z = np.zeros((len(fuels), len(years)))
    for j, fuel in enumerate(fuels):
        actual_data = df_actual[df_actual['Топливо'] == fuel]['Валовое потребление ТЭР'].values
        Z[j, :len(actual_data)] = actual_data
        forecast_data = forecast_results[fuel][model]
        Z[j, len(actual_data):] = forecast_data

    X, Y = np.meshgrid(years, np.arange(len(fuels)))
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, cmap=colormaps[model], edgecolor='k', alpha=0.85)
    ax.set_xlabel('Год', fontsize=10, labelpad=8)
    ax.set_ylabel('Топливо', fontsize=10, labelpad=8)
    ax.set_zlabel('Потребление ТЭР (млн. тонн)', fontsize=10, labelpad=8)
    ax.set_title(f'Модель: {model}', fontsize=12, pad=12)
    ax.set_yticks(np.arange(len(fuels)))
    ax.set_yticklabels(fuels, fontsize=8, rotation=30, ha='right')
    ax.view_init(elev=30, azim=50)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)
    return send_file(img, mimetype='image/png')

@app.route('/api/metrics', methods=['GET'])
def api_get_metrics():
    fuel_type = request.args.get('fuel_type')
    if fuel_type:
        metrics = get_metrics_by_fuel(fuel_type)
    else:
        metrics = get_all_metrics()
    return jsonify(metrics)

@app.route('/api/metrics/latest', methods=['GET'])
def api_get_latest_metrics():
    fuel_type = request.args.get('fuel_type')
    if not fuel_type:
        return jsonify([])
    metrics = get_latest_metrics_by_fuel(fuel_type)
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True) 