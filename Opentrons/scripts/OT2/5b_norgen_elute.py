"""
OT-2  Step 5b – Norgen elution into 2 mL deep-well plate
Estimated Time  : ~10 min robot  (+2 min centrifuge)
Tips  : p300 × 1 tip

Deck layout
-----------
Slot 2 : custom_norgen_96filterplate_on_2ml_deep – Norgen filter plate on 2 mL deep-well elution plate
Slot 4 : nest_1_reservoir_195ml        – Norgen elution buffer
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
    TIP_START=int(os.environ.get('TIP_START','3'))    # after Step 5 wash uses A1-C1
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
    NORGEN_FILTER_ON_2ML='custom_norgen_96filterplate_on_2ml_deep'
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','3'))   # after Step 5 wash uses A1-C1
WELL_START=int(os.environ.get('WELL_START','0'))  # unused by this column-wise script

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5b – Norgen Elution',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

ELU_VOL  = 100   # µL per well


def run(protocol: protocol_api.ProtocolContext):

    n_cols = max(1, math.ceil(N_SAMPLES / 8))
    start  = FILTER_COL_START
    stop   = start + n_cols

    # ── Labware ───────────────────────────────────────────────────────────
    tips_300      = protocol.load_labware(TIPS_300,        9)
    filter_plate  = protocol.load_labware(NORGEN_FILTER_ON_2ML, 2)
    elu_res       = protocol.load_labware(RESERVOIR_1,     4)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    elu_src  = elu_res.wells()[0]

    target_cols = filter_plate.columns()[start:stop]

    protocol.pause(
        "STEP 5b  ▶  Remove the kit collection plate and place the Norgen filter plate "
        "on a clean NEST 96-well 2 mL deep-well elution plate at SLOT 2. "
        "Add 10 mL Norgen elution buffer to the single-channel reservoir at SLOT 4. Resume."
    )

    p300.pick_up_tip()
    for col in target_cols:
        for well in col:
            p300.aspirate(ELU_VOL, elu_src.bottom(2))
            p300.dispense(ELU_VOL, well.top(-5))
    p300.drop_tip()

    protocol.comment(
        "Step 5 complete. "
        "Centrifuge filter + elution plate 2 min at maximum speed or 2,000 RPM, RT. "
        "Confirm ~100 µL eluate per well. "
        "If processing batch 1 of 96: seal elution plate, refrigerate. "
        "Enter 0 at Zymo prompt in bash script and process batch 2 next."
    )
