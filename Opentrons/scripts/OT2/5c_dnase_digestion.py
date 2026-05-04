"""
OT-2  Step 5c – DNase digestion on Norgen elution plate
Estimated Time  : ~40 min robot  (+20 min incubation at 37 °C)
Tips  : p20 × 1 tip

Deck layout
-----------
Slot 2 : thermoscientificnunc_96_wellplate_2000ul – elution plate from Step 5
Slot 4 : dynamic reagent source        – DNase master mix
                                         (LoBind tube[s] or reservoir; 10% excess)
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
    TUBE_BLOCK_2ML='opentrons_24_aluminumblock_nest_2ml_snapcap'
    WELLPLATE_2ML='thermoscientificnunc_96_wellplate_2000ul'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'
    NORGEN_FILTER='custom_norgen_96filterplate'
    ZYMO_FILTER='custom_zymo_96filterplate'

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
TIP_START=int(os.environ.get('TIP_START','0'))    # fresh p20 rack in slot 6
WELL_START=int(os.environ.get('WELL_START','0'))  # unused by this column-wise script
TUBE_BLOCK_2ML = globals().get('TUBE_BLOCK_2ML', 'opentrons_24_aluminumblock_nest_2ml_snapcap')

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 5c – DNase Digestion',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

DNASE_VOL = 13   # µL per well (11 µL 10× buffer + 2 µL DNase)
SMALL_SOURCE_MAX_UL = 4000
SINGLE_TUBE_MAX_UL = 2000


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
    master_mix_ul = round(n_wells * DNASE_VOL * 1.1)   # 10% excess

    # ── Labware ───────────────────────────────────────────────────────────
    tips_20       = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    elution_plate = protocol.load_labware(WELLPLATE_2ML, 2)
    dnase_res     = load_source(protocol, 4, master_mix_ul)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tips_20])
    p20.starting_tip = tips_20.wells()[TIP_START]

    dnase_src   = make_source(dnase_res, master_mix_ul)
    target_cols = elution_plate.columns()[start:stop]

    protocol.pause(
        f"STEP 5c  ▶  Place the 2 mL deep-well elution plate (from Step 5b) at SLOT 2. "
        f"Prepare DNase master mix: 11 µL 10× DNase buffer + 2 µL DNase per well "
        f"({master_mix_ul} µL total for {n_wells} wells, 10% excess). "
        f"{source_prompt(4, master_mix_ul, 'DNase master mix')} Resume."
    )

    p20.pick_up_tip()
    for col in target_cols:
        for well in col:
            p20.aspirate(DNASE_VOL, dnase_src.aspiration_location(DNASE_VOL))
            p20.dispense(DNASE_VOL, well.bottom(5))
            p20.blow_out(well.bottom(8))
    p20.drop_tip()

    protocol.comment(
        "Step 5c complete. "
        "Vortex plate lightly. "
        "Incubate at 37 °C for 20 min. "
        "Proceed to Step 6 (Zymo Clean & Concentrate)."
    )
