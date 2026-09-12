from pathlib import Path
import pandas as pd
import yfinance as yf

# ==========================================
# 1. DATA LOADING FUNCTIONS
# ==========================================


def fetch_etf_data(ticker="VWCE.DE", start_date="2016-01-01"):
    df_etf = yf.download(
        ticker,
        start=start_date,
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=10,
    )
    return transform_etf_data(df_etf)


def load_wibor_data(file_path=None):
    if file_path is None:
        base_dir = Path(__file__).resolve().parents[1]
        file_path = base_dir / "data" / "data_raw_wibor_3m.csv"

    df_wibor = pd.read_csv(file_path)
    return transform_wibor_data(df_wibor)


# ==========================================
# 2. HELPER TRANSFORMATION FUNCTIONS
# ==========================================


def drop_unnecessary_columns(df, columns_to_keep):
    return df[columns_to_keep].copy()


def column_rename(df, columns_dict):
    return df.rename(columns=columns_dict)


def convert_to_datetime(df, date_column):
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    return df_copy


# ==========================================
# 3. MAIN TRANSFORMATION FUNCTIONS
# ==========================================


def transform_etf_data(df_etf_raw):
    df_etf = df_etf_raw.copy()

    if isinstance(df_etf.columns, pd.MultiIndex):
        df_etf.columns = df_etf.columns.get_level_values(0)

    df_etf = drop_unnecessary_columns(df_etf, ["Close"])
    df_etf = column_rename(df_etf, {"Close": "etf_price"})

    # Usuniecie strefy czasowej UTC z yfinance
    df_etf.index = pd.to_datetime(df_etf.index).tz_localize(None)
    return df_etf.sort_index()


def transform_wibor_data(df_wibor_raw):
    df_wibor = convert_to_datetime(df_wibor_raw, "Data")
    df_wibor = drop_unnecessary_columns(df_wibor, ["Data", "Zamkniecie"])
    df_wibor = column_rename(df_wibor, {"Zamkniecie": "wibor_3m"})

    df_wibor.set_index("Data", inplace=True)
    df_wibor["wibor_3m"] = df_wibor["wibor_3m"] / 100

    df_wibor.index = pd.to_datetime(df_wibor.index).tz_localize(None)
    return df_wibor.sort_index()


# ==========================================
# 4. DATA VALIDATION FUNCTIONS
# ==========================================


def validate_data(df: pd.DataFrame):
    required_columns = ["wibor_3m", "etf_price"]
    for column in required_columns:
        if column not in df.columns:
            print(f"Error: Missing required column: {column}")
            return False

    if df["wibor_3m"].isna().sum() > 0:
        print("Error: wibor_3m column contains missing values!")
        return False

    if df["etf_price"].isna().sum() > 0:
        print("Error: etf_price column contains missing values!")
        return False

    if (df["etf_price"] <= 0).any():
        print("Error: ETF price cannot be 0 or negative!")
        return False

    if (df["wibor_3m"] < 0).any() or (df["wibor_3m"] > 0.30).any():
        print("Error: WIBOR rate is out of realistic bounds (0% to 30%)!")
        return False

    print("Data validation passed successfully!")
    return True