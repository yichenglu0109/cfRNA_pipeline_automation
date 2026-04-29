"""
Shared configuration for cfRNA OT-2 pipeline.
Parameters can be overridden via environment variables:
    LYSIS_VOL=1800 ETOH_VOL=3000 opentrons_execute script.py
"""
import os

# ── Volumetric parameters (µL) ─────────────────────────────────────────────
LYSIS_VOL  = float(os.environ.get('LYSIS_VOL',  '1800'))  # lysis buffer per column
ETOH_VOL   = float(os.environ.get('ETOH_VOL',   '3000'))  # EtOH per column (step 3)
START_COL  = int(os.environ.get('START_COL',  '0'))        # 0-indexed; batch 1=0, batch 2=6
STOP_COL   = int(os.environ.get('STOP_COL',   '6'))        # exclusive; 6 for 48 samples, 12 for 96
N_SAMPLES  = int(os.environ.get('N_SAMPLES',  '48'))       # total wells to process; 2 for quick test
FILTER_COL_START = int(os.environ.get('FILTER_COL_START', '0'))  # 0-indexed column; batch 1=0, batch 2=6

# ── Standard Opentrons labware ─────────────────────────────────────────────
TIPS_200      = 'opentrons_96_filtertiprack_200ul'
TIPS_300      = 'opentrons_96_tiprack_300ul'
TIPS_1000     = 'opentrons_96_filtertiprack_1000ul'
RESERVOIR_1   = 'nest_1_reservoir_195ml'    # 195 mL single trough
RESERVOIR_12  = 'nest_12_reservoir_15ml'    # 12 separate 22 mL troughs
WELLPLATE_2ML = 'thermoscientificnunc_96_wellplate_2000ul'
PCR_PLATE     = 'nest_96_wellplate_100ul_pcr_full_skirt'

# ── Custom labware (JSON must be installed at /data/labware/ on robot) ─────
# Use Opentrons Labware Creator: https://labware.opentrons.com/create/
PLATE_48      = 'custom_48_wellplate_7000ul'     # Thomas Scientific 1149Q15
                                                  # 8 rows (A-H) × 6 cols, 9mm col spacing,
                                                  # 18mm row spacing, 7 mL/well, depth 65 mm
NORGEN_FILTER = 'custom_norgen_96filterplate'     # Norgen filter plate on kit collection plate
NORGEN_FILTER_ON_2ML = 'custom_norgen_96filterplate_on_2ml_deep'
ZYMO_FILTER   = 'custom_zymo_96filterplate'       # Zymo filter plate (from kit R1080)

API_LEVEL = '2.13'
