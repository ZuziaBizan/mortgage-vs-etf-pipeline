from pathlib import Path
import pandas as pd
import yfinance as yf

# ==========================================
# 1. DATA LOADING FUNCTIONS
# ==========================================


def fetch_etf_data(ticker="VWCE.DE", start_date="2016-01-01"):
    # Download historical ETF market data from Yahoo Finance
    df_etf = yf.download(ticker, start=start_date, auto_adjust=True)
    return transform_etf_data(df_etf)


def load_wibor_data(file_path=None):
    # If no path is provided, find the project base directory automatically
    if file_path is None:
        base_dir = Path(__file__).resolve().parents[1]
        file_path = base_dir / "data" / "data_raw_wibor_3m.csv"

    # Read raw WIBOR historical interest rates from local CSV file
    df_wibor = pd.read_csv(file_path)
    return transform_wibor_data(df_wibor)


# ==========================================
# 2. HELPER TRANSFORMATION FUNCTIONS
# ==========================================


def keep_columns (df, columns_to_keep):
    # Keep only specified columns in the DataFrame
    return df[columns_to_keep]


def column_rename(df, rename_dict):
    # Rename DataFrame columns using a dictionary mapping
    return df.rename(columns=rename_dict)


def convert_to_datetime(df, date_column):
    # Convert specified column to pandas Datetime objects
    df[date_column] = pd.to_datetime(df[date_column])
    return df


# ==========================================
# 3. MAIN TRANSFORMATION FUNCTIONS
# ==========================================


def transform_etf_data(df_etf_raw):
    """Clean and transform daily raw ETF data."""
    df_etf = df_etf_raw.copy()

    # Flatten MultiIndex columns returned by yfinance if present
    if isinstance(df_etf.columns, pd.MultiIndex):
        df_etf.columns = df_etf.columns.get_level_values(0)

    # Keep only Close column and rename it to etf_price
    df_etf = keep_columns(df_etf, ["Close"])
    df_etf = column_rename(df_etf, {"Close": "etf_price"})
    df_etf.index = pd.to_datetime(df_etf.index).tz_localize(None).normalize()
    return df_etf.sort_index()
  

def transform_wibor_data(df_wibor_raw):
    """Clean, format, and scale daily raw WIBOR data."""
    # Convert date column to datetime
    df_wibor = convert_to_datetime(df_wibor_raw, "Data")

    # Keep required columns and rename interest rate column
    df_wibor = keep_columns(df_wibor, ["Data", "Zamkniecie"])
    df_wibor = column_rename(df_wibor, {"Zamkniecie": "wibor_3m"})

    # Set date as index and convert percentage values to decimals (e.g. 5.5% -> 0.055)
    df_wibor.set_index("Data", inplace=True)
    df_wibor["wibor_3m"] = df_wibor["wibor_3m"] / 100

    df_wibor.index = pd.to_datetime(df_wibor.index).tz_localize(None).normalize()
    return df_wibor.sort_index()



# ==========================================
# 4. DATA VALIDATION FUNCTIONS
# ==========================================


def validate_data(df):
    # 1. Verify that all required columns are present in the DataFrame
    if "wibor_3m" not in df.columns:
        print("Error: Missing wibor_3m column!")
        return False

    if "etf_price" not in df.columns:
        print("Error: Missing etf_price column!")
        return False

    # 2. Check for missing (NaN/null) values in key columns
    if df["wibor_3m"].isna().sum() > 0:
        print("Error: wibor_3m column contains missing values!")
        return False

    if df["etf_price"].isna().sum() > 0:
        print("Error: etf_price column contains missing values!")
        return False

    # 3. Ensure ETF prices are positive and non-zero
    for cena in df["etf_price"]:
        if cena <= 0:
            print("Error: ETF price cannot be 0 or negative!")
            return False

    # 4. Check if WIBOR rates fall within realistic economic boundaries (0% to 30%)
    for wibor in df["wibor_3m"]:
        if wibor < 0 or wibor > 0.30:
            print("Error: WIBOR rate is out of realistic bounds (0% to 30%)!")
            return False

    print("Data validation passed successfully!")
    return True