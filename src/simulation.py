from pathlib import Path
import pandas as pd


def run_simulation(df):
    # 1. User mortgage input
    loan_amount = float(input("What is your mortgage amount (PLN): "))
    loan_years = int(input("How many years will you be paying it: "))
    bank_margin = float(input("What is the bank margin in %: ")) / 100
    overpayment_pln = float(
        input("Monthly extra budget you would like to invest (PLN): ")
    )

    print("\n1. Shorten loan duration\n2. Lower monthly payment")
    choice = input("Select option (1 or 2): ").strip()
    if choice == "2":
        overpayment_type = "lower_payment"
    else:
        overpayment_type = "shorten_term"

    eur_pln_rate = 4.30
    total_months = loan_years * 12

    # Resample dataset directly from input DataFrame
    monthly_rates_m = (df["wibor_3m"].resample("ME").last() + bank_margin) / 12
    etf_prices = df["etf_price"].resample("ME").last()
    simulation_months = min(total_months, len(monthly_rates_m))

    # Initial mortgage balances and tracking variables
    balance_std = loan_amount
    balance_a = loan_amount
    interest_paid_std = 0
    interest_paid_a = 0

    # Strategy A (Lower Monthly Payment / Shorten Term)
    etf_units_a = 0

    # Strategy B (ETF Investing)
    etf_units_b = 0

    # 2. Main Simulation Loop
    for i in range(simulation_months):
        r = monthly_rates_m.iloc[i]  # Monthly interest rate
        rem_months = total_months - i  # Remaining months
        etf_price = etf_prices.iloc[i]

        # Standard Mortgage (Baseline)
        annuity_factor = (r * (1 + r) ** rem_months) / (
            (1 + r) ** rem_months - 1
        )
        pmt_std = balance_std * annuity_factor
        interest_std = balance_std * r
        interest_paid_std += interest_std
        balance_std = max(0, balance_std - (pmt_std - interest_std))

        # Strategy A (Overpayment)
        if balance_a > 0:
            interest_a = balance_a * r
            interest_paid_a += interest_a

            if overpayment_type == "lower_payment":
                pmt_a = balance_a * annuity_factor
                saved_pln = max(0, pmt_std - pmt_a)
                etf_units_a += (saved_pln / eur_pln_rate) / etf_price
            else:
                pmt_a = pmt_std

            principal_a = pmt_a - interest_a
            actual_overpay = min(
                overpayment_pln, max(0, balance_a - principal_a)
            )
            balance_a = max(0, balance_a - principal_a - actual_overpay)
        else:
            # Mortgage is paid off: The full old payment + extra budget go into ETFs
            monthly_extra_cash_pln = pmt_std + overpayment_pln
            etf_units_a += (monthly_extra_cash_pln / eur_pln_rate) / etf_price

        # Strategy B (ETF Investing)
        etf_units_b += (overpayment_pln / eur_pln_rate) / etf_price

    # 3. Final calculations & results
    final_etf_price = etf_prices.iloc[simulation_months - 1]

    # Strategy A: ETF Portfolio + Belka Tax (19%)
    gross_a = (etf_units_a * final_etf_price) * eur_pln_rate
    invested_a_pln = gross_a
    net_etf_val_a = gross_a - (max(0, gross_a - invested_a_pln) * 0.19)

    equity_gained_a = (balance_std - balance_a) + net_etf_val_a

    # Strategy B: ETF Portfolio + Belka Tax (19%)
    gross_b = (etf_units_b * final_etf_price) * eur_pln_rate
    total_invested_b = overpayment_pln * simulation_months
    net_etf_val_b = gross_b - (max(0, gross_b - total_invested_b) * 0.19)

    # 4. Display Results
    print("\n" + "=" * 50)
    print("SIMULATION RESULTS")
    print("=" * 50)
    print(
        f"Strategy A (Overpayment) Net Equity Gained + ETF: {equity_gained_a:,.2f} PLN"
    )
    print(
        f"Strategy B (ETF Investing) Net Portfolio Value:  {net_etf_val_b:,.2f} PLN"
    )
    print("-" * 50)

    # Comparison and final verdict
    diff = net_etf_val_b - equity_gained_a
    if diff > 0:
        print(f"VERDICT: Strategy B (ETF) wins by {diff:,.2f} PLN")
    else:
        print(f"VERDICT: Strategy A (Overpayment) wins by {abs(diff):,.2f} PLN")


# Script entry point for interactive user execution
if __name__ == "__main__":
    csv_path = (
        Path(__file__).resolve().parents[1] / "data" / "clean_merged_data.csv"
    )
    if csv_path.exists():
        df_clean = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        run_simulation(df_clean)
    else:
        print("Data file not found. Please run pipeline.py first to generate clean_merged_data.csv!")