"""
OT-2  Step 3 – EtOH addition → mix → [centrifuge] → decant supernatant
               → re-lysis buffer → [60 °C incubate] → EtOH wash
Time  : ~35 min (+10 min incubation, +1 min centrifuge)
Tips  : P300 ×3 rows (EtOH + lysis + EtOH wash)
        P1000 ×48 (mix) + ×48 (decant) = 96 tips → 1 full P1000 tip rack
        Mid-way prompt to replace P1000 tip rack.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml       – EtOH col A  (150 mL 200-proof EtOH)
Slot 2 : custom_48_wellplate_7000ul   – 48-well sample plate (B1)
Slot 3 : nest_1_reservoir_195ml       – re-lysis buffer (20 mL); re-used for EtOH wash
Slot 5 : custom_48_wellplate_7000ul   – liquid trash (open container, e.g. empty tip box)
Slot 8 : opentrons_96_filtertiprack_1000ul
Slot 9 : opentrons_96_filtertiprack_200ul

Pipettes
--------
Left  : p300_multi_gen2
Right : p1000_single_gen2
"""

import math, sys, os
sys.path.append('/data/user_storage/cfRNA')
from config import *

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 3 – EtOH / Centrifuge / Decant / Re-lysis',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': API_LEVEL,
}

# Heights (mm from bottom) used for progressive supernatant removal
DECANT_HEIGHTS = [25, 20, 15, 6, 2, 1.2]
DECANT_VOL     = 980   # µL per aspirate step


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    tips_200   = protocol.load_labware(TIPS_200,  9)
    tips_1000  = protocol.load_labware(TIPS_1000, 8)
    plate      = protocol.load_labware(PLATE_48,  2)
    etoh_res   = protocol.load_labware(RESERVOIR_1, 1)   # EtOH source
    lysis_res  = protocol.load_labware(RESERVOIR_1, 3)   # re-lysis / later EtOH wash
    liq_trash  = protocol.load_labware(PLATE_48,   5)    # open container acting as liquid waste

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300  = protocol.load_instrument('p300_multi_gen2',   'left',  tip_racks=[tips_200])
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_1000])

    etoh_src  = etoh_res.wells()[0]
    lysis_src = lysis_res.wells()[0]

    # ════════════════════════════════════════════════════════════════════
    # PHASE 0 – Add EtOH (3000 µL/col = 15 × 200 µL with P300 multi)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3A  ▶  Place sealed 48-well plate at SLOT 2. "
        "Add 150 mL 200-proof EtOH to reservoir at SLOT 1. "
        "Remove seal from plate. Resume when ready."
    )

    etoh_iters    = math.ceil(ETOH_VOL / 200)           # 3000 → 15
    etoh_per_disp = round(ETOH_VOL / etoh_iters, 1)     # 200 µL

    p300.pick_up_tip()
    for col in plate.columns():
        for _ in range(etoh_iters):
            p300.aspirate(etoh_per_disp, etoh_src.bottom(2))
            p300.dispense(etoh_per_disp, col[0].top(-5))
    p300.drop_tip()

    # ── Mix each well individually with P1000 at 3 heights ───────────
    for col in plate.columns():
        for well in col:
            p1000.pick_up_tip()
            p1000.mix(4, 900, well.bottom(2))
            p1000.mix(4, 900, well.bottom(20))
            p1000.mix(4, 900, well.bottom(34))
            p1000.drop_tip()

    protocol.pause(
        "STEP 3B  ▶  Seal plate at SLOT 2 and centrifuge 1 min at "
        "1,000 g (RT) to pellet slurry. Return to deck unsealed. Resume."
    )

    # ════════════════════════════════════════════════════════════════════
    # PHASE 1 – Decant supernatant (~5.88 mL/well in 6 progressive steps)
    #           P1000 single-channel; new tip per well; 48 tips total.
    #           Prompt to replace tip rack halfway (after col 3).
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3C  ▶  Place open liquid-waste container at SLOT 5. "
        "Place full P1000 tip rack at SLOT 8 (current rack will be "
        "exhausted during decant). Resume to begin supernatant removal."
    )

    trash_cols = liq_trash.columns()   # use successive trash cols as liquid waste zones
    tip_count  = 0

    for col_idx, col in enumerate(plate.columns()):

        # Prompt to replace tip rack after column 3 (24 wells used so far)
        if col_idx == 3:
            protocol.pause(
                "STEP 3C (cont.)  ▶  Replace P1000 tip rack at SLOT 8 "
                "with a fresh rack. Resume to continue decanting."
            )
            p1000.reset_tipracks()

        trash_dest = trash_cols[col_idx % len(trash_cols)][0]

        for well in col:
            p1000.pick_up_tip()
            for h in DECANT_HEIGHTS:
                p1000.aspirate(DECANT_VOL, well.bottom(h), rate=0.5)
                p1000.air_gap(10)
                p1000.dispense(DECANT_VOL + 10, trash_dest.bottom(35))
                protocol.delay(seconds=0.2)
                p1000.blow_out(trash_dest.bottom(35))
                # small re-aspirate to clear tip exterior
                p1000.aspirate(10, trash_dest.bottom(35))
            p1000.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # PHASE 2 – Add re-lysis buffer (300 µL/col = 2 × 150 µL)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3D  ▶  Remove liquid-waste container from SLOT 5. "
        "Add 20 mL preheated lysis buffer to reservoir at SLOT 3. "
        "Move plate to SLOT 2. Resume."
    )

    p300.pick_up_tip()
    for col in plate.columns():
        for _ in range(2):                       # 2 × 150 µL = 300 µL
            p300.aspirate(150, lysis_src.bottom(2))
            p300.dispense(150, col[0].top(-20))
    p300.drop_tip()

    protocol.pause(
        "STEP 3E  ▶  Seal plate and vortex ≥30 s. "
        "Incubate at 60 °C for 10 min. "
        "If this is the FIRST batch of 48: keep incubator at 60 °C. "
        "If this is the SECOND batch: set incubator to 37 °C for DNase. "
        "Resume after incubation completes."
    )

    # ════════════════════════════════════════════════════════════════════
    # PHASE 3 – Add EtOH wash (300 µL/col = 2 × 150 µL)
    #           Re-use SLOT 3 reservoir; user swaps lysis for EtOH.
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3F  ▶  Empty SLOT 3 reservoir and add 20 mL 200-proof EtOH. "
        "Remove seal from plate and return to SLOT 2. Resume."
    )

    p300.pick_up_tip()
    for col in plate.columns():
        for _ in range(2):
            p300.aspirate(150, lysis_src.bottom(2))
            p300.dispense(150, col[0].top(-20))
    p300.drop_tip()

    protocol.comment(
        "Step 3 complete. Seal plate and vortex 1 min. "
        "Proceed to Step 4 (transfer to Norgen filter plate)."
    )
