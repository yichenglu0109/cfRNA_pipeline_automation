"""
OT-2  Step 1 – Add slurry + lysis buffer to 48-well plate
Time  : ~35 min  (p300 single; per-well operations)
Tips  : 2 tips total (1 slurry + 1 lysis)

Deck layout
-----------
Slot 1 : nest_1_reservoir_195ml       – lysis buffer A + 1.2% B-ME
Slot 2 : custom_48_wellplate_7000ul   – plate (moved here before lysis step)
Slot 4 : nest_1_reservoir_195ml       – slurry (~10.5 mL)
Slot 5 : custom_48_wellplate_7000ul   – plate (starts here for slurry step)
Slot 9 : opentrons_96_tiprack_300ul

Pipettes
--------
Left : p300_single_gen2
"""

import math
import sys, os
try:
    sys.path.insert(0, '/data/user_storage/cfRNA')
    from config import *
except ImportError:
    LYSIS_VOL=float(os.environ.get('LYSIS_VOL','1800'))
    ETOH_VOL=float(os.environ.get('ETOH_VOL','3000'))
    START_COL=int(os.environ.get('START_COL','0'))
    STOP_COL=int(os.environ.get('STOP_COL','6'))
    FILTER_COL_START=int(os.environ.get('FILTER_COL_START','0'))
    N_SAMPLES=int(os.environ.get('N_SAMPLES','8'))
    TIP_START=int(os.environ.get('TIP_START','0'))    # 0=A1, 1=B1, ..., 8=A2
    WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 9=A2
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
N_SAMPLES=int(os.environ.get('N_SAMPLES','16'))
TIP_START=int(os.environ.get('TIP_START','9'))    # 0=A1, 1=B1, ..., 8=A2
WELL_START=int(os.environ.get('WELL_START','0'))  # 0=A1, 1=B1, ..., 8=A2

from opentrons import protocol_api

metadata = {
    'protocolName': 'cfRNA Step 1 – Slurry + Lysis Buffer',
    'author': 'Peter Lu, adapted from Moufarrej & Quake (2023) Nature Protocols',
    'apiLevel': '2.13',
}


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    tips_300   = protocol.load_labware(TIPS_300,    9)
    plate_A    = protocol.load_labware(PLATE_48,    5)   # slurry step
    plate_B    = protocol.load_labware(PLATE_48,    2)   # lysis step
    slurry_res = protocol.load_labware(RESERVOIR_1, 4)   # slurry
    lysis_res  = protocol.load_labware(RESERVOIR_1, 1)   # lysis buffer

    # ── Pipettes ──────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])
    p300.starting_tip = tips_300.wells()[TIP_START]

    slurry_src  = slurry_res.wells()[0]   # single-well reservoir
    lysis_src   = lysis_res.wells()[0]
    target_wells = plate_A.wells()[WELL_START:WELL_START + N_SAMPLES]

    # ════════════════════════════════════════════════════════════════════
    # STEP A – Slurry (200 µL per well, slow aspirate; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 1A  ▶  Place 48-well plate at SLOT 5. "
        "Vortex preheated slurry and add 10.5 mL to reservoir at SLOT 4. "
        "Resume when ready."
    )

    p300.pick_up_tip()
    for well in target_wells:
        p300.mix(1, 100, slurry_src.bottom(2))
        p300.aspirate(200, slurry_src.bottom(2), rate=0.2)
        protocol.delay(seconds=1.5)
        p300.air_gap(10)
        p300.dispense(210, well.top(-30))
        p300.blow_out(well.top(-30))
    p300.drop_tip()

    # ════════════════════════════════════════════════════════════════════
    # STEP B – Lysis buffer (1800 µL per well; 8 × 225 µL; 1 tip reused)
    # ════════════════════════════════════════════════════════════════════
    protocol.pause(
        "STEP 1B  ▶  Move 48-well plate to SLOT 2. "
        "Add ~40 mL preheated lysis buffer (+ 1.2% B-ME) to the "
        "reservoir at SLOT 1 (refill in ~40 mL batches to prevent "
        "crystallisation). Resume when ready."
    )

    iters    = math.ceil(LYSIS_VOL / 250)        # 1800 → 8
    per_disp = round(LYSIS_VOL / iters, 1)       # 225.0 µL

    target_wells_B = plate_B.wells()[WELL_START:WELL_START + N_SAMPLES]
    p300.pick_up_tip()
    for well in target_wells_B:
        for _ in range(iters):
            p300.aspirate(per_disp, lysis_src.bottom(2))
            p300.dispense(per_disp, well.top(-20))
            p300.blow_out(well.top(-20))
    p300.drop_tip()

    protocol.comment(
        "Step 1 complete. "
        "Proceed manually: transfer samples into plate at slot 2 "
        "using a multichannel P1000 (mix each column ≥5×). "
        "Seal plate and incubate at 60 °C for 10 min."
    )
