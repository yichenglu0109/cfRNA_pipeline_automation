"""
OT-2  Step 5c – DNase digestion on Norgen elution plate
Estimated Time  : ~40 min robot  (+20 min incubation at 37 °C)
Tips  : p20 × 1 tip

Deck layout
-----------
Slot 2 : thermoscientificnunc_96_wellplate_2000ul – elution plate from Step 5
Slot 4 : nest_1_reservoir_195ml       – DNase master mix
                                         (11 µL 10× buffer + 2 µL DNase per well; 10% excess)
Slot 6 : opentrons_96_tiprack_20ul

Pipettes
--------
Right : p20_single_gen2
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
    N_SAMPLES=int(os.environ.get('N_SAMPLES','4'))
    TIP_START=int(os.environ.get('TIP_START','0'))
    WELL_START=int(os.environ.get('WELL_START','6'))
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_300='opentrons_96_tiprack_300ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    WELLPLATE_2ML='thermoscientificnunc_96_wellplate_2000ul'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'
    NORGEN_FILTER='custom_norgen_96filterplate'
    ZYMO_FILTER='custom_zymo_96filterplate'

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','1'))    # fresh p20 rack in slot 6
WELL_START=int(os.environ.get('WELL_START','0'))  # unused by this column-wise script

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5c – DNase Digestion',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

DNASE_VOL = 13   # µL per well (11 µL 10× buffer + 2 µL DNase)


def run(protocol: protocol_api.ProtocolContext):

    n_cols = max(1, math.ceil(N_SAMPLES / 8))
    start  = FILTER_COL_START
    stop   = start + n_cols
    n_wells = n_cols * 8
    master_mix_ul = round(n_wells * DNASE_VOL * 1.1)   # 10% excess

    # ── Labware ───────────────────────────────────────────────────────────
    tips_20       = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    elution_plate = protocol.load_labware(WELLPLATE_2ML, 2)
    dnase_res     = protocol.load_labware(RESERVOIR_1,   4)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tips_20])
    p20.starting_tip = tips_20.wells()[TIP_START]

    dnase_src   = dnase_res.wells()[0]
    target_cols = elution_plate.columns()[start:stop]

    protocol.pause(
        f"STEP 5c  ▶  Place the 2 mL deep-well elution plate (from Step 5b) at SLOT 2. "
        f"Prepare DNase master mix: 11 µL 10× DNase buffer + 2 µL DNase per well "
        f"({master_mix_ul} µL total for {n_wells} wells, 10% excess). "
        f"Add master mix to the single-channel reservoir at SLOT 4. Resume."
    )

    p20.pick_up_tip()
    for col in target_cols:
        for well in col:
            p20.aspirate(DNASE_VOL, dnase_src.bottom(1))
            p20.dispense(DNASE_VOL, well.bottom(5))
            p20.blow_out(well.top(-5))
    p20.drop_tip()

    protocol.comment(
        "Step 5c complete. "
        "Vortex plate lightly. "
        "Incubate at 37 °C for 20 min. "
        "Proceed to Step 6 (Zymo Clean & Concentrate)."
    )
