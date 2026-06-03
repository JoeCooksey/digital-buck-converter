# 2026-06-03 — Phase 0 complete: theory & small-signal model

**Phase:** 0 (Theory & modeling)
**Time:** deep block

## What I did
- Derived the buck converter from first principles by hand: volt-second balance, CCM duty cycle `D = V_out/V_in = 5/12 ≈ 0.417`, inductor-ripple and output-ripple equations. (→ `Phase0/HandNotesAndDerivations.pdf`)
- Built the **control-to-output transfer function** `G_vd(s)` in Python (python-control) — the small-signal plant the digital loop will later compensate. (→ `Phase0/gvd_bode.py`, `Phase0/gvd_bode.png`)

## What I found / measured
- `G_vd(s)` is a second-order system: the output L–C filter is a resonant double-pole.
- With L = 33 µH, C = 44 µF: `f₀ = 1/(2π√(LC)) ≈ 4.2 kHz`.
- `Q = R_load / Z₀` where `Z₀ = √(L/C)` → at R_load = 5 Ω the LC tank peaks noticeably.
- Phase falls ~180° through `f₀` — confirms a plain integrator won't stabilize this; a **Type-III compensator** is required (Phase 5).

## Why it matters
Modeling the plant *before* hardware tells me the shape of the problem: a sharp double-pole that eats phase margin. Everything in the control design later is about recovering that phase.

## Next (Phase 1)
- Model the power stage in **LTspice**, verify D and ripple against the hand calcs, sweep load.
- Confirm the simulated Bode of the power stage matches this hand-derived `G_vd(s)`.
- First task next session: build the open-loop buck in LTspice with ideal switches at 100 kHz and check `V_out` settles to 5 V.
