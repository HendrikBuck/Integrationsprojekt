import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(9, 8))

# achsen ausblenden
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_position(('data', 0))
ax.spines['bottom'].set_position(('data', 0))

# parameter für funktion
Y_max = 10
Y = np.linspace(0, Y_max, 100)

c1 = 0.5          # marginale konsumquote
Z0 = 1.5          # autonome ausgaben vor dem schock
delta_I = 1.5     # investitionsschock durch campus projekt

# Ffunktionen
Z_45 = Y                            # 45-grad-linie (Y = Z)
ZZ = Z0 + c1 * Y                    # ursprüngliche nachfrage
ZZ_prime = (Z0 + delta_I) + c1 * Y  # neue nachfrage nach investitionsschock

# gleichgewichte berechnen
Y_eq = Z0 / (1 - c1)                # altes gleichgewicht (A0)
Y_eq_prime = (Z0 + delta_I) / (1 - c1) # neues gleichgewicht (A1)

# linien
ax.plot(Y, Z_45, color='gray', linewidth=2.5, label='45° Linie')
ax.plot(Y, ZZ, color='#a3cae6', linewidth=3, label='ZZ')       
ax.plot(Y, ZZ_prime, color='#bad8d0', linewidth=3, label="ZZ'")

# multiplikatoreffekt
# A -> B
ax.annotate('', xy=(Y_eq, Y_eq + delta_I), xytext=(Y_eq, Y_eq),
            arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.6", color='black', lw=1.5))
# B -> C
ax.annotate('', xy=(Y_eq + delta_I, Y_eq + delta_I), xytext=(Y_eq, Y_eq + delta_I),
            arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.6", color='black', lw=1.5))
# C -> D
Y_C = Y_eq + delta_I
Z_D = (Z0 + delta_I) + c1 * Y_C
ax.annotate('', xy=(Y_C, Z_D), xytext=(Y_C, Y_C),
            arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.6", color='black', lw=1.5))
# D -> E
ax.annotate('', xy=(Z_D, Z_D), xytext=(Y_C, Z_D),
            arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.6", color='black', lw=1.5))

# punkte + beschriftungen
ax.plot(Y_eq, Y_eq, marker='o', color='black', markersize=6)
ax.text(Y_eq + 0.2, Y_eq - 0.4, '$A_0$', fontsize=14, fontstyle='italic')

ax.plot(Y_eq_prime, Y_eq_prime, marker='o', color='black', markersize=6)
ax.text(Y_eq_prime - 0.2, Y_eq_prime + 0.3, "$A_1$", fontsize=14, fontstyle='italic', weight='bold')

ax.text(Y_eq - 0.4, Y_eq + delta_I + 0.1, 'B', fontsize=12, fontstyle='italic')
ax.text(Y_eq + delta_I + 0.1, Y_eq + delta_I - 0.5, 'C', fontsize=12, fontstyle='italic')
ax.text(Y_C - 0.4, Z_D + 0.1, 'D', fontsize=12, fontstyle='italic')
ax.text(Z_D + 0.1, Z_D - 0.3, 'E', fontsize=12, fontstyle='italic')

# Linienbeschriftungen
ax.text(Y_max - 0.5, ZZ[-1], '$ZZ_0$', fontsize=14, weight='bold', color='#D32F2F', fontstyle='italic')
ax.text(Y_max - 0.5, ZZ_prime[-1] + 0.2, "$ZZ_1$", fontsize=14, weight='bold', color='#D32F2F', fontstyle='italic')

# investitionsschock pfeil
arrow_x = Y_eq_prime + 0.8
ax.annotate(r'$\Delta I$ (Investitionen für den Campus)', xy=(arrow_x, ZZ_prime[int(arrow_x*10)]), 
            xytext=(arrow_x, ZZ[int(arrow_x*10)]),
            arrowprops=dict(color='#D32F2F', width=4, headwidth=12, headlength=12),
            fontsize=12, color='#D32F2F', va='center', ha='left')

# hilfslinien
# Für A0
ax.plot([Y_eq, Y_eq], [0, Y_eq], color='gray', linestyle='--', alpha=0.7)
ax.plot([0, Y_eq], [Y_eq, Y_eq], color='gray', linestyle='--', alpha=0.7)
# Für A1
ax.plot([Y_eq_prime, Y_eq_prime], [0, Y_eq_prime], color='gray', linestyle='--', alpha=0.7)
ax.plot([0, Y_eq_prime], [Y_eq_prime, Y_eq_prime], color='gray', linestyle='--', alpha=0.7)

# achsenbeschriftung
ax.set_xticks([Y_eq, Y_eq_prime])
ax.set_xticklabels(['$Y_0$', "$Y_1$"], fontsize=14)

ax.set_yticks([Y_eq, Y_eq_prime])
ax.set_yticklabels(['$Y_0$', "$Y_1$"], fontsize=14)

ax.set_xlabel('Einkommen $Y$', fontsize=16, weight='bold', labelpad=20)
ax.set_ylabel('Nachfrage ($Z$), Produktion ($Y$)', fontsize=16, weight='bold', labelpad=20)

arc = patches.Arc((0, 0), 3, 3, angle=0, theta1=0, theta2=45, color='black', linewidth=1.2)
ax.add_patch(arc)
ax.text(0.6, 0.2, '45°', fontsize=12)

# darstellungsbereich anpassen
ax.set_xlim(0, Y_max + 1)
ax.set_ylim(0, Y_max + 1)

plt.tight_layout()
plt.show()
