# 15 mL Tube-Based Semi-Automated cfRNA Extraction on OT-2

Author: Peter Lu  
Date: 2026-05-16

This is the operating protocol for the tube-based OT-2 pilot scripts in this directory. It is intended for an operator standing at the robot. The OT-2 performs repetitive liquid handling; the user loads reagents, caps/uncaps tubes, vortexes, centrifuges, swaps collection/elution tubes, and confirms setup at each pause.

The current tube scripts default to **4 samples** using `p300_single_gen2` and `p20_single_gen2`. They do not replace the plate-based scripts in `Opentrons/scripts/OT2`.

## Overview

The tube workflow follows the same stages as the plate workflow:

1. RNA extraction in 15 mL conical sample tubes and individual Norgen columns.
2. DNase digestion of the Norgen eluate in 1.5 mL elution tubes.
3. RNA cleanup and concentration using individual Zymo columns.

Current tube pilot scripts:

| Stage | Section | Script | Purpose |
|---|---|---|---|
| RNA extraction | Step 1 | `1_add_slurry_lysis_tube.py` | Add slurry and lysis buffer to 15 mL conical sample tubes |
| RNA extraction | Step 2 | manual | Add samples, mix, incubate |
| RNA extraction | Step 3 | `3_etoh_centrifuge_tube.py` | Add EtOH, vortex, pellet, decant, re-lysis, EtOH wash |
| RNA extraction | Step 4 | `4_transfer_to_norgen_column_tube.py` | Transfer sample slurry to Norgen columns |
| RNA extraction | Step 5 | `5_norgen_wash_tube.py` | Wash Norgen columns and dry spin |
| RNA extraction | Step 5b | `5b_norgen_elute_tube.py` | Elute Norgen columns into 1.5 mL elution tubes |
| DNA digestion | Step 5c | `5c_dnase_digestion_tube.py` | Add DNase master mix |
| Cleanup | Step 6 | `6_zymo_clean_conc_tube.py` | Zymo binding, washes and final elution |

## Hardware Configuration

The scripts assume:

- `p300_single_gen2` on the left mount
- `p20_single_gen2` on the right mount
- one shared `opentrons_24_aluminumblock_nest_2ml_snapcap` at slot 4 for Norgen/Zymo columns, eluates and small reagents
- 3D-printed 15 mL tube rack at slot 2

Upload this custom labware JSON in the Opentrons App before uploading the scripts:

`labware/3dprinted_15_tuberack_15000ul.json`

The scripts load it by load name:

```python
SAMPLE_TUBE_RACK = "3dprinted_15_tuberack_15000ul"
```

The JSON is provisional. After measuring the physical rack, edit `x`, `y`,
`diameter`, `depth`, and `dimensions` in the JSON, then re-upload it in the App.
Use normal Opentrons labware offset calibration for whole-rack deck placement
after the geometry is correct. The shared 24-block remains the canonical
`opentrons_24_aluminumblock_nest_2ml_snapcap`.

The 3D-printed rack definition uses the standard slot 2 footprint
(`127.76 mm x 85.48 mm`), so slots 1 and 3 are available unless a physical
clearance check shows your printed rack overhangs. Reservoir steps use slot 5.

### Physical Placement Guide

Use slot 2 as the reference footprint. The current JSON has a 3 row x 5 column
layout (`A1-C5`). Sample and waste 15 mL tube positions are explicit so the
same positions are used across all scripts. Defaults:

```bash
SAMPLE_TUBES=A1,A2,A3,A4
TRASH_TUBES=C1,C2,C3,C4
```

Step 3 uses these `TRASH_TUBES` positions in the same slot 2 rack, so no second
15 mL waste rack is required by default. Row B is intentionally unused in the
default 4-sample layout.

## Shared 24-Tube Rack Map

The shared 24-tube rack is loaded at slot 4 in all scripts that use small tubes.

| Position | Contents |
|---|---|
| A1 | Sample 1 Norgen column during Steps 4-5b, then Norgen eluate / Zymo input |
| B1 | Sample 2 Norgen column during Steps 4-5b, then Norgen eluate / Zymo input |
| C1 | Sample 3 Norgen column during Steps 4-5b, then Norgen eluate / Zymo input |
| D1 | Sample 4 Norgen column during Steps 4-5b, then Norgen eluate / Zymo input |
| A2 | Sample 1 Zymo column during Step 6 |
| B2 | Sample 2 Zymo column during Step 6 |
| C2 | Sample 3 Zymo column during Step 6 |
| D2 | Sample 4 Zymo column during Step 6 |
| A4 | DNase master mix |
| B4 | Zymo binding buffer, or re-lysis buffer during Step 3 |
| C4 | Zymo EtOH |
| D4 | Zymo prep buffer, or Norgen wash buffer during Step 5 |
| A5 | Zymo wash buffer 2 |
| B5 | Nuclease-free water |
| C5 | Slurry in Step 1, then Norgen elution buffer in Step 5b, then Zymo wash buffer 1 tube 1 in Step 6 |
| D5 | Zymo wash buffer 1 tube 2 in Step 6 |

The scripts pause before a position is reused. Relabel tubes clearly before starting.

## Reagent Setup

Default volumes are inherited from the plate-based protocol:

| Reagent | Per sample |
|---|---:|
| Slurry | 200 uL |
| Lysis buffer | 1800 uL |
| EtOH for extraction | 3000 uL |
| Re-lysis buffer | 300 uL |
| EtOH wash after re-lysis | 300 uL |
| Norgen wash buffer | 400 uL per wash, 3 washes |
| Norgen elution buffer | 100 uL |
| DNase master mix | 13 uL |
| Zymo binding buffer | 226 uL |
| Zymo EtOH | 339 uL |
| RNA prep buffer | 400 uL |
| Zymo wash 1 | 700 uL |
| Zymo wash 2 | 400 uL |
| Final nuclease-free water | 15 uL |

The scripts include reagent excess when prompting for source volumes. Pre-warmed slurry and lysis buffer can crystallize or clog tips if cooled; work promptly after vortexing and loading.

## Calibration and Validation

Most shared heights are centralized in `config.py`, but the current standalone tube scripts also carry their own fallback values. Before real samples, confirm the uploaded script values match the table below and run water or dyed-water checks for:

| Operation | Current config constant |
|---|---|
| Step 1 slurry/lysis dispense into 15 mL tubes | `SAMPLE_TOP_DISPENSE_OFFSET`, current Step 1 fallback `top(5)` |
| Step 3 EtOH/re-lysis/wash dispense into 15 mL tubes | `SAMPLE_TOP_DISPENSE_OFFSET`, current Step 3 fallback `top(-10)` |
| Step 3 decant waste dispense | `TRASH_DISPENSE_H`, current Step 3 fallback `bottom(50)` |
| Step 3 staged decant | `DECANT_HEIGHTS`, current Step 3 fallback `45,41,37,33,29,25,21,17,13,11,8.5,6.5` |
| 15 mL conical tube mixing | `SAMPLE_MIX_LOW_H`, `SAMPLE_MIX_HIGH_H` |
| 2 mL reagent tube aspiration | `REAGENT_TUBE_ASPIRATE_H`, default `bottom(1.0)` |
| DNase-treated eluate tube aspiration into Zymo | `ZYMO_INPUT_ASPIRATE_H`, default `bottom(2.0)` |
| slurry tube aspiration | `SLURRY_TUBE_ASPIRATE_H`, default `bottom(2)` |
| DNase dispense / blowout | `DNASE_DISPENSE_H`, `DNASE_BLOWOUT_H`, defaults `bottom(5)` and `bottom(8)` |
| Step 5/5b/6 shared 24-block safe travel after low tube/column moves | `SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP`, default `top(25)` |
| Step 4 15 mL sample/slurry aspiration into Norgen | `SAMPLE_ASPIRATE_H`, current Step 4 fallback `bottom(0.5)` |
| Norgen column load/wash dispense / blowout | `NORGEN_COLUMN_DISPENSE_FROM_TOP`, `NORGEN_COLUMN_BLOWOUT_FROM_TOP`, defaults `top(-3)` and `top(0)` |
| Norgen elution placement | `NORGEN_ELUTE_FROM_TOP`, default `top(-12)` |
| Step 6 binding/EtOH dispense into DNase-treated eluate tubes | `SAMPLE_DISPENSE_H`, current Step 6 fallback `bottom(30)` |
| Zymo column load/wash dispense / blowout | `ZYMO_COLUMN_DISPENSE_FROM_TOP`, `ZYMO_COLUMN_BLOWOUT_FROM_TOP`, defaults `top(0)` and `top(0)` |
| Zymo final elution placement / blowout | `ZYMO_ELUTE_FROM_TOP`, `ZYMO_ELUTE_BLOWOUT_FROM_TOP`, defaults `top(-12)` and `top(-8)` |

Prior OT2 small-sample scripts used the 24-block as reagent source at `bottom(1.5)` for most LoBind reagents and `bottom(2)` for slurry. This tube pilot defaults reagent aspiration to `bottom(1.0)` after clearance checks showed enough room, while keeping slurry at `bottom(2)`. Norgen and Zymo column heights are separated because column/no-column, Norgen/Zymo geometry, and 1.5 mL/2 mL receiver height can differ.

Example height override:

```bash
N_SAMPLES=4 \
NORGEN_COLUMN_DISPENSE_FROM_TOP=-3 \
NORGEN_ELUTE_FROM_TOP=-12 \
REAGENT_TUBE_ASPIRATE_H=1.0 \
ZYMO_INPUT_ASPIRATE_H=2.0 \
SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP=25 \
opentrons_execute 6_zymo_clean_conc_tube.py
```

Critical step: `bottom(0)` is not guaranteed physical clearance. Validate low positions after installing or changing labware definitions, tip types, or deck offsets.

## Run Settings

Recommended pilot commands:

```bash
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TRASH_TUBES=C1,C2 TIP_START=49 opentrons_execute 1_add_slurry_lysis_tube.py
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TRASH_TUBES=C1,C2 TIP_START=50 opentrons_execute 3_etoh_centrifuge_tube.py
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TIP_START=54 opentrons_execute 4_transfer_to_norgen_column_tube.py
N_SAMPLES=4 TIP_START=32 opentrons_execute 5_norgen_wash_tube.py
N_SAMPLES=4 TIP_START=33 opentrons_execute 5b_norgen_elute_tube.py
N_SAMPLES=4 P20_TIP_START=0 opentrons_execute 5c_dnase_digestion_tube.py
N_SAMPLES=4 TIP_START=40 P20_TIP_START=0 opentrons_execute 6_zymo_clean_conc_tube.py
```

Tip starts above match the current standalone script fallbacks. Do not include spaces inside comma-separated tube lists; use `SAMPLE_TUBES=A1,A2`, not `SAMPLE_TUBES=A1, A2`.

## Rack Position / Water Test

Before running samples, upload `labware/3dprinted_15_tuberack_15000ul.json`, then
upload and run `test_3dprinted_15ml_positions_water.py`.

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `3dprinted_15_tuberack_15000ul` | empty 15 mL tubes in A1/A2/A3/A4/C1/C2/C3/C4 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

The test is now a no-liquid safety check. It moves the p300 over
A1/A2/A3/A4/C1/C2/C3/C4 at `top(10.0)` only, pauses, then repeats the hover path in reverse.
It does not aspirate, dispense, or enter the tubes.

## Procedure

### Step 1 (`1_add_slurry_lysis_tube.py`): Slurry and lysis buffer addition

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `3dprinted_15_tuberack_15000ul` | 15 mL conical sample tubes |
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | slurry in C5 |
| 5 | `nest_1_reservoir_195ml` | lysis buffer + 1.2% B-ME |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place the current sample tubes in the sample rack. Current standalone Step 1 defaults to A1 and A2.
2. Vortex preheated slurry thoroughly.
3. Add the prompted slurry volume to shared-rack tube C5.
4. Run `1_add_slurry_lysis_tube.py`.
5. The robot adds 200 uL slurry to each 15 mL conical sample tube and blows out at `tube.top(5)`.
6. When prompted, add preheated lysis buffer + 1.2% B-ME to the slot 5 reservoir.
7. Resume. The robot adds 1800 uL lysis buffer to each sample tube and blows out at `tube.top(5)`.

Pause point: manually add sample to each tube, mix thoroughly, cap, and incubate at 60 C for 10 min.

### Step 2 (manual): Sample addition and incubation

1. Add samples or controls to the prepared lysis/slurry tubes.
2. Mix each tube thoroughly by pipetting or vortexing.
3. Cap tubes and incubate at 60 C for 10 min.
4. Briefly spin or tap down liquid before Step 3.

Keep tubes capped except during active pipetting.

### Step 3 (`3_etoh_centrifuge_tube.py`): EtOH, decant, re-lysis and EtOH wash

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | 15 mL tube rack | post-incubation sample tubes in `SAMPLE_TUBES`; open waste tubes in `TRASH_TUBES` |
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | re-lysis buffer, then EtOH wash in B4 |
| 5 | `nest_1_reservoir_195ml` | 200-proof EtOH |
| 8, 9 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Add prompted 200-proof EtOH volume to the slot 5 reservoir.
2. Resume. The robot adds 3000 uL EtOH to each sample tube.
3. Cap tubes, vortex at least 30 sec, centrifuge 30 sec at 1,000 g, then return uncapped tubes to slot 2.
4. Place open liquid-waste tubes in `TRASH_TUBES` wells of the same slot 2 rack.
5. Resume. The robot decants supernatant by staged heights down to `bottom(6.5)` and dispenses waste to `bottom(50)` in the paired waste tubes.
6. Add prompted preheated re-lysis buffer to tube B4 and resume.
7. Cap tubes, vortex at least 30 sec, incubate at 60 C for 10 min.
8. Replace B4 contents with prompted 200-proof EtOH wash and resume. Step 3 currently dispenses additions at `tube.top(-10)`.

Pause point: cap and vortex tubes to resuspend slurry/EtOH mixture, briefly spin or tap down, then continue immediately to Step 4.

### Step 4 (`4_transfer_to_norgen_column_tube.py`): Transfer to Norgen columns

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `3dprinted_15_tuberack_15000ul` | freshly vortexed sample tubes |
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | Norgen columns with collection tubes in A1-D1 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place freshly vortexed sample tubes at slot 2.
2. Place Norgen columns with collection tubes in slot 4 positions A1-D1.
3. For each sample prompt, vortex that tube, briefly spin or tap down, uncap only that tube, and resume.
4. The robot mixes and transfers sample slurry to the matching Norgen column. Current Step 4 fallback aspirates from the 15 mL source at `bottom(0.5)`.
5. After all samples are loaded, centrifuge columns 2 min at maximum speed or 2,000 RPM, RT.
6. Discard flow-through.

### Step 5 (`5_norgen_wash_tube.py`): Norgen washes

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | Norgen columns A1-D1 and Norgen wash buffer D4 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place Norgen columns with collection tubes in slot 4 positions A1-D1.
2. Add prompted Norgen wash buffer to tube D4.
3. Resume. The robot adds 400 uL wash buffer to each column.
   Step 5 uses `SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP=25` after wash source aspiration and after column dispense/blowout before moving across the 24-block.
4. Centrifuge 2 min at maximum speed or 2,000 RPM, RT. Discard flow-through.
5. Repeat for wash 2.
6. Repeat for wash 3, then centrifuge 5 min at 2,000 RPM, RT for dry spin.
7. Discard flow-through.

### Step 5b (`5b_norgen_elute_tube.py`): Norgen elution

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | dry-spun Norgen columns on clean elution tubes A1-D1; Norgen elution buffer C5 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place dry-spun Norgen columns on clean 1.5 mL elution tubes in A1-D1.
2. Keep final eluate identity mapped to A1-D1.
3. Add prompted Norgen elution buffer to C5.
4. Resume. The robot adds 100 uL elution buffer to each column.
   Step 5b uses `SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP=25` after C5 source aspiration and after Norgen column elution/blowout before moving across the 24-block.
5. Centrifuge 2 min at maximum speed or 2,000 RPM, RT.
6. Keep eluates in shared rack positions A1-D1 in sample order.

### Step 5c (`5c_dnase_digestion_tube.py`): DNase digestion

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | eluates A1-D1, DNase master mix A4 |
| 7 | `opentrons_96_tiprack_20ul` | p20 tips |

1. Prepare DNase master mix: 11 uL 10x DNase buffer + 2 uL DNase per sample, with excess.
2. Add prompted master mix volume to A4.
3. Resume. The robot adds 13 uL DNase master mix to each eluate.
4. Cap tubes, vortex lightly, and incubate at 37 C for 20 min.

### Step 6 (`6_zymo_clean_conc_tube.py`): Zymo clean and concentrate

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | DNase-treated samples A1-D1, Zymo columns A2-D2 and small reagents |
| 7 | `opentrons_96_tiprack_20ul` | p20 tips |
| 8, 9 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place DNase-treated samples in A1-D1.
2. Add prompted Zymo binding buffer to B4. Resume. Step 6 currently dispenses binding buffer to A1-D1 at `bottom(30)`.
3. Add prompted 100% EtOH to C4. Resume. Step 6 currently dispenses EtOH to A1-D1 at `bottom(30)`.
4. Cap and vortex sample tubes at least 30 sec.
5. Place Zymo columns with collection tubes in slot 4 positions A2-D2. Resume.
6. The robot loads each sample onto the matching Zymo column.
7. Centrifuge 5 min at 3,000-5,000 g, RT. Discard flow-through.
8. Add prompted RNA prep buffer to D4. Resume, then centrifuge and discard flow-through.
9. Add prompted Zymo wash buffer 1 to C5 and D5. Resume, then centrifuge and replace collection tubes.
10. Add prompted Zymo wash buffer 2 to A5. Resume, then centrifuge and discard flow-through plus collection tubes.
11. Place columns on final clean elution tubes.
12. Add prompted nuclease-free water to B5. Resume.
13. Centrifuge final columns 5 min at 3,000-5,000 g.
14. Confirm about 15 uL final eluate per sample and freeze at -80 C.

## Workflow Completion Checklist

| Workflow step | Completed | Notes |
|---|---|---|
| Labware names installed or environment overrides set | [ ] |  |
| Deck calibration and labware offsets confirmed | [ ] |  |
| 15 mL tube and column heights validated with water/dye | [ ] |  |
| Step 1 slurry and lysis added | [ ] |  |
| Step 2 sample addition and 60 C incubation complete | [ ] |  |
| Step 3 EtOH, decant, re-lysis and EtOH wash complete | [ ] |  |
| Step 4 Norgen transfer and centrifugation complete | [ ] |  |
| Step 5 Norgen washes and dry spin complete | [ ] |  |
| Step 5b Norgen elution complete | [ ] |  |
| Step 5c DNase addition and 37 C incubation complete | [ ] |  |
| Step 6 Zymo cleanup and final elution complete | [ ] |  |
| Final eluate volume and operational notes recorded | [ ] |  |

## Data to Record

| Field | Notes |
|---|---|
| Sample ID | Preserve A1-D1 order through Norgen and Zymo |
| Input volume | Same across all samples if possible |
| Reagent lot | Norgen kit, Zymo kit, EtOH, DNase |
| Final eluate volume observed | Record low-volume samples |
| Clogging or slow flow | Record Norgen and Zymo separately |
| Pellet/slurry carryover | Especially after Step 3 decant and Step 4 transfer |
| Height/calibration notes | Any tip contact, splashing, missed liquid or residual volume |
| RNA concentration/profile | Bioanalyzer or downstream QC |
