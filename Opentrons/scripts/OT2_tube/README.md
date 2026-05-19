# OT2 Tube-Based cfRNA Pilot

This folder contains a 4-sample tube-based pilot version of the OT-2 cfRNA workflow. It is independent from `Opentrons/scripts/OT2`.

## Protocol Documents

| Document | Purpose |
| --- | --- |
| `protocol.md` | Short index for this folder's protocol documents |
| `extraction_OT2_protocol_15mL_tube.md` | General 15 mL tube-based OT-2 operating protocol |
| `OT2_TUBE_PROTOCOL_PILOT_4_SAMPLES.md` | Current 4-sample OT-2-only pilot: two plasma samples, one water control and one positive-control mouse tissue extract |

## Hardware Assumptions

- Left mount: `p300_single_gen2`
- Right mount: `p20_single_gen2`
- One shared `opentrons_24_aluminumblock_nest_2ml_snapcap` for Norgen/Zymo columns, eluates and small reagents
- 3D-printed 15 mL tube rack in slot 2

Upload this custom labware JSON in the Opentrons App before uploading the scripts:

`labware/3dprinted_15_tuberack_15000ul.json`

The scripts load it by load name:

```python
SAMPLE_TUBE_RACK = "3dprinted_15_tuberack_15000ul"
```

The JSON is provisional. After measuring the physical rack, edit `x`, `y`,
`diameter`, `depth`, and `dimensions` in the JSON, then re-upload it in the App.
The shared 24-block remains the canonical
`opentrons_24_aluminumblock_nest_2ml_snapcap`.

The 3D-printed rack definition uses the standard slot 2 footprint
(`127.76 mm x 85.48 mm`), so slots 1 and 3 are available unless a physical
clearance check shows your printed rack overhangs. Reservoir steps use slot 5.

## Physical Placement Guide

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

Early positions are sample products:

| Position | Contents |
| --- | --- |
| A1-D1 | Norgen columns during Steps 4-5b, then Norgen eluates / Zymo input samples 1-4 |
| A2-D2 | Zymo columns during Step 6 |

Small reagent positions:

| Position | Contents |
| --- | --- |
| A4 | DNase master mix |
| B4 | Zymo binding buffer or re-lysis buffer during Step 3 |
| C4 | Zymo EtOH |
| D4 | Zymo prep buffer or Norgen wash buffer during Step 5 |
| A5 | Zymo wash buffer 2 |
| B5 | Nuclease-free water |
| C5 | Slurry in Step 1, then Norgen elution buffer in Step 5b, then Zymo wash buffer 1 tube 1 in Step 6 |
| D5 | Zymo wash buffer 1 tube 2 in Step 6 |

The scripts pause before any position is reused.

## Command Examples

```bash
N_SAMPLES=4 TIP_START=0 opentrons_execute 1_add_slurry_lysis_tube.py
N_SAMPLES=4 TIP_START=2 opentrons_execute 3_etoh_centrifuge_tube.py
N_SAMPLES=4 TIP_START=13 opentrons_execute 4_transfer_to_norgen_column_tube.py
N_SAMPLES=4 TIP_START=17 opentrons_execute 5_norgen_wash_tube.py
N_SAMPLES=4 TIP_START=20 opentrons_execute 5b_norgen_elute_tube.py
N_SAMPLES=4 P20_TIP_START=0 opentrons_execute 5c_dnase_digestion_tube.py
N_SAMPLES=4 TIP_START=21 P20_TIP_START=1 opentrons_execute 6_zymo_clean_conc_tube.py
```

## Rack Position / Water Test

Upload `labware/3dprinted_15_tuberack_15000ul.json`, then upload and run:

```bash
opentrons_execute test_3dprinted_15ml_positions_water.py
```

The test protocol is now a no-liquid safety check. It moves the p300 over
A1/A2/A3/A4/C1/C2/C3/C4 at `top(10.0)` only, pauses, then repeats the hover
path in reverse. It does not aspirate, dispense, or enter the tubes.

## Calibration Notes

All tube and filter-column heights are centralized in `config.py` and can be overridden with environment variables. Before wet sample runs, validate the provisional heights with water or dyed water:

- 15 mL conical tube aspiration and decant heights
- Norgen column dispense/elution heights
- Zymo column dispense/elution heights
- shared 24-block safe travel height for tall tubes/column stacks
- final p20 15 uL elution placement

This tube pilot defaults to `bottom(1.0)` for most 24-block LoBind reagent sources. Prior OT2 scripts used `bottom(1.5)` for those reagent sources, `bottom(2)` for slurry, and `bottom(5)` / `bottom(8)` for p20 DNase dispense/blowout into 2 mL wells.

Common height overrides:

```bash
NORGEN_COLUMN_DISPENSE_FROM_TOP=-3 \
ZYMO_COLUMN_DISPENSE_FROM_TOP=0 \
NORGEN_ELUTE_FROM_TOP=-12 \
ZYMO_ELUTE_FROM_TOP=-12 \
SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP=25 \
REAGENT_TUBE_ASPIRATE_H=1.0 \
opentrons_execute 6_zymo_clean_conc_tube.py
```
