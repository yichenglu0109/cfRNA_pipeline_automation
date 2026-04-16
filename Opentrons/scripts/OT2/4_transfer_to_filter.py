"""
OT-2  Step 4 – Transfer sample from 48-well plate → Norgen 96-well filter plate
Time  : ~8 min  (P1000 single-channel, per-well)
Tips  : P1000 ×48 tips (1 per well; half a tip rack)

Deck layout
-----------
Slot 2 : custom_48_wellplate_7000ul        – 48-well sample plate
Slot 5 : custom_norgen_96filterplate       – Norgen filter plate (on 2 mL collection plate)
Slot 6 : nest_96_wellplate_2ml_deep        – tip trash / spare container
Slot 8 : opentrons_96_filtertiprack_1000ul

env var : FILTER_COL_START  (0-indexed start column on filter plate; 0 for batch 1, 6 for batch 2)

Pipettes
--------
Right : p1000_single_gen2
"""

import sys, os
sys.path.append('/data/user_storage/cfRNA')
from config import *

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 4 – Transfer to Norgen Filter Plate',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': API_LEVEL,
}


def run(protocol: protocol_api.ProtocolContext):

    filter_col_start = FILTER_COL_START  # 0-indexed column; 0 for batch 1, 6 for batch 2

    # ── Labware ───────────────────────────────────────────────────────────
    tips_1000     = protocol.load_labware(TIPS_1000,     8)
    plate_48      = protocol.load_labware(PLATE_48,      2)
    filter_plate  = protocol.load_labware(NORGEN_FILTER, 5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_1000])

    # Target columns on filter plate (6 columns × 8 wells = 48 wells per batch)
    # Batch 1: filter cols 0-5  (columns 1-6)
    # Batch 2: filter cols 6-11 (columns 7-12)
    filter_cols = filter_plate.columns()[filter_col_start: filter_col_start + 6]

    protocol.pause(
        f"STEP 4  ▶  Place vortexed 48-well plate at SLOT 2 (column 1 unsealed). "
        f"Place Norgen filter plate (on collection plate) at SLOT 5, "
        f"corner A1 top-left. "
        f"Filter plate will be filled starting at column {filter_col_start + 1}. "
        "Resume when ready."
    )

    # Transfer each column of the 48-well plate → corresponding filter column
    # Vortex + unseal one column at a time to prevent slurry settling
    for col_idx, (src_col, dst_col) in enumerate(zip(plate_48.columns(), filter_cols)):

        protocol.pause(
            f"  ▶  Vortex plate briefly (focus on column {col_idx + 1}). "
            f"Remove seal from column {col_idx + 1} only. Resume."
        )

        for src_well, dst_well in zip(src_col, dst_col):
            p1000.pick_up_tip()
            p1000.mix(2, 500, src_well.bottom(2))
            p1000.aspirate(950, src_well.bottom(2), rate=0.75)
            protocol.delay(seconds=0.5)
            p1000.aspirate(40,  src_well.bottom(2), rate=0.75)
            p1000.air_gap(10)
            p1000.dispense(1000, dst_well.bottom(20), rate=0.5)
            p1000.blow_out(dst_well.bottom(20))
            p1000.drop_tip()

    protocol.comment(
        "Step 4 complete. "
        "Centrifuge filter + collection plate (unsealed rows only) "
        "4 min at 2,500–4,000 g, RT. Proceed to Step 5."
    )
