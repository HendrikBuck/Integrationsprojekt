import pandas as pd
import matplotlib.pyplot as plt

# Datei laden
file_path = r"outputs_monte_carlo\monte_carlo_results.xlsx"
df = pd.read_excel(file_path, sheet_name="All_Iterations")

# Szenarien
scenarios = ["Moderat", "Selektiv", "Aggressiv"]

# Gemeinsame Darstellungsachse
x_min = -16
x_max = 10

for scenario in scenarios:
    values = df.loc[df["scenario"] == scenario, "Delta_R_MioCHF"].dropna()
    mean_value = values.mean()

    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=30, range=(x_min, x_max), edgecolor="black")
    plt.xlim(x_min, x_max)

    # Mean-Linie
    plt.axvline(mean_value, linestyle="--", linewidth=1.5, color="black", label="Mean")

    plt.title(f"Verteilung von ΔR – {scenario}")
    plt.xlabel("ΔR (Mio. CHF)")
    plt.ylabel("Häufigkeit")
    plt.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    plt.savefig(f"histogram_{scenario.lower()}.png", dpi=300, bbox_inches="tight")
    plt.show()