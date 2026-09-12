import pandas as pd

def column_rename(df, columns_dict):
    return df.rename(columns=columns_dict)

def drop_unnecessary_columns(df, columns_to_keep):
    return df[columns_to_keep].copy()

def convert_to_datetime(df, date_column):
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    return df_copy

#Data validation
import pandas as pd


def validate_data(df: pd.DataFrame):
    # 1. Check if required columns exist in the DataFrame
    required_columns = ["wibor_3m", "etf_price"]
    for column in required_columns:
        if column not in df.columns:
            print(f"Error: Missing required column: {column}")
            return False

    # 2. Check if there are any missing values (NaNs) in those columns
    if df["wibor_3m"].isna().sum() > 0:
        print("Error: wibor_3m column contains missing values!")
        return False

    if df["etf_price"].isna().sum() > 0:
        print("Error: etf_price column contains missing values!")
        return False

    # 3. Check for realistic values (Sanity check)
    # ETF prices must be positive numbers
    if (df["etf_price"] <= 0).any():
        print("Error: ETF price cannot be 0 or negative!")
        return False

    # WIBOR rate should be realistic (between 0% and 30%)
    if (df["wibor_3m"] < 0).any() or (df["wibor_3m"] > 0.30).any():
        print("Error: WIBOR rate is out of realistic bounds (0% to 30%)!")
        return False

    print("Data validation passed successfully!")
    return True