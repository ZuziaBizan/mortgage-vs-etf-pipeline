from pathlib import Path
import pandas as pd
import simulation as sim  # Importujemy moduł symulacji
import transformation as tr


def run_pipeline():
    print("1. Fetching ETF data...")
    df_etf_raw = tr.fetch_etf_data()

    print("2. Loading WIBOR data...")
    df_wibor_raw = tr.load_wibor_data()



    print("3. Merging Daily ETF with Latest Available WIBOR...")
    # Standardize datetime precision
    df_etf.index = pd.to_datetime(df_etf.index).astype("datetime64[ns]")
    df_wibor.index = pd.to_datetime(df_wibor.index).astype("datetime64[ns]")

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

    # 4. Validating Clean Data
    print("4. Validating merged data...")
    if not tr.validate_data(df_merged):
        print("Stopping pipeline due to invalid data.")
        return

    # Save to CSV after successful validation
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "data" / "clean_merged_data.csv"
    df_merged.to_csv(output_path)

    print("Done! Data prepared successfully.\n")
    print("=" * 50)
    print("STARTING MORTGAGE VS ETF SIMULATION")
    print("=" * 50)

    # 5. Run interactive simulation using the freshly created data
    sim.run_simulation(df_merged)


if __name__ == "__main__":
    run_pipeline()