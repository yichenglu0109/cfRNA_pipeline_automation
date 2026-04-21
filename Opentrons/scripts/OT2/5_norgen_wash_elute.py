"""
OT-2  Step 5 – Norgen filter: 3× wash → dry spin → elute
Time  : ~15 min robot  (+3+3+8+5+5 = 24 min centrifuge)
Tips  : p1000 × 4 tips (1 per wash × 3 + 1 elution)

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml        – Norgen wash buffer (24 mL/wash)
Slot 2 : custom_norgen_96filterplate   – filter plate (on collection plate)
Slot 4 : nest_12_reservoir_15ml        – elution buffer in well A9 (col 9)
Slot 9 : opentrons_96_filtertiprack_1000ul

env var : START_COL  (0-indexed; 0 for batch 1, 6 for batch 2)
          STOP_COL   (exclusive; 6 for batch 1, 12 for batch 2)

Pipettes
--------
Right : p1000_single_gen2
"""

import sys, os
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
    'protocolName': 'cfRNA Step 5 – Norgen Wash + Elute',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

WASH_VOL = 400   # µL per well per wash
ELU_VOL  = 120   # µL per well


def run(protocol: protocol_api.ProtocolContext):

    start = START_COL
    stop  = STOP_COL

    # ── Labware ───────────────────────────────────────────────────────────
    tips_1000     = protocol.load_labware(TIPS_1000,      9)
    filter_plate  = protocol.load_labware(NORGEN_FILTER,  2)
    wash_res      = protocol.load_labware(RESERVOIR_1,    1)
    elu_res       = protocol.load_labware(RESERVOIR_12,   4)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_1000])

    wash_src = wash_res.wells()[0]
    elu_src  = elu_res.wells_by_name()['A9']

    target_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 3× WASH  (400 µL per well; 1 tip per wash, reused across all wells)
    # ════════════════════════════════════════════════════════════════════
    for wash_num in range(3):
        protocol.pause(
            f"WASH {wash_num + 1}/3  ▶  Place filter plate at SLOT 2 "
            f"(after centrifugation). "
            f"Add 24 mL Norgen wash buffer to reservoir at SLOT 1. "
            "Resume when ready."
        )

        p1000.pick_up_tip()
        for col in target_cols:
            for well in col:
                p1000.aspirate(WASH_VOL, wash_src.bottom(2))
                p1000.dispense(WASH_VOL, well.bottom(22))
        p1000.drop_tip()

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
    # ELUTION  (120 µL per well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "ELUTION  ▶  Replace collection plate under filter plate with "
        "a labeled 96-well deep-well elution plate. "
        "Add 10 mL elution buffer to col 9 of the 12-col reservoir at SLOT 4. "
        "Place filter + elution plate at SLOT 2. Resume."
    )

    p1000.pick_up_tip()
    for col in target_cols:
        for well in col:
            p1000.aspirate(ELU_VOL, elu_src.bottom(2))
            p1000.dispense(ELU_VOL, well.bottom(22))
    p1000.drop_tip()

    protocol.comment(
        "Step 5 complete. "
        "Centrifuge filter + elution plate 5 min at 2,500–4,000 g, RT. "
        "Confirm ~100 µL eluate per well. "
        "If processing batch 1 of 96: seal elution plate, refrigerate. "
        "Enter 0 at Zymo prompt in bash script and process batch 2 next."
    )
