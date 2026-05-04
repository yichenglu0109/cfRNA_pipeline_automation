"""
OT-2  Step 5b – Norgen elution into 2 mL deep-well plate
Estimated Time  : ~10 min robot  (+2 min centrifuge)
Tips  : p300 × 1 tip

Deck layout
-----------
Slot 2 : custom_norgen_96filterplate_on_2ml_deep – Norgen filter plate on 2 mL deep-well elution plate
Slot 4 : dynamic reagent source         – Norgen elution buffer
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
    TIP_START=int(os.environ.get('TIP_START','24'))    # after Step 5 uses 3 more p300 tips
    WELL_START=int(os.environ.get('WELL_START','0'))  # well index on filter plate
    TIPS_200='opentrons_96_filtertiprack_200ul'
    TIPS_300='opentrons_96_tiprack_300ul'
    TIPS_1000='opentrons_96_filtertiprack_1000ul'
    RESERVOIR_1='nest_1_reservoir_195ml'
    RESERVOIR_12='nest_12_reservoir_15ml'
    TUBE_BLOCK_2ML='opentrons_24_aluminumblock_nest_2ml_snapcap'
    WELLPLATE_2ML='nest_96_wellplate_2ml_deep'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'       # simulation substitute
    NORGEN_FILTER='custom_norgen_96filterplate'  # simulation substitute
    NORGEN_FILTER_ON_2ML='custom_norgen_96filterplate_on_2ml_deep'
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','24'))   # after Step 5 uses 3 more p300 tips
WELL_START=int(os.environ.get('WELL_START','0'))  # unused by this column-wise script
TUBE_BLOCK_2ML = globals().get('TUBE_BLOCK_2ML', 'opentrons_24_aluminumblock_nest_2ml_snapcap')

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5b – Norgen Elution',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

ELU_VOL  = 100   # µL per well
SMALL_SOURCE_MAX_UL = 4000
SINGLE_TUBE_MAX_UL = 2000
REAGENT_EXCESS = 1.2


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


def source_layout(total_ul):
    if total_ul < SMALL_SOURCE_MAX_UL:
        n_sources = 1 if total_ul <= SINGLE_TUBE_MAX_UL else 2
        return True, n_sources, total_ul / n_sources
    return False, 1, total_ul


def load_source(protocol, slot, total_ul):
    use_tubes, _, _ = source_layout(total_ul)
    return protocol.load_labware(TUBE_BLOCK_2ML if use_tubes else RESERVOIR_1, slot)


def make_source(labware, total_ul):
    use_tubes, n_sources, per_source = source_layout(total_ul)
    if use_tubes:
        wells = [labware.wells_by_name()[name] for name in ['A1', 'A2'][:n_sources]]
        return ReagentSource(wells, [per_source] * n_sources)
    return ReagentSource([labware.wells()[0]], [total_ul])


def source_prompt(slot, total_ul, label):
    use_tubes, n_sources, per_source = source_layout(total_ul)
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
    elu_total_ul = n_wells * ELU_VOL * REAGENT_EXCESS

    # ── Labware ───────────────────────────────────────────────────────────
    tips_300      = protocol.load_labware(TIPS_300,        9)
    filter_plate  = protocol.load_labware(NORGEN_FILTER_ON_2ML, 2)
    elu_res       = load_source(protocol, 4, elu_total_ul)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    elu_src  = make_source(elu_res, elu_total_ul)

    target_cols = filter_plate.columns()[start:stop]

    protocol.pause(
        "STEP 5b  ▶  Remove the kit collection plate and place the Norgen filter plate "
        "on a clean NEST 96-well 2 mL deep-well elution plate at SLOT 2. "
        f"{source_prompt(4, elu_total_ul, 'Norgen elution buffer')} Resume."
    )

    p300.pick_up_tip()
    for col in target_cols:
        for well in col:
            p300.aspirate(ELU_VOL, elu_src.aspiration_location(ELU_VOL))
            p300.dispense(ELU_VOL, well.top(-5))
            p300.blow_out(well.top(-5))
    p300.drop_tip()

    protocol.comment(
        "Step 5 complete. "
        "Centrifuge filter + elution plate 2 min at maximum speed or 2,000 RPM, RT. "
        "Confirm ~100 µL eluate per well. "
        "If processing batch 1 of 96: seal elution plate, refrigerate. "
        "Enter 0 at Zymo prompt in bash script and process batch 2 next."
    )
