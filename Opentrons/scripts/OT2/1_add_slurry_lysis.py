"""
OT-2  Step 1 – Add slurry + lysis buffer to 48-well plate
Time  : ~8 min  (OT-1 was ~5 min; OT-2 needs 9 lysis dispenses vs 2)
Tips  : 1 row 200 µL (slurry) + 1 row 200 µL (lysis) = 2 rows total

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml       – lysis buffer A + 1.2% B-ME
Slot 2 : custom_48_wellplate_7000ul   – plate (moved here before lysis step)
Slot 4 : nest_12_reservoir_15ml       – slurry in well A1 (col 1)
Slot 5 : custom_48_wellplate_7000ul   – plate (starts here for slurry step)
Slot 9 : opentrons_96_filtertiprack_200ul

Pipettes
--------
Left  : p300_multi_gen2
"""

import math
import sys, os
sys.path.append('/data/user_storage/cfRNA')
from config import *

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 1 – Slurry + Lysis Buffer',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': API_LEVEL,
}


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    tips_200   = protocol.load_labware(TIPS_200,      9)
    plate_A    = protocol.load_labware(PLATE_48,      5)   # slurry step
    plate_B    = protocol.load_labware(PLATE_48,      2)   # lysis step
    slurry_res = protocol.load_labware(RESERVOIR_12,  4)   # slurry → well A1
    lysis_res  = protocol.load_labware(RESERVOIR_1,   1)   # lysis buffer

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips_200])

    slurry_src = slurry_res.wells_by_name()['A1']
    lysis_src  = lysis_res.wells()[0]

    # ════════════════════════════════════════════════════════════════════
    # STEP A – Slurry (200 µL per column, slow aspirate)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 1A  ▶  Place 48-well plate at SLOT 5. "
        "Vortex preheated slurry and add 10.5 mL to col 1 of the "
        "12-col reservoir at SLOT 4. Resume when ready."
    )

    p300.pick_up_tip()
    for col in plate_A.columns():
        p300.mix(1, 100, slurry_src.bottom(2))
        p300.aspirate(190, slurry_src.bottom(2), rate=0.1)   # slow – viscous slurry
        protocol.delay(seconds=1.5)
        p300.air_gap(10)
        p300.dispense(200, col[0].top(-30))
        p300.blow_out(col[0].top(-30))
    p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # STEP B – Lysis buffer (1800 µL per column; 9 × 200 µL dispenses)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 1B  ▶  Move 48-well plate to SLOT 2. "
        "Add ~40 mL preheated lysis buffer (+ 1.2% B-ME) to the "
        "reservoir at SLOT 1 (refill in ~40 mL batches to prevent "
        "crystallisation). Resume when ready."
    )

    iters    = math.ceil(LYSIS_VOL / 200)        # 1800 → 9
    per_disp = round(LYSIS_VOL / iters, 1)       # 200.0 µL

    p300.pick_up_tip()
    for col in plate_B.columns():
        for _ in range(iters):
            p300.aspirate(per_disp, lysis_src.bottom(2))
            p300.dispense(per_disp, col[0].top(-20))
    p300.drop_tip()

    protocol.comment(
        "Step 1 complete. "
        "Proceed manually: transfer samples into plate at slot 2 "
        "using a multichannel P1000 (mix each column ≥5×). "
        "Seal plate and incubate at 60 °C for 10 min."
    )
