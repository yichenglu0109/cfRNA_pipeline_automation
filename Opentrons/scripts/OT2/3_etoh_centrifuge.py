"""
OT-2  Step 3 – EtOH addition → [mix] → [centrifuge] → decant supernatant
               → re-lysis buffer → [60 °C incubate] → EtOH wash
Time  : ~8 hr (+10 min incubation, +30 sec centrifuge +1 min vortexing)
Tips  : p300 ×99 total (1 EtOH + 48 mix + 48 decant + 1 relysis + 1 wash)
        Requires 2 full p300 tip racks on deck before starting.

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml       – EtOH (150 mL 200-proof EtOH)
Slot 2 : custom_48_wellplate_7000ul   – 48-well sample plate
Slot 3 : nest_1_reservoir_195ml       – re-lysis buffer (20 mL); re-used for EtOH wash
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
    WELLPLATE_2ML='nest_96_wellplate_2ml_deep'
    PCR_PLATE='nest_96_wellplate_100ul_pcr_full_skirt'
    PLATE_48='custom_48_wellplate_7000ul'       # simulation substitute
    NORGEN_FILTER='custom_norgen_96filterplate'  # simulation substitute
    ZYMO_FILTER='custom_zymo_96filterplate'    # simulation substitute

# Pilot defaults; environment variables can still override these per run.
N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
TIP_START=int(os.environ.get('TIP_START','2'))    # after Step 1 uses 2 p300 tips
WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2

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


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    tips_a     = protocol.load_labware(TIPS_300, 9)
    tips_b     = protocol.load_labware(TIPS_300, 8)
    plate      = protocol.load_labware(PLATE_48,  2)
    etoh_res   = protocol.load_labware(RESERVOIR_1, 1)
    lysis_res  = protocol.load_labware(RESERVOIR_1, 3)
    liq_trash  = protocol.load_labware(PLATE_48,   5)

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_a, tips_b])
    p300.starting_tip = tips_a.wells()[TIP_START]

    etoh_src  = etoh_res.wells()[0]
    lysis_src = lysis_res.wells()[0]

    target_wells = plate.wells()[WELL_START:WELL_START + N_SAMPLES]

    # ════════════════════════════════════════════════════════════════════
    # PHASE 0 – Add EtOH (3000 µL/well = 12 × 250 µL; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 3A  ▶  Place sealed 48-well plate at SLOT 2. "
        "Add 150 mL 200-proof EtOH to reservoir at SLOT 1. "
        "Load 2 full p300 tip racks at SLOTS 8 and 9. "
        "Remove seal from plate. Resume when ready."
    )

    etoh_iters    = math.ceil(ETOH_VOL / 250)             # 3000 → 12
    etoh_per_disp = round(ETOH_VOL / etoh_iters, 1)      # 250 µL

    p300.pick_up_tip()
    for well in target_wells:
        for _ in range(etoh_iters):
            p300.aspirate(etoh_per_disp, etoh_src.bottom(2))
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
        "Add 20 mL preheated lysis buffer to reservoir at SLOT 3. "
        "Move plate to SLOT 2. Resume."
    )

    p300.pick_up_tip()
    for well in target_wells:
        p300.aspirate(300, lysis_src.bottom(2))
        p300.dispense(300, well.top(-20))
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
        "STEP 3F  ▶  Empty SLOT 3 reservoir and add 20 mL 200-proof EtOH. "
        "Remove seal from plate and return to SLOT 2. Resume."
    )

    p300.pick_up_tip()
    for well in target_wells:
        p300.aspirate(300, lysis_src.bottom(2))
        p300.dispense(300, well.top(-20))
        p300.blow_out(well.top(-20))
    p300.drop_tip()

    protocol.comment(
        "Step 3 complete. Seal plate and vortex 1 min. "
        "Proceed to Step 4 (transfer to Norgen filter plate)."
    )
