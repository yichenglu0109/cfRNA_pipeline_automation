"""
OT-2  Step 4 – Transfer sample from 48-well plate → Norgen 96-well filter plate
Estimated Time  : ~1 hr  (P300 single-channel, 48-well)
Tips  : P300 ×48 tips (1 per well; half a tip rack)

Deck layout
-----------
Slot 2 : custom_48_wellplate_7000ul        – 48-well sample plate
Slot 5 : custom_norgen_96filterplate_on_2ml_deep – Norgen filter plate on 2 mL deep-well collection plate
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
    N_SAMPLES=int(os.environ.get('N_SAMPLES','4'))
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
    NORGEN_FILTER_ON_2ML='custom_norgen_96filterplate_on_2ml_deep'
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','4'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','6')) # 0-indexed start column on filter plate; 0 for batch 1, 6 for batch 2
# TIP_START=int(os.environ.get('TIP_START','13'))   # after Steps 1 and 3 use 13 p300 tips
TIP_START=int(os.environ.get('TIP_START','8'))    # start at 8 
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
    filter_plate  = protocol.load_labware(NORGEN_FILTER_ON_2ML,  5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    # wells_per_col = len(plate_48.columns()[0])
    # src_wells = plate_48.wells()[WELL_START:WELL_START + N_SAMPLES]
    # filter_wells_per_col = len(filter_plate.columns()[0])
    # dst_wells = filter_plate.wells()[filter_col_start * filter_wells_per_col:
    #                                  filter_col_start * filter_wells_per_col + N_SAMPLES]

    # If only doing 4 samples in batch 1, just do first 4 wells in FILTER_COL_START column instead of calculating whole column offsets.
    src_wells = plate_48.wells()[WELL_START:WELL_START + N_SAMPLES]
    dst_wells = filter_plate.columns()[filter_col_start][0:N_SAMPLES] 

    protocol.pause(
        f"STEP 4  ▶  Place freshly vortexed 48-well plate at SLOT 2. "
        f"Place Norgen filter plate on a 2 mL deep-well collection plate at SLOT 5, "
        f"corner A1 top-left. "
        f"Filter plate will be filled starting at column {filter_col_start + 1}. "
        "Resume when ready."
    )

    # Transfer well-by-well; pause at each new source column so user can vortex + unseal.
    # current_col = None
    # for i, (src_well, dst_well) in enumerate(zip(src_wells, dst_wells)):
    #     src_col_idx = (WELL_START + i) // wells_per_col
    #     if src_col_idx != current_col:
    #         current_col = src_col_idx
    #         protocol.pause(
    #             f"  ▶  Fully reseal the plate and vortex 30 sec, focusing on column "
    #             f"{src_col_idx + 1}. Briefly spin or tap down liquid from the seal/walls. "
    #             f"Remove seal from column {src_col_idx + 1} only, visually confirm no "
    #             "visible slurry pellet remains, then resume immediately."
    #         )
    #     p300.pick_up_tip()
    #     p300.mix(6, 250, src_well.bottom(2))
    #     p300.mix(4, 250, src_well.bottom(12))
    #     for _ in range(3):   # 3 × 230 µL + 10 µL air gap = 690 µL slurry/sample per well
    #         p300.mix(2, 200, src_well.bottom(2))
    #         p300.aspirate(230, src_well.bottom(1.7), rate=0.5)
    #         protocol.delay(seconds=0.5)
    #         p300.air_gap(10)
    #         p300.dispense(240, dst_well.top(-5))
    #         p300.blow_out(dst_well.top(-5))
    #     p300.drop_tip()

    # For batch 1 with only 4 samples, just do 4 wells in FILTER_COL_START column instead of whole column; pause once to vortex + unseal.
    
    protocol.pause(
        f"  ▶  Fully reseal the plate and vortex 30 sec, focusing on column "
        f"{WELL_START // 8 + 1}. Briefly spin or tap down liquid from the seal/walls. "
        f"Remove seal from column {WELL_START // 8 + 1} only, visually confirm no "
        "visible slurry pellet remains, then resume immediately."
    )
    for src_well, dst_well in zip(src_wells, dst_wells):
        p300.pick_up_tip()
        p300.mix(6, 250, src_well.bottom(2))
        p300.mix(4, 250, src_well.bottom(12))
        for _ in range(3):   # 3 × 230 µL + 10 µL air gap = 690 µL slurry/sample per well
            p300.mix(2, 200, src_well.bottom(2))
            p300.aspirate(230, src_well.bottom(1.7), rate=0.5)
            protocol.delay(seconds=0.5)
            p300.air_gap(10)
            p300.dispense(240, dst_well.top(-5))
            p300.blow_out(dst_well.top(-5))
        p300.drop_tip()

    protocol.comment(
        "Step 4 complete. "
        "Centrifuge filter + 2 mL deep-well collection plate (unsealed rows only) "
        "2 min at maximum speed or 2,000 RPM, RT. Proceed to Step 5."
    )
