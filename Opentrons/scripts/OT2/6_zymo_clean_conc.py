"""
OT-2  Step 6 – Zymo RNA Clean & Concentrate
Time  : ~1 hr (with centrifugation)
Tips  : p300 ×7 tips (dispensing) + p300 ×48 tips (transfer)
        Requires 1–2 full p300 tip racks.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml             – replace between RNA prep buffer, wash buffer and nuclease-free H2O
Slot 2 : custom_zymo_96filterplate          – Zymo filter plate (on collection plate → elution plate)
Slot 3 : thermoscientificnunc_96_wellplate_2000ul – sample plate (eluted cfRNA + DNase product)
Slot 4 : nest_1_reservoir_195ml             – replace between binding buffer and EtOH
Slot 6 : opentrons_96_tiprack_20ul
Slot 8 : opentrons_96_tiprack_300ul
Slot 9 : opentrons_96_tiprack_300ul

env var : START_COL (0-indexed), STOP_COL (exclusive)

Pipettes
--------
Left  : p300_single_gen2
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
    TIP_START=int(os.environ.get('TIP_START','17'))    # 0=A1, 1=B1, ..., 8=A2
    WELL_START=int(os.environ.get('WELL_START','6'))  # well index on sample/filter plate
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_300='opentrons_96_tiprack_300ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    WELLPLATE_2ML='thermoscientificnunc_96_wellplate_2000ul'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'       # simulation substitute
    NORGEN_FILTER='custom_norgen_96filterplate'  # simulation substitute
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','34'))       # p300 rack continues after Step 5
P20_TIP_START=int(os.environ.get('P20_TIP_START','1')) # p20 rack continues after Step 5b uses A1
WELL_START=int(os.environ.get('WELL_START','0'))       # unused by this column-wise script

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 6 – Zymo Clean & Concentrate',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

BIND_VOL  = 226
ETOH_VOL2 = 339
PREP_VOL  = 400
WASH1_VOL = 700
WASH2_VOL = 400
ZYMO_LOAD_VOL = 226
ZYMO_LOAD_REPS = 3
REAGENT_EXCESS = 1.2


def reagent_ml(n_wells, per_well_ul):
    return round(n_wells * per_well_ul * REAGENT_EXCESS / 1000, 1)


def run(protocol: protocol_api.ProtocolContext):

    n_cols = max(1, math.ceil(N_SAMPLES / 8))
    start  = FILTER_COL_START
    stop   = start + n_cols
    n_wells = n_cols * 8

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a       = protocol.load_labware(TIPS_300,       9)
    tips_b       = protocol.load_labware(TIPS_300,       8)
    tips_20      = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    sample_plate = protocol.load_labware(WELLPLATE_2ML,  3)
    filter_plate = protocol.load_labware(ZYMO_FILTER,    2)
    bind_res     = protocol.load_labware(RESERVOIR_1,    4)
    wash_res     = protocol.load_labware(RESERVOIR_1,    1)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left',  tip_racks=[tips_a, tips_b])
    p20  = protocol.load_instrument('p20_single_gen2',  'right', tip_racks=[tips_20])
    p300.starting_tip = tips_a.wells()[TIP_START]
    p20.starting_tip = tips_20.wells()[P20_TIP_START]

    bind_src  = bind_res.wells()[0]
    etoh_src  = bind_res.wells()[0]
    prep_src  = wash_res.wells()[0]
    wash_src  = wash_res.wells()[0]
    elu_src   = wash_res.wells()[0]

    target_sample_cols = sample_plate.columns()[start:stop]
    target_filter_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 1. Binding buffer (226 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6A  ▶  Place sample plate (post-DNase) at SLOT 3. "
        f"Place a 195 mL single-channel reservoir containing {reagent_ml(n_wells, BIND_VOL)} mL "
        "binding buffer at SLOT 4. "
        "Load 2 full p300 tip racks at SLOTS 8 and 9. Resume."
    )
    iters    = math.ceil(BIND_VOL / 250)
    per_disp = round(BIND_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_sample_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, bind_src.bottom(2))
                p300.dispense(per_disp, well.bottom(5))
                p300.blow_out(well.top(-2))
    p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # 2. EtOH (339 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        f"STEP 6B  ▶  Replace the SLOT 4 reservoir with a 195 mL single-channel reservoir "
        f"containing {reagent_ml(n_wells, ETOH_VOL2)} mL 100% EtOH. "
        "Resume."
    )
    iters    = math.ceil(ETOH_VOL2 / 250)
    per_disp = round(ETOH_VOL2 / iters, 1)
    p300.pick_up_tip()
    for col in target_sample_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, etoh_src.bottom(2))
                p300.dispense(per_disp, well.bottom(25))
                p300.blow_out(well.top(-2))
    p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # 3. Vortex + transfer to Zymo filter plate (p300; 3 × 226 µL/well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6C  ▶  Remove sample plate from SLOT 3. Vortex ≥30 s. "
        "Return sample plate to SLOT 3. "
        "Place Zymo filter plate (on collection plate) at SLOT 2. Resume."
    )

    for src_col, dst_col in zip(target_sample_cols, target_filter_cols):
        for src_well, dst_well in zip(src_col, dst_col):
            p300.pick_up_tip()
            for _ in range(ZYMO_LOAD_REPS):   # 3 × 226 µL = 678 µL
                p300.aspirate(ZYMO_LOAD_VOL, src_well.bottom(0.5))
                protocol.delay(seconds=0.5)
                p300.air_gap(20)
                p300.dispense(ZYMO_LOAD_VOL + 20, dst_well.top(-5))
                p300.blow_out(dst_well.top(-5))
            p300.drop_tip()

    protocol.comment(
        "Centrifuge filter plate 5 min at 3,000–5,000 g, RT. "
        "Discard flow-through; reassemble with collection plate."
    )

    # ════════════════════════════════════════════════════════════════════
    # 4. RNA prep buffer (400 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6D  ▶  Place filter plate at SLOT 2. "
        f"Place a 195 mL single-channel reservoir containing {reagent_ml(n_wells, PREP_VOL)} mL "
        "RNA prep buffer at SLOT 1. "
        "Resume."
    )
    iters    = math.ceil(PREP_VOL / 250)
    per_disp = round(PREP_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, prep_src.bottom(2))
                p300.dispense(per_disp, well.bottom(22))
                p300.blow_out(well.top(-2))
    p300.drop_tip()
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through."
    )

    # ════════════════════════════════════════════════════════════════════
    # 5. Wash buffer – round 1 (700 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6E  ▶  Place filter plate at SLOT 2. "
        f"Replace the SLOT 1 reservoir with a 195 mL single-channel reservoir containing "
        f"{reagent_ml(n_wells, WASH1_VOL)} mL wash buffer. "
        "Resume."
    )
    iters    = math.ceil(WASH1_VOL / 250)
    per_disp = round(WASH1_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, wash_src.bottom(2))
                p300.dispense(per_disp, well.bottom(22))
                p300.blow_out(well.top(-2))
    p300.drop_tip()
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through. "
        "Replace collection plate with a new one."
    )

    # ════════════════════════════════════════════════════════════════════
    # 6. Wash buffer – round 2 (400 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6F  ▶  Place filter plate at SLOT 2. "
        f"Replace the SLOT 1 reservoir with a 195 mL single-channel reservoir containing "
        f"{reagent_ml(n_wells, WASH2_VOL)} mL wash buffer. "
        "Resume."
    )
    iters    = math.ceil(WASH2_VOL / 250)
    per_disp = round(WASH2_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, wash_src.bottom(2))
                p300.dispense(per_disp, well.bottom(22))
                p300.blow_out(well.top(-2))
    p300.drop_tip()
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through AND collection plate. "
        "Place filter plate on a NEW 96-well PCR plate (elution plate)."
    )

    # ════════════════════════════════════════════════════════════════════
    # 7. Elution  (12.5 µL nuclease-free H2O per well; p20)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6G  ▶  Discard collection plate. Place filter plate on a NEW "
        "96-well PCR plate (elution plate) at SLOT 2. "
        "Replace the SLOT 1 reservoir with a 195 mL single-channel reservoir containing "
        "1 mL nuclease-free H2O. "
        "Resume."
    )

    p20.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            p20.aspirate(12.5, elu_src.bottom(1))
            p20.dispense(12.5, well.bottom(5))
            p20.blow_out(well.top(-2))
    p20.drop_tip()

    protocol.comment(
        "Step 6 complete. "
        "Centrifuge filter + elution plate 5 min at 3,000–5,000 g. "
        "Confirm ~12 µL eluate per well. Aliquot and freeze at -80 °C."
    )
