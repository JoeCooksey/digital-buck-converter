# 2026-06-04 — Phase 1: open-loop LTspice simulation of the ideal buck

**Phase:** 1 (Open-loop simulation)
**Time:** deep block
**Files:** `Phase1/idealBuckConverter/`

## What I did
- Built the open-loop buck power stage in **LTspice** (`buckConverter.asc`) — ideal voltage-controlled switch (`SW` model, Ron = 0.05 Ω) high-side, **1N5819 Schottky** as the freewheeling diode (asynchronous buck for now; the synchronous low-side FET comes with the Phase 2 power-stage design).
- Used the Phase 0 design values: `V_in = 12 V`, `L = 33 µH` (Rser 0.05 Ω), `C = 44 µF` (Rser 0.05 Ω), `R_load = 1.667 Ω` (≙ 5 V / 3 A), switching at **100 kHz** (`PULSE` period 10 µs).
- Drove the gate open-loop with a fixed on-time and **swept duty** via `.step param Ton list 3u 4.17u 4.5u 5u` (D = 0.30 / 0.417 / 0.45 / 0.50) to see V_out vs. D.
- Ran a 2 ms `.tran`; captured startup, steady-state output ripple, inductor current, and the duty sweep. (Screenshots in the folder.)

## What I found / measured
- **It works** — V_out charges up and settles to a clean regulated DC with the expected triangular inductor current. Topology and switching behavior confirmed.
- **Steady-state DC offset.** At the *ideal* duty `D = 0.417` (`Ton = 4.17 µs`) V_out settles to **≈ 4.62–4.64 V**, not 5.0 V. The shortfall is the **Schottky forward drop (~0.4 V) plus the switch/L/C series resistances** — real silicon needs a *higher* duty than `V_out/V_in`. The sweep quantifies it:

  | Ton | D | V_out (settled) |
  |---|---|---|
  | 3.0 µs | 0.30 | ≈ 3.25 V |
  | 4.17 µs | 0.417 | ≈ 4.62 V |
  | 4.5 µs | 0.45 | ≈ 4.97 V |
  | 5.0 µs | 0.50 | ≈ 5.58 V |

  → a true 5 V open-loop needs **D ≈ 0.45**, not 0.417. This DC error is exactly what the closed loop will null out in Phase 5.
- **Output ripple ≈ 45 mV pk-pk** (≈ 4.595 → 4.640 V), just under the **< 50 mV** spec target. ✓
- **Inductor ripple ≈ 0.95 A** (current swings ~2.30 → ~3.25 A, avg ≈ 2.78 A) ≈ **30 % of I_out** — right on the ~0.9 A design target. ✓
- **Startup ringing validates the Phase 0 plant.** Open-loop start is underdamped: V_out overshoots to **~6.1 V (~30 %)**, rings, and settles by **~0.8 ms**. The ring frequency matches `f₀ ≈ 4.2 kHz` from the hand-derived `G_vd(s)` — the LC double-pole shows up in the time domain exactly where the model said it would.

## Why it matters
This closes the loop between Phase 0 theory and a working power stage: ripple and inductor-ripple hit their targets, and the underdamped startup ring is the same resonance the `G_vd(s)` double-pole predicted. The open-loop DC error (diode + parasitics push the needed duty above the ideal `V_out/V_in`) makes the case for closed-loop regulation concrete — there's a real, measurable offset for the compensator to remove.

## Next (Phase 2)
- Move from the ideal switch + diode to a **synchronous** power stage (2× N-ch MOSFET + gate driver + dead-time) and pick real parts → BOM.
- Re-check duty, ripple, and conduction/switching losses with device models; size L and C against the measured ripple.
- Carry the "real D > ideal D" offset forward as the DC operating point the Phase 5 compensator regulates around.

## Notes
- The LTspice waveform dump (`*.raw`, ~5.7 MB) is git-ignored — it regenerates from `buckConverter.asc`. The schematic, run log, and exported plots are committed.
