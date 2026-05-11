# Tube-Based Semi-Automated cfRNA Extraction on OT-2

Author: Peter Lu  
Date: 2026-05-09

This is the operating protocol for the tube-based OT-2 pilot scripts in this directory. It is intended for an operator standing at the robot. The OT-2 performs repetitive liquid handling; the user loads reagents, caps/uncaps tubes, vortexes, centrifuges, swaps collection/elution tubes, and confirms setup at each pause.

This first tube pilot is designed for **4 samples** using `p300_single_gen2` and `p20_single_gen2`. It does not replace the plate-based scripts in `Opentrons/scripts/OT2`.

## Overview

The tube workflow follows the same stages as the plate workflow:

1. RNA extraction in 15 mL conical sample tubes and individual Norgen columns.
2. DNase digestion of the Norgen eluate in 2 mL tubes.
3. RNA cleanup and concentration using individual Zymo columns.

Current tube pilot scripts:

| Stage | Section | Script | Purpose |
|---|---|---|---|
| RNA extraction | Step 1 | `1_add_slurry_lysis_tube.py` | Add slurry and lysis buffer to 15 mL conical sample tubes |
| RNA extraction | Step 2 | manual | Add samples, mix, incubate |
| RNA extraction | Step 3 | `3_etoh_centrifuge_tube.py` | Add EtOH, vortex, pellet, decant, re-lysis, EtOH wash |
| RNA extraction | Step 4 | `4_transfer_to_norgen_column_tube.py` | Transfer sample slurry to Norgen columns |
| RNA extraction | Step 5 | `5_norgen_wash_tube.py` | Wash Norgen columns and dry spin |
| RNA extraction | Step 5b | `5b_norgen_elute_tube.py` | Elute Norgen columns into 2 mL tubes |
| DNA digestion | Step 5c | `5c_dnase_digestion_tube.py` | Add DNase master mix |
| Cleanup | Step 6 | `6_zymo_clean_conc_tube.py` | Zymo binding, washes and final elution |

## Hardware Configuration

The scripts assume:

- `p300_single_gen2` on the left mount
- `p20_single_gen2` on the right mount
- one shared `opentrons_24_aluminumblock_nest_2ml_snapcap` at slot 4 for Norgen/Zymo columns, eluates and small reagents
- custom 8-position 4-way 15 mL rack at slot 2

Upload this custom labware JSON in the Opentrons App before uploading the scripts:

`labware/custom_4way_8x15ml_tuberack.json`

The scripts load it by load name:

```python
SAMPLE_TUBE_RACK = "custom_4way_8x15ml_tuberack"
```

The JSON is provisional. After measuring the physical rack, edit `x`, `y`,
`diameter`, `depth`, and `dimensions` in the JSON, then re-upload it in the App.
Use normal Opentrons labware offset calibration for whole-rack deck placement
after the geometry is correct. The shared 24-block remains the canonical
`opentrons_24_aluminumblock_nest_2ml_snapcap`.

Because the 4-way rack can overhang the slot 2 footprint, slots 1 and 3 are left
empty by default. Reservoir steps use slot 5.

### Physical Placement Guide

Use slot 2 as the reference footprint: `127.76 mm x 85.48 mm`. Center the 4-way
rack on slot 2 before labware offset calibration.

For a rack body dimension of `rack_x` by `rack_y`:

```text
left/right overhang = (rack_x - 127.76) / 2
front/back gap      = (85.48 - rack_y) / 2
```

If using the common Heathrow/Stellar 4-way rack body (`174 mm x 95 mm`), the
fully centered placement is about `23.1 mm` overhang on both left and right.
That rack body is wider than the slot in both axes, so it would also overhang
about `4.8 mm` front and back. If your measured `rack_y` is shorter than the
slot instead, use the same formula and leave equal front/back gaps.

The current 8-well JSON keeps only the in-slot usable 15 mL positions:
`A1,B1,A2,B2,A3,B3,A4,B4`.

Sample and waste 15 mL tube positions are explicit so the commercial and custom
racks use the same identity order. Defaults:

```bash
SAMPLE_TUBES=A1,B1,A2,B2
TRASH_TUBES=A3,B3,A4,B4
```

Step 3 uses these `TRASH_TUBES` positions in the same slot 2 rack, so no second
15 mL waste rack is required by default.

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
| C5 | Slurry in Step 1, then Norgen elution buffer in Step 5b |

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

All sensitive heights are centralized in `config.py` and can be overridden per run with environment variables. Before real samples, run water or dyed-water checks for:

| Operation | Current config constant |
|---|---|
| 15 mL conical tube aspiration | `SAMPLE_ASPIRATE_H` |
| 15 mL conical tube staged decant | `DECANT_HEIGHTS` |
| 15 mL conical tube mixing | `SAMPLE_MIX_LOW_H`, `SAMPLE_MIX_HIGH_H` |
| 2 mL reagent tube aspiration | `REAGENT_TUBE_ASPIRATE_H`, default `bottom(1.0)` |
| slurry tube aspiration | `SLURRY_TUBE_ASPIRATE_H`, default `bottom(2)` |
| DNase dispense / blowout | `DNASE_DISPENSE_H`, `DNASE_BLOWOUT_H`, defaults `bottom(5)` and `bottom(8)` |
| Norgen column load/wash dispense | `NORGEN_COLUMN_DISPENSE_FROM_TOP`, default `top(5)` |
| Norgen elution placement | `NORGEN_ELUTE_FROM_BOTTOM`, default `bottom(5)` |
| Zymo column load/wash dispense | `ZYMO_COLUMN_DISPENSE_FROM_TOP`, default `top(5)` |
| Zymo final elution placement | `ZYMO_ELUTE_FROM_BOTTOM`, default `bottom(5)` |

Prior OT2 small-sample scripts used the 24-block as reagent source at `bottom(1.5)` for most LoBind reagents and `bottom(2)` for slurry. This tube pilot defaults reagent aspiration to `bottom(1.0)` after clearance checks showed enough room, while keeping slurry at `bottom(2)`. Norgen and Zymo column heights are separated because column/no-column, Norgen/Zymo geometry, and 1.5 mL/2 mL receiver height can differ.

Example height override:

```bash
N_SAMPLES=4 \
NORGEN_COLUMN_DISPENSE_FROM_TOP=10 \
NORGEN_ELUTE_FROM_BOTTOM=6 \
REAGENT_TUBE_ASPIRATE_H=1.0 \
opentrons_execute 5b_norgen_elute_tube.py
```

Critical step: `bottom(0)` is not guaranteed physical clearance. Validate low positions after installing or changing labware definitions, tip types, or deck offsets.

## Run Settings

Recommended pilot commands:

```bash
N_SAMPLES=4 TIP_START=0 opentrons_execute 1_add_slurry_lysis_tube.py
N_SAMPLES=4 TIP_START=2 opentrons_execute 3_etoh_centrifuge_tube.py
N_SAMPLES=4 TIP_START=13 opentrons_execute 4_transfer_to_norgen_column_tube.py
N_SAMPLES=4 TIP_START=17 opentrons_execute 5_norgen_wash_tube.py
N_SAMPLES=4 TIP_START=20 opentrons_execute 5b_norgen_elute_tube.py
N_SAMPLES=4 P20_TIP_START=0 opentrons_execute 5c_dnase_digestion_tube.py
N_SAMPLES=4 TIP_START=21 P20_TIP_START=1 opentrons_execute 6_zymo_clean_conc_tube.py
```

Tip starts assume one continuous p300 tip sequence across extraction and a p20 tip sequence for DNase/final elution. Reset `TIP_START` or `P20_TIP_START` if you replace racks.

## Rack Position / Water Test

Before running samples, upload `labware/custom_4way_8x15ml_tuberack.json`, then
upload and run `test_4way_15ml_positions_water.py`.

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `custom_4way_8x15ml_tuberack` | empty 15 mL tubes in A1/B1/A2/B2/A3/B3/A4/B4 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

The test is now a no-liquid safety check. It moves the p300 over all eight tube
positions at `top(10.0)` only, pauses, then repeats the hover path in reverse.
It does not aspirate, dispense, or enter the tubes.

## Procedure

### Step 1 (`1_add_slurry_lysis_tube.py`): Slurry and lysis buffer addition

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `custom_4way_8x15ml_tuberack` | 15 mL conical sample tubes |
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | slurry in C5 |
| 5 | `nest_1_reservoir_195ml` | lysis buffer + 1.2% B-ME |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place four 15 mL conical sample tubes in the sample rack.
2. Vortex preheated slurry thoroughly.
3. Add the prompted slurry volume to shared-rack tube C5.
4. Run `1_add_slurry_lysis_tube.py`.
5. The robot adds 200 uL slurry to each 15 mL conical sample tube.
6. When prompted, add preheated lysis buffer + 1.2% B-ME to the slot 5 reservoir.
7. Resume. The robot adds 1800 uL lysis buffer to each sample tube.

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
5. Resume. The robot decants supernatant by staged heights.
6. Add prompted preheated re-lysis buffer to tube B4 and resume.
7. Cap tubes, vortex at least 30 sec, incubate at 60 C for 10 min.
8. Replace B4 contents with prompted 200-proof EtOH wash and resume.

Pause point: cap and vortex tubes to resuspend slurry/EtOH mixture, briefly spin or tap down, then continue immediately to Step 4.

### Step 4 (`4_transfer_to_norgen_column_tube.py`): Transfer to Norgen columns

Deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `custom_4way_8x15ml_tuberack` | freshly vortexed sample tubes |
| 4 | `opentrons_24_aluminumblock_nest_2ml_snapcap` | Norgen columns with collection tubes in A1-D1 |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place freshly vortexed sample tubes at slot 2.
2. Place Norgen columns with collection tubes in slot 4 positions A1-D1.
3. For each sample prompt, vortex that tube, briefly spin or tap down, uncap only that tube, and resume.
4. The robot mixes and transfers sample slurry to the matching Norgen column.
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

1. Place dry-spun Norgen columns on clean 2 mL elution tubes in A1-D1.
2. Keep final eluate identity mapped to A1-D1.
3. Add prompted Norgen elution buffer to C5.
4. Resume. The robot adds 100 uL elution buffer to each column.
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
| 5 | `nest_1_reservoir_195ml` | Zymo wash buffer 1 |
| 7 | `opentrons_96_tiprack_20ul` | p20 tips |
| 8, 9 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place DNase-treated samples in A1-D1.
2. Add prompted Zymo binding buffer to B4. Resume.
3. Add prompted 100% EtOH to C4. Resume.
4. Cap and vortex sample tubes at least 30 sec.
5. Place Zymo columns with collection tubes in slot 4 positions A2-D2. Resume.
6. The robot loads each sample onto the matching Zymo column.
7. Centrifuge 5 min at 3,000-5,000 g, RT. Discard flow-through.
8. Add prompted RNA prep buffer to D4. Resume, then centrifuge and discard flow-through.
9. Add prompted Zymo wash buffer 1 to reservoir slot 5. Resume, then centrifuge and replace collection tubes.
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
