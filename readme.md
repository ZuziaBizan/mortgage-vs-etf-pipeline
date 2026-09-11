# Mortgage Overpayment vs. ETF Investing

Hi! This is my Python project where I check what makes more financial sense:
paying off a mortgage faster or investing excess money in an ETF (VWCE.DE).

I built this project to practice writing modular Python code, building daily data pipelines, and working with real financial data.

---

## What Does This Project Do?

1. **Fetches Financial Data:** Downloads ETF prices (`VWCE.DE`) from Yahoo Finance and combines them with Polish WIBOR 3M interest rates.
2. **Cleans & Prepares Data:** Fixes dates, aligns trading days, and ensures no missing data.
3. **Automates Daily Updates:** Uses GitHub Actions to automatically update the dataset every day.
4. **Runs an Interactive Simulation:** Asks the user for their mortgage details and calculates which option leaves them with more money!

---

### Tools & Libraries Used

* **Python 3.10+**
* **Pandas** – for data cleaning and merging
* **yfinance** – to download ETF (VWCE.DE) price
* **GitHub Actions** – for daily, automatic ETF price updates
* **Jupyter Notebook** – for initial data analysis (EDA)

---

## 📁 Project Structure

```text
.
├── .github/workflows/
│   └── daily_pipeline.yml  # Runs the code automatically every day
├── data/
│   ├── clean_merged_data.csv   # The ready-to-use clean dataset
│   └── data_raw_wibor_3m.csv   # WIBOR 3M interest rates
├── src/
│   ├── eda.ipynb               # My data exploration notebook
│   ├── pipeline.py            # Main script to run everything
│   ├── simulation.py          # Math engine comparing Both options
│   └── transformation.py      # Functions for cleaning the data
├── .gitignore
└── README.md
