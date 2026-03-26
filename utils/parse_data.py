import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

scats_file_path = "data/scats_data_october_2006.xls"
scats_sites_file_path = "data/SCATSSiteListingSpreadsheet_VicRoads.xlsx"

def parse_scats_data(path):
    df = pd.read_excel(path, sheet_name="Data", header=1)

    # Clean up column names
    df.columns = df.columns.str.strip()
    
    # Filter columns
    traffic_df = df[['SCATS Number', 'Date'] + [f'V{i:02d}' for i in range(96)]]

    grouped = traffic_df.groupby('SCATS Number')

    # Convert each site into time series
    site_time_series = {}

    for site, group in grouped:
        group = group.sort_values('Date')
        values = group[[f'V{i:02d}' for i in range(96)]].values
        series = values.flatten()

        site_time_series[site] = series
    
    # Check missing values
    # for site, series in site_time_series.items():
    #     if np.isnan(series).any():
    #         print(f"Missing value in {site}")

    return site_time_series

def normalize_data(series):
    scalers = {}
    scaled_series = {}

    # Normalize data
    for site, series in series.items():
        scaler = MinMaxScaler()
        series = series.reshape(-1, 1)

        scaled = scaler.fit_transform(series)
        scalers[site] = scaler
        scaled_series[site] = scaled

    return scaled_series, scalers

def parse_scats_sites(path):
    df = pd.read_excel(path, sheet_name="SCATS Site Numbers", header=9, engine="openpyxl")

    # Clean up column names
    df.columns = df.columns.str.strip()

    return df

def create_training_data(series, window_size=4):
    X, y = [], []

    for i in range(len(series) - window_size):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size])

    return np.array(X), np.array(y)

def create_training_data_for_all_sites(scaled_series, window_size=4):
    all_X, all_y = [], []

    for site, series in scaled_series.items():
        X, y = create_training_data(series, window_size)
        all_X.append(X)
        all_y.append(y)

    return np.vstack(all_X), np.vstack(all_y)

# series = parse_scats_data(scats_file_path)
# X, y = create_training_data(series[970], window_size=4)
# print(X.shape, y.shape)
# parse_scats_sites(scats_sites_file_path)