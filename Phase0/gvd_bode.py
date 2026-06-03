"""
Phase 0 — Control-to-output transfer function of a voltage-mode buck converter.

G_vd(s) describes how a small wiggle in the duty cycle d moves the output
voltage V_out. For a voltage-mode buck it is a second-order system: the output
L-C filter forms a resonant double-pole. This script builds G_vd(s), prints the
resonant frequency, and plots its Bode diagram.

    G_vd(s) = V_in / ( 1 + s/(Q*w0) + (s/w0)^2 )      with  w0 = 1/sqrt(L*C)

Why this matters: notice the phase plunges ~180 deg as you sweep past f0. A
double-pole eats 180 deg of phase margin in a hurry, which is exactly why a
plain integrator won't stabilize this loop -- you'll need a Type-III
compensator later to claw that phase back.
"""

import numpy as np
import matplotlib.pyplot as plt
import control as ct

# ----------------------------------------------------------------------------
# Parameters (Phase 0 power stage)
# ----------------------------------------------------------------------------
L = 33e-6        # output inductor [H]
C = 44e-6        # output capacitor [F]
V_in = 12.0      # input voltage [V]  -> sets the DC gain of G_vd

# Q (damping) is set by the load and parasitics. For an ideal buck driving a
# resistive load R:   Q = R * sqrt(C/L) = R / Z0,  where Z0 = sqrt(L/C).
R_load = 5.0                       # load resistance [ohm]
Z0 = np.sqrt(L / C)                # characteristic impedance of the LC tank [ohm]
Q = R_load / Z0                    # quality factor (dimensionless)

# ----------------------------------------------------------------------------
# Resonant frequency
# ----------------------------------------------------------------------------
w0 = 1.0 / np.sqrt(L * C)          # [rad/s]
f0 = w0 / (2.0 * np.pi)            # [Hz]

print(f"Z0  = sqrt(L/C)        = {Z0:.3f} ohm")
print(f"Q   = R_load / Z0      = {Q:.3f}")
print(f"w0  = 1/sqrt(L*C)      = {w0:.1f} rad/s")
print(f"f0  = 1/(2*pi*sqrt(LC)) = {f0/1e3:.2f} kHz")
print(f"DC gain G_vd(0)        = {V_in:.1f} V  ({20*np.log10(V_in):.1f} dB)")

# ----------------------------------------------------------------------------
# Build G_vd(s) as a control transfer function
#   denominator = (1/w0^2) s^2 + (1/(Q*w0)) s + 1
# ----------------------------------------------------------------------------
num = [V_in]
den = [1.0 / w0**2, 1.0 / (Q * w0), 1.0]
G_vd = ct.tf(num, den)
print("\nG_vd(s) =", G_vd)

# ----------------------------------------------------------------------------
# Bode plot
# ----------------------------------------------------------------------------
# Sweep from two decades below f0 to two decades above it.
w = np.logspace(np.log10(w0) - 2, np.log10(w0) + 2, 2000)
mag, phase, omega = ct.frequency_response(G_vd, w)

freqs_hz = omega / (2.0 * np.pi)
mag_db = 20.0 * np.log10(mag)
phase_deg = np.degrees(phase)

fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

# --- Magnitude ---
ax_mag.semilogx(freqs_hz, mag_db, color="C0", lw=2)
ax_mag.axvline(f0, color="C3", ls="--", lw=1.2, label=f"$f_0$ = {f0/1e3:.2f} kHz")
ax_mag.axhline(20 * np.log10(V_in), color="gray", ls=":", lw=1,
               label=f"DC gain = {20*np.log10(V_in):.1f} dB")
peak_db = mag_db.max()
ax_mag.annotate(f"LC peak  ({peak_db:.1f} dB,  Q={Q:.1f})",
                xy=(f0, peak_db), xytext=(f0 * 1.6, peak_db + 2),
                arrowprops=dict(arrowstyle="->", color="C3"), color="C3")
ax_mag.set_ylabel("Magnitude [dB]")
ax_mag.set_title(r"Buck control-to-output  $G_{vd}(s) = V_{in}\,/\,(1 + s/Q\omega_0 + (s/\omega_0)^2)$")
ax_mag.grid(True, which="both", alpha=0.3)
ax_mag.legend(loc="lower left")

# --- Phase ---
ax_phase.semilogx(freqs_hz, phase_deg, color="C0", lw=2)
ax_phase.axvline(f0, color="C3", ls="--", lw=1.2)
ax_phase.axhline(-90, color="gray", ls=":", lw=1, label="$-90°$ (at $f_0$)")
ax_phase.annotate("phase falls ~180° through $f_0$\n(why you need Type-III)",
                  xy=(f0, -90), xytext=(f0 / 60, -135), color="C3")
ax_phase.set_ylabel("Phase [deg]")
ax_phase.set_xlabel("Frequency [Hz]")
ax_phase.set_yticks([0, -45, -90, -135, -180])
ax_phase.grid(True, which="both", alpha=0.3)
ax_phase.legend(loc="lower left")

fig.tight_layout()
out_png = "gvd_bode.png"
fig.savefig(out_png, dpi=130)
print(f"\nSaved Bode plot -> {out_png}")
plt.show()
