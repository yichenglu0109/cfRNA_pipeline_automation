"""
OT-2  Step 3 – EtOH addition → [mix] → [centrifuge] → decant supernatant
               → re-lysis buffer → [60 °C incubate] → EtOH wash
Time  : ~8 hr (+10 min incubation, +30 sec centrifuge +1 min vortexing)
Tips  : p300 ×99 total (1 EtOH + 48 mix + 48 decant + 1 relysis + 1 wash)
        Requires 2 full p300 tip racks on deck before starting.

Deck layout
-----------
Slot 1 : dynamic reagent source        – EtOH
Slot 2 : custom_48_wellplate_7000ul   – 48-well sample plate
Slot 3 : dynamic reagent source        – re-lysis buffer; re-used for EtOH wash
Slot 5 : custom_48_wellplate_7000ul   – liquid trash (open container, e.g. empty tip box)
Slot 8 : opentrons_96_tiprack_300ul
Slot 9 : opentrons_96_tiprack_300ul

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
    N_SAMPLES=int(os.environ.get('N_SAMPLES','4'))
    TIP_START=int(os.environ.get('TIP_START','2'))    # after Step 1 uses 2 p300 tips
    WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2
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
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
TIP_START=int(os.environ.get('TIP_START','2'))    # after Step 1 uses 2 p300 tips
WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2
TUBE_BLOCK_2ML = globals().get('TUBE_BLOCK_2ML', 'opentrons_24_aluminumblock_nest_2ml_snapcap')

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 3 – EtOH / Centrifuge / Decant / Re-lysis',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}

# Well cross-section 16×8=128 mm²; post-EtOH liquid ~39 mm.
# Heights cover 37→4 mm; 12 levels × 2 reps × 250 µL = 6000 µL capacity.
DECANT_HEIGHTS = [37, 34, 30, 26, 22, 18, 14, 10, 8, 6, 5, 4]
DECANT_VOL     = 250   # µL per aspirate step (p300)
DECANT_REPS    = 2     # reps per height
RELYSIS_VOL    = 300
WASH_VOL       = 300
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
    etoh_total_ul = N_SAMPLES * ETOH_VOL * REAGENT_EXCESS
    relysis_total_ul = N_SAMPLES * RELYSIS_VOL * REAGENT_EXCESS
    wash_total_ul = N_SAMPLES * WASH_VOL * REAGENT_EXCESS
    slot3_load_ul = max(relysis_total_ul, wash_total_ul)

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a     = protocol.load_labware(TIPS_300, 9)
    tips_b     = protocol.load_labware(TIPS_300, 8)
    plate      = protocol.load_labware(PLATE_48,  2)
    etoh_res   = load_source(protocol, 1, etoh_total_ul)
    lysis_res  = load_source(protocol, 3, slot3_load_ul)
    liq_trash  = protocol.load_labware(PLATE_48,   5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_a, tips_b])
    p300.starting_tip = tips_a.wells()[TIP_START]

    etoh_src  = make_source(etoh_res, etoh_total_ul)

    target_wells = plate.wells()[WELL_START:WELL_START + N_SAMPLES]

    # ════════════════════════════════════════════════════════════════════
    # PHASE 0 – Add EtOH (3000 µL/well = 12 × 250 µL; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3A  ▶  Place sealed 48-well plate at SLOT 2. "
        f"{source_prompt(1, etoh_total_ul, '200-proof EtOH')} "
        "Load 2 full p300 tip racks at SLOTS 8 and 9. "
        "Remove seal from plate. Resume when ready."
    )

    etoh_iters    = math.ceil(ETOH_VOL / 250)             # 3000 → 12
    etoh_per_disp = round(ETOH_VOL / etoh_iters, 1)      # 250 µL

    p300.pick_up_tip()
    for well in target_wells:
        for _ in range(etoh_iters):
            p300.aspirate(etoh_per_disp, etoh_src.aspiration_location(etoh_per_disp))
            p300.air_gap(10)
            p300.dispense(etoh_per_disp, well.top(-5))
            p300.blow_out(well.top(-5))
    p300.drop_tip()

    protocol.pause(
        "STEP 3B  ▶  Seal plate and vortex ≥30 s to mix EtOH with sample. "
        "Briefly spin/tap down if liquid remains on the seal or well walls. "
        "Then centrifuge 30 sec at 1,000 g (RT) to pellet slurry. "
        "Return plate to SLOT 2 unsealed. Resume."
    )

    # ════════════════════════════════════════════════════════════════════
    # PHASE 1 – Decant supernatant (~5.88 mL/well; new tip per well)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3C  ▶  Place open liquid-waste container at SLOT 5. Resume."
    )

    trash_wells = liq_trash.wells()

    for i, well in enumerate(target_wells):
        trash_dest = trash_wells[(WELL_START + i) % len(trash_wells)]
        p300.pick_up_tip()
        for h in DECANT_HEIGHTS:
            for _ in range(DECANT_REPS):
                p300.aspirate(DECANT_VOL, well.bottom(h), rate=0.5)
                p300.air_gap(10)
                p300.dispense(DECANT_VOL + 10, trash_dest.bottom(35))
                protocol.delay(seconds=0.2)
                p300.blow_out(trash_dest.top())
        p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # PHASE 2 – Add re-lysis buffer (300 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3D  ▶  Remove liquid-waste container from SLOT 5. "
        f"{source_prompt(3, relysis_total_ul, 'preheated lysis buffer')} "
        "Move plate to SLOT 2. Resume."
    )

    lysis_src = make_source(lysis_res, relysis_total_ul)
    p300.pick_up_tip()
    for well in target_wells:
        p300.aspirate(RELYSIS_VOL, lysis_src.aspiration_location(RELYSIS_VOL))
        p300.dispense(RELYSIS_VOL, well.top(-20))
        p300.blow_out(well.top(-20))
    p300.drop_tip()

    protocol.pause(
        "STEP 3E  ▶  Seal plate and vortex ≥30 s. "
        "Incubate at 60 °C for 10 min. "
        "If this is the FIRST batch of 48: keep incubator at 60 °C. "
        "If this is the SECOND batch or there is only one batch of samples: set incubator to 37 °C for DNase. "
        "Resume after incubation completes."
    )

    # ════════════════════════════════════════════════════════════════════
    # PHASE 3 – Add EtOH wash (300 µL/well; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3F  ▶  Empty the SLOT 3 reagent source. "
        f"{source_prompt(3, wash_total_ul, '200-proof EtOH')} "
        "Remove seal from plate and return to SLOT 2. Resume."
    )

    wash_src = make_source(lysis_res, wash_total_ul)
    p300.pick_up_tip()
    for well in target_wells:
        p300.aspirate(WASH_VOL, wash_src.aspiration_location(WASH_VOL))
        p300.dispense(WASH_VOL, well.top(-20))
        p300.blow_out(well.top(-20))
    p300.drop_tip()

    protocol.comment(
        "Step 3 complete. Seal plate and vortex 1 min. "
        "Proceed to Step 4 (transfer to Norgen filter plate)."
    )
