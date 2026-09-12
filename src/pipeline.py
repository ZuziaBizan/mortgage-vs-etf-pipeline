from pathlib import Path
import pandas as pd
import simulation as sim
import transformation as tr


def run_pipeline():
    print("1. Fetching & transforming ETF data...")
    df_etf = tr.fetch_etf_data()

    print("2. Loading & transforming WIBOR data...")
    df_wibor = tr.load_wibor_data()

    print("3. Merging Daily ETF with Latest Available WIBOR...")

    # FIX: Reset index to explicitly force matching datetime64[ns] dtypes on columns
    df_etf = df_etf.reset_index()
    df_wibor = df_wibor.reset_index()

    # Identify date column names (typically 'Date' or 'Data')
    date_col_etf = df_etf.columns[0]
    date_col_wibor = df_wibor.columns[0]

    # Explicitly enforce nanosecond datetime precision
    df_etf[date_col_etf] = pd.to_datetime(df_etf[date_col_etf]).astype(
        "datetime64[ns]"
    )
    df_wibor[date_col_wibor] = pd.to_datetime(df_wibor[date_col_wibor]).astype(
        "datetime64[ns]"
    )

    # Ensure datasets are sorted by date before asof merge
    df_etf = df_etf.sort_values(by=date_col_etf)
    df_wibor = df_wibor.sort_values(by=date_col_wibor)

    # Perform backward asof merge on explicit date columns
    df_merged = pd.merge_asof(
        df_etf,
        df_wibor,
        left_on=date_col_etf,
        right_on=date_col_wibor,
        direction="backward",
    ).dropna()

    # Restore primary date index and clean up redundant date columns
    df_merged.set_index(date_col_etf, inplace=True)
    if date_col_wibor in df_merged.columns:
        df_merged.drop(columns=[date_col_wibor], inplace=True)

    print("4. Validating merged data...")
    if not tr.validate_data(df_merged):
        raise ValueError("Data validation failed. Aborting pipeline process.")

    # Save clean dataset to CSV
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "data" / "clean_merged_data.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(output_path)

    print(
        f"Done! Pipeline finished successfully. Data saved to: {output_path}\n"
    )

    # Automatically trigger interactive simulation using the merged dataset
    sim.run_simulation(df_merged)


if __name__ == "__main__":
    run_pipeline()