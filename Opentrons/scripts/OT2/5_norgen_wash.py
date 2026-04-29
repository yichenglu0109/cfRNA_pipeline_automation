"""
OT-2  Step 5 – Norgen filter: 3× wash → dry spin
Estimated Time  : ~45 min robot  (+9 min centrifuge)
Tips  : p300 × 3 tips (1 per wash × 3)

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml        – Norgen wash buffer (24 mL/wash)
Slot 2 : custom_norgen_96filterplate   – filter plate on kit collection plate
Slot 9 : opentrons_96_tiprack_300ul

env var : START_COL  (0-indexed; 0 for batch 1, 6 for batch 2)
          STOP_COL   (exclusive; 6 for batch 1, 12 for batch 2)

Pipettes
--------
Left : p300_single_gen2
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
    N_SAMPLES=int(os.environ.get('N_SAMPLES','2'))
    TIP_START=int(os.environ.get('TIP_START','0'))    # 0=A1, 1=B1, ..., 8=A2
    WELL_START=int(os.environ.get('WELL_START','0'))  # well index on filter plate
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_300='opentrons_96_tiprack_300ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    WELLPLATE_2ML='nest_96_wellplate_2ml_deep'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'       # simulation substitute
    NORGEN_FILTER='custom_norgen_96filterplate'  # simulation substitute
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','30'))   # fresh p300 rack in slot 9
WELL_START=int(os.environ.get('WELL_START','0'))  # unused by this column-wise script

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5 – Norgen Wash',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

WASH_VOL = 400   # µL per well per wash
def run(protocol: protocol_api.ProtocolContext):

    n_cols = max(1, math.ceil(N_SAMPLES / 8))
    start  = FILTER_COL_START
    stop   = start + n_cols

    # ── Labware ───────────────────────────────────────────────────────────
    tips_300      = protocol.load_labware(TIPS_300,        9)
    filter_plate  = protocol.load_labware(NORGEN_FILTER,   2)
    wash_res      = protocol.load_labware(RESERVOIR_1,     1)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    wash_src = wash_res.wells()[0]
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

        wash_iters = math.ceil(WASH_VOL / 250)
        wash_per   = round(WASH_VOL / wash_iters, 1)
        p300.pick_up_tip()
        for col in target_cols:
            for well in col:
                for _ in range(wash_iters):
                    p300.aspirate(wash_per, wash_src.bottom(2))
                    p300.dispense(wash_per, well.top(-5))
        p300.drop_tip()

        if wash_num < 2:
            protocol.comment(
                f"Centrifuge filter plate 2 min at maximum speed or 2,000 RPM, RT. "
                "Discard flow-through."
            )
        else:
            protocol.comment(
                "Centrifuge filter plate 5 min at 2,000 RPM, RT. "
                "Discard flow-through (dry spin)."
            )

    protocol.comment(
        "Step 5 complete. "
        "After dry spin, discard flow-through. "
        "Proceed to Step 5b: replace the collection plate with a clean 2 mL deep-well elution plate."
    )
