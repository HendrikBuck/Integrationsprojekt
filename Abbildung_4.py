import matplotlib.pyplot as plt
import numpy as np

# daten
q_max = 12
Q = np.linspace(0, q_max, 500)
MC = 15  # grenzkosten

# nachfragefunktion p(q)
def p_inelastisch(q): return 100 - 8 * q
def p_elastisch(q): return 60 - 3 * q

# schnittpunkte berechen
p_H = 76  # preis für konzerne
q_H = (100 - p_H) / 8  # menge, bei der die kurve p_H schneidet (q=3)

p_L = 36  # preis für lokale
q_L = (60 - p_L) / 3   # menge, bei der die Kurve p_L schneidet (q=8)

plt.figure(figsize=(10, 7))

# kurven zeichnen
plt.plot(Q, p_inelastisch(Q), color='#a3cae6', lw=2.5, label='Nachfrage inelastisch (Konzerne)')
plt.plot(Q, p_elastisch(Q), color='#bad8d0', lw=2.5, linestyle='--', label='Nachfrage elastisch (Lokale)')
plt.axhline(y=MC, color='black', lw=1.5, label='Grenzkosten (MC)')

# gewinnflächen
# inelastisches rechteck von 0 bis q_H und von MC bis p_H
plt.fill_between([0, q_H], MC, p_H, color='#a3cae6', alpha=0.2)

# elastisch: rechteck von 0 bis q_L und von MC bis p_L
plt.fill_between([q_H, q_L], MC, p_L, color='#bad8d0', alpha=0.15, zorder=1)

# hilflinie zu schnittpunkten
#vertikal
plt.plot([q_H, q_H], [MC, p_H], color='#a3cae6', linestyle=':', lw=1.5)
plt.plot([q_L, q_L], [MC, p_L], color='#bad8d0', linestyle=':', lw=1.5)

#horizontal
plt.axhline(y=p_H, xmax=q_H/q_max, color='#a3cae6', linestyle=':', lw=1)
plt.axhline(y=p_L, xmax=q_L/q_max, color='#bad8d0', linestyle=':', lw=1)

# achsenbeschriftung
plt.text(-0.5, p_H, '$P_{Konzerne}$', color='#a3cae6', fontweight='bold', ha='right', va='center')
plt.text(-0.5, p_L, '$P_{Lokale}$', color='#bad8d0', fontweight='bold', ha='right', va='center')
plt.text(q_H, MC-5, '$Q_H$', color='#a3cae6', ha='center')
plt.text(q_L, MC-5, '$Q_L$', color='#bad8d0', ha='center')
plt.text(-0.5, MC, 'MC', color='black', ha='right', va='center')

# styling
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

plt.xlabel('Vermietete Fläche (Q)', loc='right')
plt.ylabel('Mietpreis (P)', loc='top', rotation=0)

plt.ylim(0, 110)
plt.xlim(0, 12)
plt.legend(frameon=False, loc='upper right')

plt.tight_layout()
plt.show()
