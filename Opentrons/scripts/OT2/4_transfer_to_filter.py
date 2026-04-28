"""
OT-2  Step 4 – Transfer sample from 48-well plate → Norgen 96-well filter plate
Estimated Time  : ~1 hr  (P300 single-channel, 48-well)
Tips  : P300 ×48 tips (1 per well; half a tip rack)

Deck layout
-----------
Slot 2 : custom_48_wellplate_7000ul        – 48-well sample plate
Slot 5 : custom_norgen_96filterplate       – Norgen filter plate on kit collection plate
Slot 6 : nest_96_wellplate_2ml_deep        – tip trash / spare container
Slot 8 : opentrons_96_tiprack_300ul

env var : FILTER_COL_START  (0-indexed start column on filter plate; 0 for batch 1, 6 for batch 2)

Pipettes
--------
Left : p300_single_gen2
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
    N_SAMPLES=int(os.environ.get('N_SAMPLES','2'))
    TIP_START=int(os.environ.get('TIP_START','0'))    # 0=A1, 1=B1, ..., 8=A2
    WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2
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
TIP_START=int(os.environ.get('TIP_START','0'))    # fresh p300 rack in slot 8
WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 4 – Transfer to Norgen Filter Plate',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}


def run(protocol: protocol_api.ProtocolContext):

    filter_col_start = FILTER_COL_START  # 0-indexed column; 0 for batch 1, 6 for batch 2

    # ── Labware ───────────────────────────────────────────────────────────
    tips_300      = protocol.load_labware(TIPS_300,       8)
    plate_48      = protocol.load_labware(PLATE_48,       2)
    filter_plate  = protocol.load_labware(NORGEN_FILTER,  5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    wells_per_col = len(plate_48.columns()[0])
    src_wells = plate_48.wells()[WELL_START:WELL_START + N_SAMPLES]
    filter_wells_per_col = len(filter_plate.columns()[0])
    dst_wells = filter_plate.wells()[filter_col_start * filter_wells_per_col:
                                     filter_col_start * filter_wells_per_col + N_SAMPLES]

    protocol.pause(
        f"STEP 4  ▶  Place vortexed 48-well plate at SLOT 2. "
        f"Place Norgen filter plate (on collection plate) at SLOT 5, "
        f"corner A1 top-left. "
        f"Filter plate will be filled starting at column {filter_col_start + 1}. "
        "Resume when ready."
    )

    # Transfer well-by-well; pause at each new source column so user can vortex + unseal
    current_col = None
    for i, (src_well, dst_well) in enumerate(zip(src_wells, dst_wells)):
        src_col_idx = (WELL_START + i) // wells_per_col
        if src_col_idx != current_col:
            current_col = src_col_idx
            protocol.pause(
                f"  ▶  Vortex plate briefly (focus on column {src_col_idx + 1}). "
                f"Remove seal from column {src_col_idx + 1} only. Resume."
            )
        p300.pick_up_tip()
        p300.mix(2, 250, src_well.bottom(2))
        for _ in range(3):   # 3 × 200 µL + 10 µL air gap = 600 µL sample per well
            p300.aspirate(200, src_well.bottom(1.7), rate=0.75)
            protocol.delay(seconds=0.5)
            p300.air_gap(10)
            p300.dispense(210, dst_well.top(-5), rate=0.5)
            p300.blow_out(dst_well.top(-5))
        p300.drop_tip()

    protocol.comment(
        "Step 4 complete. "
        "Centrifuge filter + collection plate (unsealed rows only) "
        "2 min at maximum speed or 2,000 RPM, RT. Proceed to Step 5."
    )
