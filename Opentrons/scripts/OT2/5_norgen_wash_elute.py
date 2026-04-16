"""
OT-2  Step 5 – Norgen filter: 3× wash → dry spin → elute
Time  : ~8 min robot  (+3+3+8+5+5 = 24 min centrifuge)
Tips  : P300 ×4 columns (3 washes + 1 elute); continues from column 6 of tip rack
        (columns 1-5 used in Step 3; hardcoded offset, see starting_tip below)

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml        – Norgen wash buffer (24 mL/wash)
Slot 2 : custom_norgen_96filterplate   – filter plate (on collection plate)
                                          batch 1: col 1 closest to user
                                          batch 2: col 12 closest to user (flip plate)
Slot 4 : nest_12_reservoir_15ml        – elution buffer in well A9 (col 9)
Slot 9 : opentrons_96_filtertiprack_200ul

env var : START_COL  (0-indexed; 0 for batch 1, 6 for batch 2)
          STOP_COL   (exclusive; 6 for batch 1, 12 for batch 2)

Pipettes
--------
Left  : p300_multi_gen2
"""

import sys, os
sys.path.append('/data/user_storage/cfRNA')
from config import *

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5 – Norgen Wash + Elute',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': API_LEVEL,
}

WASH_VOL   = 400    # µL per well per wash
ELU_VOL    = 120    # µL per well


def run(protocol: protocol_api.ProtocolContext):

    start = START_COL   # 0-indexed column slice start
    stop  = STOP_COL    # 0-indexed column slice stop (exclusive)

    # ── Labware ───────────────────────────────────────────────────────────
    tips_200      = protocol.load_labware(TIPS_200,      9)
    filter_plate  = protocol.load_labware(NORGEN_FILTER, 2)
    wash_res      = protocol.load_labware(RESERVOIR_1,   1)   # wash buffer
    elu_res       = protocol.load_labware(RESERVOIR_12,  4)   # elution in well A9

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips_200])

    # Continue tips from column 6 (columns 1–5 consumed in Step 3).
    # tips_200.columns() has 12 elements (indices 0-11); index 5 = column 6 (well A6).
    p300.starting_tip = tips_200.columns()[5][0]

    wash_src = wash_res.wells()[0]
    elu_src  = elu_res.wells_by_name()['A9']     # col 9 of 12-col reservoir

    target_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 3× WASH  (400 µL per column = 2 × 200 µL with P300 multi)
    # ════════════════════════════════════════════════════════════════════
    for wash_num in range(3):
        protocol.pause(
            f"WASH {wash_num + 1}/3  ▶  Place filter plate at SLOT 2 "
            f"(after centrifugation). "
            f"Add 24 mL Norgen wash buffer to reservoir at SLOT 1. "
            "Resume when ready."
        )

        p300.pick_up_tip()
        for col in target_cols:
            for _ in range(2):                   # 2 × 200 µL = 400 µL
                p300.aspirate(200, wash_src.bottom(2))
                p300.dispense(200, col[0].bottom(22))
        p300.drop_tip()

        if wash_num < 2:
            protocol.comment(
                f"Centrifuge filter plate 3 min at 2,500–4,000 g, RT. "
                "Discard flow-through."
            )
        else:
            protocol.comment(
                "Centrifuge filter plate 8 min at 2,500–4,000 g, RT. "
                "Discard flow-through (dry spin)."
            )

    # ════════════════════════════════════════════════════════════════════
    # ELUTION  (120 µL per column = 1 × 120 µL with P300 multi)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "ELUTION  ▶  Replace collection plate under filter plate with "
        "a labeled 96-well deep-well elution plate. "
        "Add 10 mL elution buffer to col 9 of the 12-col reservoir at SLOT 4. "
        "Place filter + elution plate at SLOT 2. Resume."
    )

    p300.pick_up_tip()
    for col in target_cols:
        p300.aspirate(ELU_VOL, elu_src.bottom(2))
        p300.dispense(ELU_VOL, col[0].bottom(22))
    p300.drop_tip()

    protocol.comment(
        "Step 5 complete. "
        "Centrifuge filter + elution plate 5 min at 2,500–4,000 g, RT. "
        "Confirm ~100 µL eluate per well. "
        "If processing batch 1 of 96: seal elution plate, refrigerate. "
        "Enter 0 at Zymo prompt in bash script and process batch 2 next."
    )
