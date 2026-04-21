"""
OT-2  Step 3 – EtOH addition → mix → [centrifuge] → decant supernatant
               → re-lysis buffer → [60 °C incubate] → EtOH wash
Time  : ~50 min (+10 min incubation, +1 min centrifuge)
Tips  : p1000 ×99 total (1 EtOH + 48 mix + 48 decant + 1 relysis + 1 wash)
        Requires 2 full p1000 tip racks on deck before starting.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml       – EtOH (150 mL 200-proof EtOH)
Slot 2 : custom_48_wellplate_7000ul   – 48-well sample plate
Slot 3 : nest_1_reservoir_195ml       – re-lysis buffer (20 mL); re-used for EtOH wash
Slot 5 : custom_48_wellplate_7000ul   – liquid trash (open container, e.g. empty tip box)
Slot 8 : opentrons_96_filtertiprack_1000ul
Slot 9 : opentrons_96_filtertiprack_1000ul

Pipettes
--------
Right : p1000_single_gen2
"""

import math, sys, os
try:
    sys.path.insert(0, '/data/user_storage/cfRNA')
    from config import *
except ImportError:
    LYSIS_VOL=float(os.environ.get('LYSIS_VOL','1800'))
    ETOH_VOL=float(os.environ.get('ETOH_VOL','3000'))
    START_COL=int(os.environ.get('START_COL','0'))
    STOP_COL=int(os.environ.get('STOP_COL','6'))
    FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    WELLPLATE_2ML='nest_96_wellplate_2ml_deep'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='nest_96_wellplate_2ml_deep'       # simulation substitute
    NORGEN_FILTER='nest_96_wellplate_2ml_deep'  # simulation substitute
    ZYMO_FILTER='nest_96_wellplate_2ml_deep'    # simulation substitute

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 3 – EtOH / Centrifuge / Decant / Re-lysis',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

DECANT_HEIGHTS = [25, 20, 15, 6, 2, 1.2]
DECANT_VOL     = 980   # µL per aspirate step


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a     = protocol.load_labware(TIPS_1000, 9)
    tips_b     = protocol.load_labware(TIPS_1000, 8)
    plate      = protocol.load_labware(PLATE_48,  2)
    etoh_res   = protocol.load_labware(RESERVOIR_1, 1)
    lysis_res  = protocol.load_labware(RESERVOIR_1, 3)
    liq_trash  = protocol.load_labware(PLATE_48,   5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_a, tips_b])

    etoh_src  = etoh_res.wells()[0]
    lysis_src = lysis_res.wells()[0]

    # ════════════════════════════════════════════════════════════════════
    # PHASE 0 – Add EtOH (3000 µL/well = 3 × 1000 µL; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3A  ▶  Place sealed 48-well plate at SLOT 2. "
        "Add 150 mL 200-proof EtOH to reservoir at SLOT 1. "
        "Load 2 full p1000 tip racks at SLOTS 8 and 9. "
        "Remove seal from plate. Resume when ready."
    )

    etoh_iters    = math.ceil(ETOH_VOL / 1000)           # 3000 → 3
    etoh_per_disp = round(ETOH_VOL / etoh_iters, 1)      # 1000 µL

    p1000.pick_up_tip()
    for col in plate.columns():
        for well in col:
            for _ in range(etoh_iters):
                p1000.aspirate(etoh_per_disp, etoh_src.bottom(2))
                p1000.dispense(etoh_per_disp, well.top(-5))
    p1000.drop_tip()

    # ── Mix each well individually at 3 heights ───────────────────────
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
    # PHASE 1 – Decant supernatant (~5.88 mL/well; new tip per well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3C  ▶  Place open liquid-waste container at SLOT 5. Resume."
    )

    trash_cols = liq_trash.columns()

    for col_idx, col in enumerate(plate.columns()):
        trash_dest = trash_cols[col_idx % len(trash_cols)][0]
        for well in col:
            p1000.pick_up_tip()
            for h in DECANT_HEIGHTS:
                p1000.aspirate(DECANT_VOL, well.bottom(h), rate=0.5)
                p1000.air_gap(10)
                p1000.dispense(DECANT_VOL + 10, trash_dest.bottom(35))
                protocol.delay(seconds=0.2)
                p1000.blow_out(trash_dest.bottom(35))
                p1000.aspirate(10, trash_dest.bottom(35))
            p1000.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # PHASE 2 – Add re-lysis buffer (300 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3D  ▶  Remove liquid-waste container from SLOT 5. "
        "Add 20 mL preheated lysis buffer to reservoir at SLOT 3. "
        "Move plate to SLOT 2. Resume."
    )

    p1000.pick_up_tip()
    for col in plate.columns():
        for well in col:
            p1000.aspirate(300, lysis_src.bottom(2))
            p1000.dispense(300, well.top(-20))
    p1000.drop_tip()

    protocol.pause(
        "STEP 3E  ▶  Seal plate and vortex ≥30 s. "
        "Incubate at 60 °C for 10 min. "
        "If this is the FIRST batch of 48: keep incubator at 60 °C. "
        "If this is the SECOND batch: set incubator to 37 °C for DNase. "
        "Resume after incubation completes."
    )

    # ════════════════════════════════════════════════════════════════════
    # PHASE 3 – Add EtOH wash (300 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3F  ▶  Empty SLOT 3 reservoir and add 20 mL 200-proof EtOH. "
        "Remove seal from plate and return to SLOT 2. Resume."
    )

    p1000.pick_up_tip()
    for col in plate.columns():
        for well in col:
            p1000.aspirate(300, lysis_src.bottom(2))
            p1000.dispense(300, well.top(-20))
    p1000.drop_tip()

    protocol.comment(
        "Step 3 complete. Seal plate and vortex 1 min. "
        "Proceed to Step 4 (transfer to Norgen filter plate)."
    )
