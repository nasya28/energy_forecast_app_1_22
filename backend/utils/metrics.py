import sqlite3
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def calculate_metrics(actual, predicted):
    """Вычисляет MAE и RMSE между фактическими и прогнозными значениями."""
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    return mae, rmse

def save_metrics_to_db(fuel_type, model_name, mae, rmse, db_path='forecasts.db'):
    """Сохраняет метрики в базу данных."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fuel_type TEXT,
            model_name TEXT,
            mae REAL,
            rmse REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT INTO forecast_metrics (fuel_type, model_name, mae, rmse)
        VALUES (?, ?, ?, ?)
    ''', (fuel_type, model_name, mae, rmse))
    conn.commit()
    conn.close()

def print_all_metrics(db_path='forecasts.db'):
    """Выводит все метрики из базы данных forecast_metrics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fuel_type, model_name, mae, rmse, created_at FROM forecast_metrics
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    if not rows:
        print('Нет сохранённых метрик.')
    else:
        print(f"{'Топливо':<20} {'Модель':<20} {'MAE':<10} {'RMSE':<10} {'Дата'}")
        print('-'*70)
        for row in rows:
            print(f"{row[0]:<20} {row[1]:<20} {row[2]:<10.4f} {row[3]:<10.4f} {row[4]}")
    conn.close()

def get_all_metrics(db_path='forecasts.db'):
    """Возвращает все метрики из базы данных forecast_metrics в виде списка словарей."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fuel_type, model_name, mae, rmse, created_at FROM forecast_metrics
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'fuel_type': row[0],
            'model_name': row[1],
            'mae': row[2],
            'rmse': row[3],
            'created_at': row[4]
        }
        for row in rows
    ]

def get_metrics_by_fuel(fuel_type, db_path='forecasts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fuel_type, model_name, mae, rmse, created_at FROM forecast_metrics
        WHERE fuel_type = ?
        ORDER BY created_at DESC
    ''', (fuel_type,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'fuel_type': row[0],
            'model_name': row[1],
            'mae': row[2],
            'rmse': row[3],
            'created_at': row[4]
        }
        for row in rows
    ]

def get_latest_metrics_by_fuel(fuel_type, db_path='forecasts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fuel_type, model_name, mae, rmse, MAX(created_at) as created_at
        FROM forecast_metrics
        WHERE fuel_type = ?
        GROUP BY model_name
        ORDER BY model_name
    ''', (fuel_type,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'fuel_type': row[0],
            'model_name': row[1],
            'mae': row[2],
            'rmse': row[3],
            'created_at': row[4]
        }
        for row in rows
    ]
