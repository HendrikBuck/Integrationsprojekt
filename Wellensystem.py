import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.patches import Rectangle

# =========================================================
# EINSTELLUNGEN
# =========================================================
START_TIME = 6.0          # 06:00
END_TIME = 24.0           # 24:00
OPERATING_END = 23.5      # 23:30
SLOT_MIN = 5              # 5-Minuten-Slots

# TITLE = "Das Wellensystem: Abflugwellen folgen dicht auf Ankunftswellen"
SUBTITLE_BOLD = "Betriebszeiten"
SUBTITLE_NORMAL = " 06:00 – 23:30 Uhr"

# Farben
COLOR_STARTS = "#9FC8E6"      # hellblau
COLOR_LANDINGS = "#B7D7CF"    # hellgrün
COLOR_BAND = "#EAE7C8"        # hellgelb
COLOR_BORDER = "#E1B90E"      # gelb
COLOR_GRID = "#A9A9A9"
COLOR_ZERO = "#9A9A9A"
TITLE_COLOR = "#244B8F"

# =========================================================
# ZEITRASTER
# =========================================================
slot_h = SLOT_MIN / 60.0
times = np.arange(START_TIME, END_TIME + slot_h, slot_h)
n = len(times)

dep = np.zeros(n)   # Starts (oben, positiv)
arr = np.zeros(n)   # Landungen (unten, später negativ)

# =========================================================
# HILFSFUNKTIONEN
# =========================================================
def h_to_idx(h):
    """Stundenwert (z.B. 7.5) -> Slot-Index."""
    return int(round((h - START_TIME) * 60 / SLOT_MIN))

def add_pattern(series, start_h, pattern):
    """
    Fügt ab start_h die Werte aus pattern slotweise ein.
    pattern = Liste ganzzahliger Werte pro 5-Minuten-Slot.
    """
    i0 = h_to_idx(start_h)
    for k, val in enumerate(pattern):
        idx = i0 + k
        if 0 <= idx < len(series):
            series[idx] += val

def add_noise(series, seed=42, prob=0.12, low=1, high=1):
    """
    Kleine unregelmässige Ausschläge, damit die Fläche natürlicher aussieht.
    """
    rng = np.random.default_rng(seed)
    noise_mask = rng.random(len(series)) < prob
    noise_vals = rng.integers(low, high + 1, size=len(series))
    series += noise_mask * noise_vals

def time_labels(values):
    labels = []
    for h in values:
        hh = int(h)
        mm = int(round((h - hh) * 60))
        labels.append(f"{hh:02d}:{mm:02d}")
    return labels

# =========================================================
# WELLEN DEFINIEREN
# =========================================================

# ---------------------------------------------------------
# LANDUNGEN (unten)
# ---------------------------------------------------------
add_pattern(arr, 6.00, [1, 4, 0, 0, 1, 0])
add_pattern(arr, 6.50, [1, 0, 1, 0, 2, 0, 3, 0, 3, 0, 4, 0, 3, 0, 2, 0, 2, 0, 1, 0])

add_pattern(arr, 10.75, [2, 2, 4, 2, 3, 2, 3, 0, 2, 3, 2, 4])

add_pattern(arr, 11.92, [1, 2, 0, 2, 4, 2, 3, 2, 3, 1, 2, 0, 2])

add_pattern(arr, 15.50, [1, 3, 3, 2, 4, 3, 2, 4, 2, 3, 2, 0, 2, 3, 2, 0, 2])

add_pattern(arr, 19.83, [1, 2, 0, 2, 3, 2, 1, 3, 2, 2, 1])

add_pattern(arr, 21.17, [2, 2, 1, 3, 2, 4, 2, 3, 2, 1, 3, 2, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])

# ---------------------------------------------------------
# STARTS (oben)
# ---------------------------------------------------------
add_pattern(dep, 6.25, [1, 0, 1, 0, 0, 0, 2, 3, 3, 4, 2, 4, 2, 1, 0, 0, 0])

add_pattern(dep, 8.08, [1, 0, 0, 0, 1, 1, 1, 0, 1, 2, 0, 1, 0, 0, 1, 0, 2, 0, 3, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0])

add_pattern(dep, 11.58, [1, 0, 0, 2, 4, 3, 3, 3, 3, 2, 4, 3, 4, 3, 4, 2, 1, 2, 0, 1, 0, 0, 1])

add_pattern(dep, 15.25, [1, 0, 0, 0, 1, 0, 0, 0, 0])

add_pattern(dep, 16.50, [1, 1, 2, 2, 4, 3, 3, 4, 2, 3, 2, 2, 4, 2, 0, 0, 1, 0, 0, 1, 0])

add_pattern(dep, 20.58, [1, 0, 0, 1, 0, 0, 2, 2, 1, 3, 2, 1, 2, 1, 0, 1, 0, 0, 0, 0, 0, 0, 5, 1, 0, 0, 1])

# Kleine Unregelmässigkeiten ergänzen
add_noise(dep, seed=1, prob=0.08, low=1, high=1)
add_noise(arr, seed=2, prob=0.08, low=1, high=1)

# Begrenzen auf Maximalwerte wie in der Vorlage
dep = np.clip(dep, 0, 5)
arr = np.clip(arr, 0, 5)

# Landungen negativ
arr = -arr

# =========================================================
# PLOT
# =========================================================
fig, ax = plt.subplots(figsize=(13.5, 9), dpi=140)

# Hintergrund leicht grau
fig.patch.set_facecolor("#F2F2F2")
ax.set_facecolor("#F2F2F2")

# Betriebszeitenband oben
band_y0 = 5.25
band_height = 0.75
ax.add_patch(
    Rectangle(
        (START_TIME, band_y0),
        OPERATING_END - START_TIME,
        band_height,
        facecolor=COLOR_BAND,
        edgecolor="none",
        zorder=0
    )
)

# Vertikale gelbe Linien
ax.axvline(START_TIME, color=COLOR_BORDER, linewidth=1.3, zorder=5)
ax.axvline(23.5, color=COLOR_BORDER, linewidth=1.3, zorder=5)

# Horizontale Gridlines
for y in range(-5, 6):
    ax.axhline(y, color=COLOR_GRID, linewidth=0.7, alpha=0.75, zorder=0)

# Null-Linie
ax.axhline(0, color=COLOR_ZERO, linewidth=1.6, zorder=2)

# Flächen
ax.fill_between(times, 0, dep, color=COLOR_STARTS, alpha=0.95, zorder=3)
ax.fill_between(times, 0, arr, color=COLOR_LANDINGS, alpha=0.95, zorder=3)

# Limits
ax.set_xlim(5.0, 24.6)
ax.set_ylim(-5.4, 6.0)

# X-Achse: 30-Minuten-Ticks
xticks = np.arange(6.0, 24.5, 0.5)
ax.set_xticks(xticks)
ax.set_xticklabels(time_labels(xticks), rotation=90, fontsize=9)
ax.tick_params(axis="x", length=0, pad=8)

# Y-Achse: Labels als positive Zahlen oben und unten
yticks = np.arange(-5, 6, 1)
ax.set_yticks(yticks)
ax.set_yticklabels([str(abs(y)) for y in yticks], fontsize=10)
ax.tick_params(axis="y", length=0, pad=8)

# Achsenbeschriftung OHNE Stern
ax.set_ylabel("Anzahl Flüge pro 5 Minuten", fontsize=13)

# # Titel
# fig.text(
#     0.09, 0.92,
#     TITLE,
#     fontsize=21,
#     color=TITLE_COLOR,
#     ha="left",
#     va="center"
# )

# Untertitel im Band
ax.text(
    (START_TIME + OPERATING_END) / 2,
    band_y0 + band_height / 2,
    SUBTITLE_BOLD,
    fontsize=13,
    fontweight="bold",
    ha="right",
    va="center"
)
ax.text(
    (START_TIME + OPERATING_END) / 2,
    band_y0 + band_height / 2,
    SUBTITLE_NORMAL,
    fontsize=13,
    ha="left",
    va="center"
)

# Labels "Starts" und "Landungen"
ax.text(6.95, 4.45, "Starts", fontsize=16, ha="left", va="center")
ax.text(6.95, -4.55, "Landungen", fontsize=16, ha="left", va="center")

# Einfache Kreissymbole links
ax.scatter([6.5], [4.45], s=450, color=COLOR_STARTS, edgecolor="none", zorder=6)
ax.scatter([6.5], [-4.55], s=450, color=COLOR_LANDINGS, edgecolor="none", zorder=6)
ax.text(6.5, 4.45, "✈", ha="center", va="center", fontsize=18, color="white", rotation=20, zorder=7)
ax.text(6.5, -4.55, "✈", ha="center", va="center", fontsize=18, color="white", rotation=-20, zorder=7)

# Rahmen entfernen
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout(rect=[0.08, 0.08, 0.97, 0.9])
plt.savefig("wellensystem.png", dpi=300, bbox_inches="tight")
plt.show()