from pathlib import Path
import pandas as pd
import transformation as tr


def run_pipeline():
    print("1. Fetching ETF data...")
    df_etf_raw = tr.fetch_etf_data()

    print("2. Loading WIBOR data...")
    df_wibor_raw = tr.load_wibor_data()

    print("3. Transforming raw datasets...")
    df_etf = tr.transform_etf_data(df_etf_raw)
    df_wibor = tr.transform_wibor_data(df_wibor_raw)

    print("4. Merging Daily ETF with Latest Available WIBOR...")
    # Convert to datetime and normalize to same unit (microseconds)
    df_etf.index = pd.to_datetime(df_etf.index).as_unit('us')
    df_wibor.index = pd.to_datetime(df_wibor.index).as_unit('us')

    # Sort indices before merging
    df_etf = df_etf.sort_index()
    df_wibor = df_wibor.sort_index()

    # Perform backward ASOF merge
    df_merged = pd.merge_asof(
        df_etf,
        df_wibor,
        left_index=True,
        right_index=True,
        direction="backward",
    ).dropna()

    # Validating Clean Data
    print("5. Validating merged data...")
    if not tr.validate_data(df_merged):
        raise ValueError("Data validation failed. Aborting pipeline process.")

    # Save to CSV after successful validation
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "data" / "clean_merged_data.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(output_path)

    print(f"Done! Pipeline finished successfully. Data saved to: {output_path}")


if __name__ == "__main__":
    run_pipeline()