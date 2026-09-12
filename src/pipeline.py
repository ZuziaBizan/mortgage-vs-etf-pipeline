from pathlib import Path
import pandas as pd
import yfinance as yf
import transformation as tr


def run_pipeline():
    print("1. Fetching ETF data...")
    df_etf_raw = yf.download(
        "VWCE.DE",
        start="2016-01-01",
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=10,
    )
    if isinstance(df_etf_raw.columns, pd.MultiIndex):
        df_etf_raw.columns = df_etf_raw.columns.get_level_values(0)

    print("2. Loading WIBOR data...")
    base_dir = Path(__file__).resolve().parents[1]
    csv_path = base_dir / "data" / "data_raw_wibor_3m.csv"
    df_wibor_raw = pd.read_csv(csv_path)

    print("3. Transforming ETF (Daily)...")
    df_etf = tr.drop_unnecessary_columns(df_etf_raw, ["Close"])
    df_etf = tr.column_rename(df_etf, {"Close": "etf_price"})

    print("4. Transforming WIBOR (Daily)...")
    df_wibor = tr.convert_to_datetime(df_wibor_raw, "Data")

    # 1. Keep ONLY the relevant columns first
    df_wibor = tr.drop_unnecessary_columns(df_wibor, ["Data", "Zamkniecie"])

    # 2. Rename 'Zamkniecie' to 'wibor_3m'
    df_wibor = tr.column_rename(df_wibor, {"Zamkniecie": "wibor_3m"})

    # 3. Set 'Data' as the index and convert percentage to decimal
    df_wibor.set_index("Data", inplace=True)
    df_wibor["wibor_3m"] = df_wibor["wibor_3m"] / 100

    print("5. Merging Daily ETF with Latest Available WIBOR...")
   # Match date formats before combining datasets
    df_etf.index = pd.to_datetime(df_etf.index).astype("datetime64[ns]")
    df_wibor.index = pd.to_datetime(df_wibor.index).astype("datetime64[ns]")

# Sort both datasets by date before merging
    df_etf = df_etf.sort_index()
    df_wibor = df_wibor.sort_index()

    # Perform backward ASOF merge (assigns the latest available WIBOR rate to each ETF date)
    df_merged = pd.merge_asof(
        df_etf,
        df_wibor,
        left_index=True,
        right_index=True,
        direction="backward",
    ).dropna()

    # 6. Validating Clean Data
    print("6. Validating merged data...")
    if not tr.validate_data(df_merged):
        print("Stopping pipeline due to invalid data.")
        return

    # Save to CSV only after successful validation
    output_path = base_dir / "data" / "clean_merged_data.csv"
    df_merged.to_csv(output_path)

    print("Done! Saved clean daily dataset with assigned WIBOR.")
    print(df_merged.head())


if __name__ == "__main__":
    run_pipeline()