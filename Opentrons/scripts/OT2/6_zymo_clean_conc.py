"""
OT-2  Step 6 – Zymo RNA Clean & Concentrate
Time  : ~1 hr (with centrifugation)
Tips  : p1000 ×7 tips (dispensing) + p1000 ×48 tips (transfer)
        Requires 1–2 full p1000 tip racks.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml   – RNA prep buffer (pos 1) + wash buffer (pos 2)
Slot 2 : custom_zymo_96filterplate          – Zymo filter plate (on collection plate)
Slot 3 : nest_96_wellplate_2ml_deep         – sample plate (eluted cfRNA + DNase product)
Slot 4 : nest_1_reservoir_195ml             – binding buffer (pos 1) + EtOH (pos 2)
Slot 8 : opentrons_96_filtertiprack_1000ul
Slot 9 : opentrons_96_filtertiprack_1000ul

env var : START_COL (0-indexed), STOP_COL (exclusive)

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
    'protocolName': 'cfRNA Step 6 – Zymo Clean & Concentrate',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

BIND_VOL  = 226
ETOH_VOL2 = 339
PREP_VOL  = 400
WASH1_VOL = 700
WASH2_VOL = 400


def _dispense_to_cols(pipette, src_well, cols, vol, max_tip=900):
    """Dispense vol µL to each well in target columns using p1000 single,
    splitting into ceil(vol/max_tip) aspirate-dispense pairs per well."""
    iters    = math.ceil(vol / max_tip)
    per_disp = round(vol / iters, 1)
    pipette.pick_up_tip()
    for col in cols:
        for well in col:
            for _ in range(iters):
                pipette.aspirate(per_disp, src_well.bottom(2))
                pipette.dispense(per_disp, well.bottom(22))
    pipette.drop_tip()


def run(protocol: protocol_api.ProtocolContext):

    start = START_COL
    stop  = STOP_COL

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a       = protocol.load_labware(TIPS_1000,     9)
    tips_b       = protocol.load_labware(TIPS_1000,     8)
    sample_plate = protocol.load_labware(WELLPLATE_2ML, 3)
    filter_plate = protocol.load_labware(ZYMO_FILTER,   2)
    bind_res     = protocol.load_labware(RESERVOIR_1,   4)
    wash_res     = protocol.load_labware(RESERVOIR_1,   1)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_a, tips_b])

    bind_src  = bind_res.wells()[0]
    etoh_src  = bind_res.wells()[1]
    prep_src  = wash_res.wells()[0]
    wash_src  = wash_res.wells()[1]

    target_sample_cols = sample_plate.columns()[start:stop]
    target_filter_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 1. Binding buffer (226 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6A  ▶  Place sample plate (post-DNase) at SLOT 3. "
        "Add 27 mL binding buffer to position 1 of the reservoir at SLOT 4. "
        "Load 2 full p1000 tip racks at SLOTS 8 and 9. Resume."
    )
    _dispense_to_cols(p1000, bind_src, target_sample_cols, BIND_VOL)

    # ════════════════════════════════════════════════════════════════════
    # 2. EtOH (339 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6B  ▶  Add 50 mL 100% EtOH to position 2 of reservoir at SLOT 4. "
        "Resume."
    )
    _dispense_to_cols(p1000, etoh_src, target_sample_cols, ETOH_VOL2)

    # ════════════════════════════════════════════════════════════════════
    # 3. Mix + transfer to Zymo filter plate (p1000; 1 × 900 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6C  ▶  Place Zymo filter plate (on collection plate) at SLOT 2. "
        "Resume."
    )

    for src_col, dst_col in zip(target_sample_cols, target_filter_cols):
        for src_well, dst_well in zip(src_col, dst_col):
            p1000.pick_up_tip()
            p1000.mix(3, 500, src_well.bottom(2))
            p1000.aspirate(900, src_well.bottom(2))
            protocol.delay(seconds=0.5)
            p1000.air_gap(100)
            p1000.dispense(1000, dst_well.bottom(10))
            p1000.aspirate(200, dst_well.bottom(25))
            p1000.drop_tip()

    protocol.comment(
        "Centrifuge filter plate 5 min at 3,000–5,000 g, RT. "
        "Discard flow-through; reassemble with collection plate."
    )

    # ════════════════════════════════════════════════════════════════════
    # 4. RNA prep buffer (400 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6D  ▶  Place filter plate at SLOT 2. "
        "Add 48 mL RNA prep buffer to position 1 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p1000, prep_src, target_filter_cols, PREP_VOL)
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through."
    )

    # ════════════════════════════════════════════════════════════════════
    # 5. Wash buffer – round 1 (700 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6E  ▶  Place filter plate at SLOT 2. "
        "Add 84 mL wash buffer to position 2 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p1000, wash_src, target_filter_cols, WASH1_VOL)
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through. "
        "Replace collection plate with a new one."
    )

    # ════════════════════════════════════════════════════════════════════
    # 6. Wash buffer – round 2 (400 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6F  ▶  Place filter plate at SLOT 2. "
        "Add 48 mL wash buffer to position 2 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p1000, wash_src, target_filter_cols, WASH2_VOL)
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through AND collection plate. "
        "Place filter plate on a NEW 96-well PCR plate (elution plate)."
    )

    protocol.comment(
        "Step 6 complete (robot). "
        "MANUAL FINAL STEP: add 12.5 µL nuclease-free H2O per well by hand "
        "(P20 multichannel), centrifuge 5 min at 3,000–5,000 g. "
        "Confirm ~12 µL eluate per well. Aliquot and freeze at -80 °C."
    )
