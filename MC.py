import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


print("started")


# =========================================================
# MONTE CARLO SIMULATION
# Flughafen Zürich AG - Peak Pricing Szenarien
# Speicherschonende Version
# =========================================================

# -------------------------
# 1. BASISWERTE
# -------------------------
BASE_YEAR = 2025
M_TOTAL = 270_116
AVIATION_REVENUE_MIO = 415.7
E_BASE = (AVIATION_REVENUE_MIO * 1_000_000) / M_TOTAL  # CHF pro Bewegung

N_ITERATIONS = 10_000
RANDOM_SEED = 42
CHUNK_SIZE = 50_000  # kleiner halten für stabilen RAM-Verbrauch

OUTPUT_DIR = "outputs_monte_carlo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(RANDOM_SEED)

# -------------------------
# 2. SZENARIOPARAMETER
# -------------------------
SCENARIOS = {
    "Moderat": {
        "alpha": (0.15, 0.20, 0.25),
        "p":     (0.05, 0.08, 0.12),
        "r":     (0.78, 0.85, 0.92),
        "s":     (0.05, 0.09, 0.14),
        "k":     (0.92, 0.96, 1.00),
    },
    "Selektiv": {
        "alpha": (0.18, 0.25, 0.30),
        "p":     (0.08, 0.12, 0.18),
        "r":     (0.68, 0.76, 0.86),
        "s":     (0.08, 0.14, 0.22),
        "k":     (0.89, 0.94, 0.99),
    },
    "Aggressiv": {
        "alpha": (0.20, 0.30, 0.40),
        "p":     (0.15, 0.22, 0.30),
        "r":     (0.45, 0.60, 0.75),
        "s":     (0.10, 0.18, 0.28),
        "k":     (0.85, 0.91, 0.97),
    },
}


# -------------------------
# 3. HILFSFUNKTIONEN
# -------------------------
def triangular_sample(minimum: float, mode: float, maximum: float, size: int) -> np.ndarray:
    return np.random.triangular(left=minimum, mode=mode, right=maximum, size=size)


def simulate_scenario(
    scenario_name: str,
    params: dict,
    n_iterations: int,
    m_total: int,
    e_base: float,
    chunk_size: int = 50_000
) -> pd.DataFrame:
    """
    Speicherschonende Simulation:
    - zieht in Chunks
    - behält nur gültige Ziehungen
    - stoppt exakt bei n_iterations
    """

    # Vorallokation für exakt n Iterationen
    alpha_arr = np.empty(n_iterations, dtype=np.float64)
    p_arr = np.empty(n_iterations, dtype=np.float64)
    r_arr = np.empty(n_iterations, dtype=np.float64)
    s_arr = np.empty(n_iterations, dtype=np.float64)
    k_arr = np.empty(n_iterations, dtype=np.float64)
    d_arr = np.empty(n_iterations, dtype=np.float64)

    m_peak_arr = np.empty(n_iterations, dtype=np.float64)
    e_peak_arr = np.empty(n_iterations, dtype=np.float64)
    e_off_arr = np.empty(n_iterations, dtype=np.float64)

    r0_arr = np.empty(n_iterations, dtype=np.float64)
    r1_arr = np.empty(n_iterations, dtype=np.float64)
    delta_chf_arr = np.empty(n_iterations, dtype=np.float64)
    delta_mio_arr = np.empty(n_iterations, dtype=np.float64)

    filled = 0
    loop_counter = 0

    while filled < n_iterations:
        loop_counter += 1
        remaining = n_iterations - filled
        current_chunk = max(chunk_size, remaining)

        alpha_draws = triangular_sample(*params["alpha"], size=current_chunk)
        p_draws = triangular_sample(*params["p"], size=current_chunk)
        r_draws = triangular_sample(*params["r"], size=current_chunk)
        s_draws = triangular_sample(*params["s"], size=current_chunk)
        k_draws = triangular_sample(*params["k"], size=current_chunk)

        d_draws = 1.0 - r_draws - s_draws
        valid_mask = d_draws >= 0

        valid_count = int(valid_mask.sum())
        if valid_count == 0:
            continue

        take = min(valid_count, remaining)

        alpha_valid = alpha_draws[valid_mask][:take]
        p_valid = p_draws[valid_mask][:take]
        r_valid = r_draws[valid_mask][:take]
        s_valid = s_draws[valid_mask][:take]
        k_valid = k_draws[valid_mask][:take]
        d_valid = d_draws[valid_mask][:take]

        m_peak_aff = m_total * alpha_valid
        e_peak = e_base * (1.0 + p_valid)
        e_off = e_base * k_valid

        r0 = m_peak_aff * e_base
        r1 = m_peak_aff * ((r_valid * e_peak) + (s_valid * e_off))
        delta_r = r1 - r0

        end = filled + take

        alpha_arr[filled:end] = alpha_valid
        p_arr[filled:end] = p_valid
        r_arr[filled:end] = r_valid
        s_arr[filled:end] = s_valid
        k_arr[filled:end] = k_valid
        d_arr[filled:end] = d_valid

        m_peak_arr[filled:end] = m_peak_aff
        e_peak_arr[filled:end] = e_peak
        e_off_arr[filled:end] = e_off

        r0_arr[filled:end] = r0
        r1_arr[filled:end] = r1
        delta_chf_arr[filled:end] = delta_r
        delta_mio_arr[filled:end] = delta_r / 1_000_000

        filled = end

        if loop_counter % 5 == 0 or filled == n_iterations:
            print(f"{scenario_name}: {filled}/{n_iterations} valid iterations collected")

    df_result = pd.DataFrame({
        "scenario": scenario_name,
        "alpha": alpha_arr,
        "p": p_arr,
        "r": r_arr,
        "s": s_arr,
        "k": k_arr,
        "d": d_arr,
        "M_peak_aff": m_peak_arr,
        "E_base": e_base,
        "E_peak": e_peak_arr,
        "E_off": e_off_arr,
        "R0_CHF": r0_arr,
        "R1_CHF": r1_arr,
        "Delta_R_CHF": delta_chf_arr,
        "Delta_R_MioCHF": delta_mio_arr
    })

    return df_result


def summarize_results(df: pd.DataFrame) -> dict:
    delta = df["Delta_R_MioCHF"]

    return {
        "Scenario": df["scenario"].iloc[0],
        "Iterations": len(df),
        "Mean_Delta_R_MioCHF": delta.mean(),
        "Median_Delta_R_MioCHF": delta.median(),
        "StdDev_Delta_R_MioCHF": delta.std(ddof=1),
        "Min_Delta_R_MioCHF": delta.min(),
        "P5_Delta_R_MioCHF": delta.quantile(0.05),
        "P25_Delta_R_MioCHF": delta.quantile(0.25),
        "P75_Delta_R_MioCHF": delta.quantile(0.75),
        "P95_Delta_R_MioCHF": delta.quantile(0.95),
        "Max_Delta_R_MioCHF": delta.max(),
        "Prob_Delta_R_Positive": (delta > 0).mean(),
        "Prob_Delta_R_Negative": (delta < 0).mean(),
        "Avg_alpha": df["alpha"].mean(),
        "Avg_p": df["p"].mean(),
        "Avg_r": df["r"].mean(),
        "Avg_s": df["s"].mean(),
        "Avg_d": df["d"].mean(),
        "Avg_k": df["k"].mean(),
    }


def compute_input_correlations(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["alpha", "p", "r", "s", "k", "d", "Delta_R_MioCHF"]
    corr_matrix = df[cols].corr(numeric_only=True)
    delta_corr = corr_matrix[["Delta_R_MioCHF"]].drop(index=["Delta_R_MioCHF"])
    delta_corr = delta_corr.rename(columns={"Delta_R_MioCHF": "Correlation_with_Delta_R"})
    delta_corr["Abs_Correlation"] = delta_corr["Correlation_with_Delta_R"].abs()
    return delta_corr.sort_values("Abs_Correlation", ascending=False)


def save_histogram(df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.hist(df["Delta_R_MioCHF"], bins=50)
    plt.axvline(df["Delta_R_MioCHF"].mean(), linestyle="--", linewidth=1.5, label="Mean")
    plt.axvline(0, linestyle="-", linewidth=1.2, label="Zero line")
    plt.xlabel("Δ Aviation Revenue (Mio. CHF)")
    plt.ylabel("Frequency")
    plt.title(f"Monte Carlo Distribution of ΔR - {df['scenario'].iloc[0]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_boxplot(all_results: pd.DataFrame, output_path: str) -> None:
    scenario_order = ["Moderat", "Selektiv", "Aggressiv"]
    data = [
        all_results.loc[all_results["scenario"] == scenario, "Delta_R_MioCHF"].values
        for scenario in scenario_order
    ]

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, tick_labels=scenario_order, showfliers=False)
    plt.axhline(0, linestyle="--", linewidth=1.2)
    plt.ylabel("Δ Aviation Revenue (Mio. CHF)")
    plt.title("Comparison of Monte Carlo Results Across Scenarios")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_bar_comparison(summary_df: pd.DataFrame, output_path: str) -> None:
    summary_sorted = summary_df.set_index("Scenario").loc[["Moderat", "Selektiv", "Aggressiv"]].reset_index()
    x = np.arange(len(summary_sorted))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width / 2, summary_sorted["Mean_Delta_R_MioCHF"], width, label="Mean ΔR")
    plt.bar(x + width / 2, summary_sorted["P5_Delta_R_MioCHF"], width, label="5% percentile ΔR")
    plt.axhline(0, linestyle="--", linewidth=1.2)
    plt.xticks(x, summary_sorted["Scenario"])
    plt.ylabel("Δ Aviation Revenue (Mio. CHF)")
    plt.title("Expected Value and Downside Risk by Scenario")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def print_summary_table(summary_df: pd.DataFrame) -> None:
    cols = [
        "Scenario",
        "Iterations",
        "Mean_Delta_R_MioCHF",
        "Median_Delta_R_MioCHF",
        "P5_Delta_R_MioCHF",
        "P95_Delta_R_MioCHF",
        "Prob_Delta_R_Positive",
        "Prob_Delta_R_Negative",
        "Avg_d"
    ]

    print("\n" + "=" * 95)
    print("SUMMARY RESULTS")
    print("=" * 95)
    print(summary_df[cols].round(4).to_string(index=False))
    print("=" * 95 + "\n")


def export_to_excel(summary_df: pd.DataFrame, all_results: pd.DataFrame, correlation_tables: dict, output_path: str) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        all_results.to_excel(writer, sheet_name="All_Iterations", index=False)

        for scenario_name, corr_df in correlation_tables.items():
            safe_sheet_name = f"Corr_{scenario_name}"[:31]
            corr_df.to_excel(writer, sheet_name=safe_sheet_name)

        parameter_rows = []
        for scenario, params in SCENARIOS.items():
            for var_name, values in params.items():
                parameter_rows.append({
                    "Scenario": scenario,
                    "Variable": var_name,
                    "Min": values[0],
                    "Mode": values[1],
                    "Max": values[2]
                })

        parameter_df = pd.DataFrame(parameter_rows)
        parameter_df.to_excel(writer, sheet_name="Parameters", index=False)

        base_df = pd.DataFrame({
            "Variable": [
                "Base Year",
                "Flight Movements",
                "Aviation Revenue (Mio CHF)",
                "E_base (CHF per movement)",
                "Iterations",
                "Random Seed",
                "Chunk Size"
            ],
            "Value": [
                BASE_YEAR,
                M_TOTAL,
                AVIATION_REVENUE_MIO,
                E_BASE,
                N_ITERATIONS,
                RANDOM_SEED,
                CHUNK_SIZE
            ]
        })
        base_df.to_excel(writer, sheet_name="Base_Inputs", index=False)


def main():
    print("main() running...")

    print(f"Base year: {BASE_YEAR}")
    print(f"Flight movements: {M_TOTAL:,}")
    print(f"Aviation revenue: {AVIATION_REVENUE_MIO:.1f} Mio. CHF")
    print(f"E_base: {E_BASE:.3f} CHF per movement")
    print(f"Iterations per scenario: {N_ITERATIONS:,}")
    print(f"Chunk size: {CHUNK_SIZE:,}")
    print()

    scenario_results = {}
    summary_list = []
    correlation_tables = {}

    for scenario_name, params in SCENARIOS.items():
        print(f"Simulating scenario: {scenario_name}")

        df_scenario = simulate_scenario(
            scenario_name=scenario_name,
            params=params,
            n_iterations=N_ITERATIONS,
            m_total=M_TOTAL,
            e_base=E_BASE,
            chunk_size=CHUNK_SIZE
        )

        scenario_results[scenario_name] = df_scenario

        summary = summarize_results(df_scenario)
        summary_list.append(summary)

        corr_df = compute_input_correlations(df_scenario)
        correlation_tables[scenario_name] = corr_df

        scenario_csv_path = os.path.join(OUTPUT_DIR, f"iterations_{scenario_name.lower()}.csv")
        df_scenario.to_csv(scenario_csv_path, index=False)

        corr_csv_path = os.path.join(OUTPUT_DIR, f"correlations_{scenario_name.lower()}.csv")
        corr_df.to_csv(corr_csv_path)

        hist_path = os.path.join(OUTPUT_DIR, f"histogram_{scenario_name.lower()}.png")
        save_histogram(df_scenario, hist_path)

        print(f"{scenario_name} done")

    all_results = pd.concat(scenario_results.values(), ignore_index=True)

    summary_df = pd.DataFrame(summary_list)
    scenario_order = pd.Categorical(summary_df["Scenario"], categories=["Moderat", "Selektiv", "Aggressiv"], ordered=True)
    summary_df = summary_df.assign(_order=scenario_order).sort_values("_order").drop(columns="_order")

    print_summary_table(summary_df)

    boxplot_path = os.path.join(OUTPUT_DIR, "comparison_boxplot.png")
    save_boxplot(all_results, boxplot_path)

    barplot_path = os.path.join(OUTPUT_DIR, "comparison_mean_p5.png")
    save_bar_comparison(summary_df, barplot_path)

    summary_csv_path = os.path.join(OUTPUT_DIR, "summary_results.csv")
    summary_df.to_csv(summary_csv_path, index=False)

    excel_path = os.path.join(OUTPUT_DIR, "monte_carlo_results.xlsx")
    export_to_excel(
        summary_df=summary_df,
        all_results=all_results,
        correlation_tables=correlation_tables,
        output_path=excel_path
    )

    interpretation_path = os.path.join(OUTPUT_DIR, "quick_interpretation.txt")
    with open(interpretation_path, "w", encoding="utf-8") as f:
        f.write("Quick interpretation of Monte Carlo simulation results\n")
        f.write("=" * 60 + "\n\n")

        for _, row in summary_df.iterrows():
            f.write(f"Scenario: {row['Scenario']}\n")
            f.write(f"- Mean ΔR: {row['Mean_Delta_R_MioCHF']:.3f} Mio. CHF\n")
            f.write(f"- Median ΔR: {row['Median_Delta_R_MioCHF']:.3f} Mio. CHF\n")
            f.write(f"- 5% percentile: {row['P5_Delta_R_MioCHF']:.3f} Mio. CHF\n")
            f.write(f"- 95% percentile: {row['P95_Delta_R_MioCHF']:.3f} Mio. CHF\n")
            f.write(f"- Probability ΔR > 0: {row['Prob_Delta_R_Positive']:.2%}\n")
            f.write(f"- Probability ΔR < 0: {row['Prob_Delta_R_Negative']:.2%}\n")
            f.write(f"- Average residual share d: {row['Avg_d']:.3f}\n\n")

        f.write("Most important drivers by scenario (simple correlations):\n\n")
        for scenario_name, corr_df in correlation_tables.items():
            f.write(f"{scenario_name}:\n")
            top_drivers = corr_df.head(3)
            for idx, (var_name, corr_row) in enumerate(top_drivers.iterrows(), start=1):
                f.write(f"  {idx}. {var_name}: {corr_row['Correlation_with_Delta_R']:.3f}\n")
            f.write("\n")

    print("Output files saved:")
    print(f"- {summary_csv_path}")
    print(f"- {excel_path}")
    print(f"- {boxplot_path}")
    print(f"- {barplot_path}")
    print(f"- {interpretation_path}")
    print(f"- folder: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
    print("finished")