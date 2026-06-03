# Digitally Controlled Synchronous Buck Converter

A from-scratch **12 V → 5 V @ 3 A** synchronous buck converter, regulated by a closed control loop I design myself and run on an **STM32G4** microcontroller. The goal is to take one power converter all the way from first-principles theory → simulation → custom PCB → bring-up → digital compensator → measured closed-loop validation, and document every step.

> **Status:** Phase 0 complete (theory & small-signal model). Actively building — see [`docs/devlog/`](docs/devlog/) for the running log.

## Target specification

| Parameter | Value |
|---|---|
| Topology | Synchronous buck (2× N-channel MOSFET) |
| Input | 12 V DC (bench supply, current-limited) |
| Output | 5 V @ 3 A (15 W) |
| Switching frequency | 100 kHz (→ 300–500 kHz later) |
| Control | Digital voltage-mode (STM32G4, design-by-emulation) |
| Output ripple target | < 50 mV |
| Inductor ripple | ~30 % of I_out (≈ 0.9 A) |

*Low-voltage by design — 12 V means no mains, no shock hazard. Brought up behind a current limit every time.*

## Phase 0 — Theory & small-signal model ✅

Derived the buck from first principles (volt-second balance, CCM duty `D = V_out/V_in`, ripple equations — see [`Phase0/HandNotesAndDerivations.pdf`](Phase0/HandNotesAndDerivations.pdf)) and built the **control-to-output transfer function** `G_vd(s)` — the plant the digital compensator will later stabilize.

For a voltage-mode buck the output L–C filter forms a resonant **double-pole**:

```
G_vd(s) = V_in / ( 1 + s/(Q·ω₀) + (s/ω₀)² )

ω₀ = 1/√(LC)        Q = R_load·√(C/L) = R_load / Z₀
L = 33 µH,  C = 44 µF,  V_in = 12 V,  R_load = 5 Ω  →  f₀ ≈ 4.2 kHz
```

![Control-to-output Bode plot](Phase0/gvd_bode.png)

**Key takeaway:** the phase plunges ~180° as the sweep passes `f₀`. A double-pole burns phase margin fast — which is exactly why a plain integrator can't stabilize this loop and a **Type-III compensator** is needed in Phase 5 to claw the phase back. Identifying this now is the whole point of modeling the plant before touching hardware.

Reproduce:

```bash
python -m venv ee-venv
ee-venv/Scripts/activate        # Windows  (source ee-venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
python Phase0/gvd_bode.py
```

## Build roadmap

| Phase | What | Status |
|---|---|---|
| 0 | Theory & small-signal model (G_vd Bode) | ✅ Done |
| 1 | Open-loop LTspice simulation (verify D, ripple, dead-time) | ⏳ Next |
| 2 | Power-stage design & BOM | ☐ |
| 3 | PCB layout in KiCad → JLCPCB | ☐ |
| 4 | Bring-up & open-loop bench test | ☐ |
| 5 | Digital control firmware (compensator → difference equation in the ISR) | ☐ |
| 6 | Closed-loop tuning & validation (loop-gain Bode/SFRA, transient, efficiency) | ☐ |
| 7 | Document & publish | (ongoing) |

## Repository layout

```
Phase0/           hand derivations (PDF) + G_vd(s) model & Bode plot
docs/devlog/      dated entry per work session — the running build log
requirements.txt  Python modeling toolchain (numpy, scipy, matplotlib, control)
```
Later phases add a KiCad project (hardware), an STM32CubeIDE project (firmware), and measured-data plots. The local Python venv (`ee-venv/`) is git-ignored — recreate it from `requirements.txt`.

## Tooling

Python (numpy / scipy / matplotlib / python-control) · LTspice · KiCad · STM32G4 (Nucleo-G474RE) · STM32CubeIDE

---
*Build log and design notes in [`docs/devlog/`](docs/devlog/). This repo documents the process, not just the result.*
