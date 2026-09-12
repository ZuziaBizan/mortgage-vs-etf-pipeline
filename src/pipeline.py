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

    df_etf.index = pd.to_datetime(df_etf.index).astype("datetime64[ns]")
    df_wibor.index = pd.to_datetime(df_wibor.index).astype("datetime64[ns]")
    
    df_merged = pd.merge_asof(
        df_etf,
        df_wibor,
        left_index=True,
        right_index=True,
        direction="backward",
    ).dropna()


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