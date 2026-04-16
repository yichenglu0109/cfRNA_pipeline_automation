"""
OT-2  Step 6 – Zymo RNA Clean & Concentrate
Time  : ~1 hr (with centrifugation)
Tips  : P300 ×17 rows; P1000 ×12–24 tips (transfer step)
        Uses 3-row tip remnant set aside from Step 5.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml   – RNA prep buffer (col 1) + wash buffer (col 2)
Slot 2 : custom_zymo_96filterplate          – Zymo filter plate (on collection plate)
Slot 3 : nest_96_wellplate_2ml_deep         – sample plate (eluted cfRNA + DNase product)
Slot 4 : nest_1_reservoir_195ml             – binding buffer (col 1) + EtOH (col 2)
Slot 8 : opentrons_96_filtertiprack_1000ul  (for transfer step; then 3-row remnant from step 5)
Slot 9 : opentrons_96_filtertiprack_200ul

env var : START_COL (0-indexed), STOP_COL (exclusive)

Pipettes
--------
Left  : p300_multi_gen2
Right : p1000_single_gen2
"""

import math, sys, os
sys.path.append('/data/user_storage/cfRNA')
from config import *

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 6 – Zymo Clean & Concentrate',
    'author': 'Adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': API_LEVEL,
}

# Volumes per column (µL)  – from Zymo R1080 kit instructions + paper
BIND_VOL  = 226
ETOH_VOL2 = 339
PREP_VOL  = 400
WASH1_VOL = 700
WASH2_VOL = 400


def _dispense_to_cols(pipette, src_well, cols, vol, max_tip=200):
    """Dispense vol µL to each of the target columns using P300 multi,
    splitting into ceil(vol/max_tip) aspirate-dispense pairs."""
    iters    = math.ceil(vol / max_tip)
    per_disp = round(vol / iters, 1)
    pipette.pick_up_tip()
    for col in cols:
        for _ in range(iters):
            pipette.aspirate(per_disp, src_well.bottom(2))
            pipette.dispense(per_disp, col[0].bottom(22))
    pipette.drop_tip()


def run(protocol: protocol_api.ProtocolContext):

    start = START_COL
    stop  = STOP_COL

    # ── Labware ───────────────────────────────────────────────────────────
    tips_200  = protocol.load_labware(TIPS_200,      9)
    tips_1000 = protocol.load_labware(TIPS_1000,     8)
    sample_plate = protocol.load_labware(WELLPLATE_2ML,  3)
    filter_plate = protocol.load_labware(ZYMO_FILTER,    2)
    bind_res     = protocol.load_labware(RESERVOIR_1,    4)   # binding buf + EtOH
    wash_res     = protocol.load_labware(RESERVOIR_1,    1)   # RNA prep + wash buffers

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300  = protocol.load_instrument('p300_multi_gen2',   'left',  tip_racks=[tips_200])
    p1000 = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips_1000])

    # Start P300 at tip remnant set aside in Step 5 (last 3 columns = cols 10-12)
    # tips_200.columns() has 12 elements (indices 0-11); index 9 = column 10
    p300.starting_tip = tips_200.columns()[9][0]

    bind_src  = bind_res.wells()[0]    # binding buffer
    etoh_src  = bind_res.wells()[1]    # 100% EtOH (second well of same reservoir)
    prep_src  = wash_res.wells()[0]    # RNA prep buffer
    wash_src  = wash_res.wells()[1]    # wash buffer (shared between 2 wash steps)

    target_sample_cols = sample_plate.columns()[start:stop]
    target_filter_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 1. Binding buffer (226 µL/col)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6A  ▶  Place sample plate (post-DNase) at SLOT 3. "
        "Add 27 mL binding buffer to position 1 of the reservoir at SLOT 4. "
        "Resume."
    )
    _dispense_to_cols(p300, bind_src, target_sample_cols, BIND_VOL)

    # ════════════════════════════════════════════════════════════════════
    # 2. EtOH (339 µL/col)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6B  ▶  Add 50 mL 100% EtOH to position 2 of reservoir at SLOT 4. "
        "Resume."
    )
    _dispense_to_cols(p300, etoh_src, target_sample_cols, ETOH_VOL2)

    # ════════════════════════════════════════════════════════════════════
    # 3. Mix + transfer to Zymo filter plate (P1000 single; 4 × 200 µL/well)
    # ════════════════════════════════════════════════════════════════════
    if stop > 6:
        protocol.pause(
            "STEP 6C  ▶  Replace P300 tip rack at SLOT 9 with a new rack. "
            "Place Zymo filter plate (on collection plate) at SLOT 2. "
            "Resume."
        )
        p300.reset_tipracks()
    else:
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
            # air gap to prevent drip back into filter
            p1000.aspirate(200, dst_well.bottom(25))
            p1000.drop_tip()

    protocol.comment(
        "Centrifuge filter plate 5 min at 3,000–5,000 g, RT. "
        "Discard flow-through; reassemble with collection plate."
    )

    # ════════════════════════════════════════════════════════════════════
    # 4. RNA prep buffer (400 µL/col)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6D  ▶  Place filter plate at SLOT 2. "
        "Add 48 mL RNA prep buffer to position 1 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p300, prep_src, target_filter_cols, PREP_VOL)
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through."
    )

    # ════════════════════════════════════════════════════════════════════
    # 5. Wash buffer – round 1 (700 µL/col = 4 × 175 µL)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6E  ▶  Place filter plate at SLOT 2. "
        "Add 84 mL wash buffer to position 2 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p300, wash_src, target_filter_cols, WASH1_VOL, max_tip=175)
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through. "
        "Replace collection plate with a new one."
    )

    # ════════════════════════════════════════════════════════════════════
    # 6. Wash buffer – round 2 (400 µL/col)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6F  ▶  Place filter plate at SLOT 2. "
        "Add 48 mL wash buffer to position 2 of reservoir at SLOT 1. "
        "Resume."
    )
    _dispense_to_cols(p300, wash_src, target_filter_cols, WASH2_VOL)
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
