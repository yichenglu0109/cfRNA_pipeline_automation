"""
OT-2  Step 6 – Zymo RNA Clean & Concentrate
Time  : ~1 hr (with centrifugation)
Tips  : p300 ×7 tips (dispensing) + p300 ×48 tips (transfer)
        Requires 1–2 full p300 tip racks.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml             – wash buffer round 1
Slot 2 : custom_zymo_96filterplate          – Zymo filter plate (on collection plate → elution plate)
Slot 3 : thermoscientificnunc_96_wellplate_2000ul – sample plate (eluted cfRNA + DNase product)
Slot 4 : dynamic reagent source             – binding buffer, EtOH, RNA prep buffer, wash 2, nuclease-free H2O
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
    TIP_START=int(os.environ.get('TIP_START','25'))    # after Step 5b uses 1 more p300 tip
    WELL_START=int(os.environ.get('WELL_START','6'))  # well index on sample/filter plate
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_300='opentrons_96_tiprack_300ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    TUBE_BLOCK_2ML='opentrons_24_aluminumblock_nest_2ml_snapcap'
    WELLPLATE_2ML='thermoscientificnunc_96_wellplate_2000ul'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'       # simulation substitute
    NORGEN_FILTER='custom_norgen_96filterplate'  # simulation substitute
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','25'))       # after Steps 1-5b use 25 p300 tips
P20_TIP_START=int(os.environ.get('P20_TIP_START','1')) # after Step 5c uses 1 p20 tip
WELL_START=int(os.environ.get('WELL_START','0'))       # unused by this column-wise script
TUBE_BLOCK_2ML = globals().get('TUBE_BLOCK_2ML', 'opentrons_24_aluminumblock_nest_2ml_snapcap')

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
SMALL_SOURCE_MAX_UL = 4000
SINGLE_TUBE_MAX_UL = 2000
FINAL_WATER_LOAD_UL = 1000


def reagent_ml(n_wells, per_well_ul):
    return round(n_wells * per_well_ul * REAGENT_EXCESS / 1000, 1)


def reagent_ul(n_wells, per_well_ul):
    return n_wells * per_well_ul * REAGENT_EXCESS


class ReagentSource:
    def __init__(self, wells, volumes_ul):
        self.wells = wells
        self.remaining = list(volumes_ul)
        self.index = 0

    def aspiration_location(self, volume_ul):
        while len(self.wells) > 1 and self.index < len(self.wells) - 1 and self.remaining[self.index] <= 0:
            self.index += 1
        if len(self.wells) > 1 and self.remaining[self.index] < volume_ul and self.index < len(self.wells) - 1:
            self.index += 1
        self.remaining[self.index] -= volume_ul
        return self.wells[self.index].bottom(1.5)


def format_ul(ul):
    return f"{ul / 1000:.1f} mL ({ul:.0f} µL)" if ul >= 1000 else f"{ul:.0f} µL"


def source_layout(total_ul, force_reservoir=False):
    if not force_reservoir and total_ul < SMALL_SOURCE_MAX_UL:
        n_sources = 1 if total_ul <= SINGLE_TUBE_MAX_UL else 2
        return True, n_sources, total_ul / n_sources
    return False, 1, total_ul


def load_source(protocol, slot, total_ul, force_reservoir=False):
    use_tubes, _, _ = source_layout(total_ul, force_reservoir)
    return protocol.load_labware(TUBE_BLOCK_2ML if use_tubes else RESERVOIR_1, slot)


def make_source(labware, total_ul, force_reservoir=False):
    use_tubes, n_sources, per_source = source_layout(total_ul, force_reservoir)
    if use_tubes:
        wells = [labware.wells_by_name()[name] for name in ['A1', 'A2'][:n_sources]]
        return ReagentSource(wells, [per_source] * n_sources)
    return ReagentSource([labware.wells()[0]], [total_ul])


def source_prompt(slot, total_ul, label, force_reservoir=False):
    use_tubes, n_sources, per_source = source_layout(total_ul, force_reservoir)
    if use_tubes:
        details = ", ".join(f"{name}: {format_ul(per_source)}" for name in ['A1', 'A2'][:n_sources])
        return (
            f"Place a 24-well aluminum block with LoBind tube(s) at SLOT {slot}. "
            f"Add {label} to {details}."
        )
    return (
        f"Place a 195 mL single-channel reservoir at SLOT {slot}. "
        f"Add {format_ul(total_ul)} {label}."
    )


def run(protocol: protocol_api.ProtocolContext):

    n_cols = max(1, math.ceil(N_SAMPLES / 8))
    start  = FILTER_COL_START
    stop   = start + n_cols
    n_wells = n_cols * 8
    bind_total_ul = reagent_ul(n_wells, BIND_VOL)
    etoh_total_ul = reagent_ul(n_wells, ETOH_VOL2)
    prep_total_ul = reagent_ul(n_wells, PREP_VOL)
    wash1_total_ul = reagent_ul(n_wells, WASH1_VOL)
    wash2_total_ul = reagent_ul(n_wells, WASH2_VOL)
    slot4_max_ul = max(bind_total_ul, etoh_total_ul, prep_total_ul, wash2_total_ul, FINAL_WATER_LOAD_UL)
    slot4_force_reservoir = slot4_max_ul >= SMALL_SOURCE_MAX_UL

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a       = protocol.load_labware(TIPS_300,       9)
    tips_b       = protocol.load_labware(TIPS_300,       8)
    tips_20      = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    sample_plate = protocol.load_labware(WELLPLATE_2ML,  3)
    filter_plate = protocol.load_labware(ZYMO_FILTER,    2)
    bind_res     = load_source(protocol, 4, slot4_max_ul, slot4_force_reservoir)
    wash_res     = protocol.load_labware(RESERVOIR_1,    1)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left',  tip_racks=[tips_a, tips_b])
    p20  = protocol.load_instrument('p20_single_gen2',  'right', tip_racks=[tips_20])
    p300.starting_tip = tips_a.wells()[TIP_START]
    p20.starting_tip = tips_20.wells()[P20_TIP_START]

    wash_src  = wash_res.wells()[0]

    target_sample_cols = sample_plate.columns()[start:stop]
    target_filter_cols = filter_plate.columns()[start:stop]

    # ════════════════════════════════════════════════════════════════════
    # 1. Binding buffer (226 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6A  ▶  Place sample plate (post-DNase) at SLOT 3. "
        f"{source_prompt(4, bind_total_ul, 'binding buffer', slot4_force_reservoir)} "
        "Load 2 full p300 tip racks at SLOTS 8 and 9. Resume."
    )
    bind_src = make_source(bind_res, bind_total_ul, slot4_force_reservoir)
    iters    = math.ceil(BIND_VOL / 250)
    per_disp = round(BIND_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_sample_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, bind_src.aspiration_location(per_disp))
                p300.dispense(per_disp, well.bottom(15))
                p300.blow_out(well.top(-2))
    p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # 2. EtOH (339 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        f"STEP 6B  ▶  Empty the SLOT 4 reagent source. "
        f"{source_prompt(4, etoh_total_ul, '100% EtOH', slot4_force_reservoir)} "
        "Resume."
    )
    etoh_src = make_source(bind_res, etoh_total_ul, slot4_force_reservoir)
    iters    = math.ceil(ETOH_VOL2 / 250)
    per_disp = round(ETOH_VOL2 / iters, 1)
    p300.pick_up_tip()
    for col in target_sample_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, etoh_src.aspiration_location(per_disp))
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
                p300.aspirate(ZYMO_LOAD_VOL, src_well.bottom(0.3))
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
        f"Empty the SLOT 4 reagent source. "
        f"{source_prompt(4, prep_total_ul, 'RNA prep buffer', slot4_force_reservoir)} "
        "Resume."
    )
    prep_src = make_source(bind_res, prep_total_ul, slot4_force_reservoir)
    iters    = math.ceil(PREP_VOL / 250)
    per_disp = round(PREP_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, prep_src.aspiration_location(per_disp))
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
        f"{wash1_total_ul / 1000:.1f} mL wash buffer. "
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
        f"Empty the SLOT 4 reagent source. "
        f"{source_prompt(4, wash2_total_ul, 'wash buffer', slot4_force_reservoir)} "
        "Resume."
    )
    wash2_src = make_source(bind_res, wash2_total_ul, slot4_force_reservoir)
    iters    = math.ceil(WASH2_VOL / 250)
    per_disp = round(WASH2_VOL / iters, 1)
    p300.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            for _ in range(iters):
                p300.aspirate(per_disp, wash2_src.aspiration_location(per_disp))
                p300.dispense(per_disp, well.bottom(22))
                p300.blow_out(well.top(-2))
    p300.drop_tip()
    protocol.comment(
        "Centrifuge 5 min at 3,000–5,000 g. Discard flow-through AND collection plate. "
        "Place filter plate on a NEW 96-well PCR plate (elution plate)."
    )

    # ════════════════════════════════════════════════════════════════════
    # 7. Elution  (15 µL nuclease-free H2O per well; p20)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 6G  ▶  Discard collection plate. Place filter plate on a NEW "
        "96-well PCR plate (elution plate) at SLOT 2. "
        f"Empty the SLOT 4 reagent source. "
        f"{source_prompt(4, FINAL_WATER_LOAD_UL, 'nuclease-free H2O', slot4_force_reservoir)} "
        "Resume."
    )

    elu_src = make_source(bind_res, FINAL_WATER_LOAD_UL, slot4_force_reservoir)
    p20.pick_up_tip()
    for col in target_filter_cols:
        for well in col:
            p20.aspirate(15, elu_src.aspiration_location(15))
            p20.dispense(17, well.bottom(5))
            p20.blow_out(well.bottom(6))
    p20.drop_tip()

    protocol.comment(
        "Step 6 complete. "
        "Centrifuge filter + elution plate 5 min at 3,000–5,000 g. "
        "Confirm ~15 µL eluate per well. Aliquot and freeze at -80 °C."
    )
