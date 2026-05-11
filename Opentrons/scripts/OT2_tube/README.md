# OT2 Tube-Based cfRNA Pilot

This folder contains a 4-sample tube-based pilot version of the OT-2 cfRNA workflow. It is independent from `Opentrons/scripts/OT2`.

## Hardware Assumptions

- Left mount: `p300_single_gen2`
- Right mount: `p20_single_gen2`
- One shared `opentrons_24_aluminumblock_nest_2ml_snapcap` for Norgen/Zymo columns, eluates and small reagents
- Custom 8-position 4-way 15 mL rack in slot 2

Upload this custom labware JSON in the Opentrons App before uploading the scripts:

`labware/custom_4way_8x15ml_tuberack.json`

The scripts load it by load name:

```python
SAMPLE_TUBE_RACK = "custom_4way_8x15ml_tuberack"
```

The JSON is provisional. After measuring the physical rack, edit `x`, `y`,
`diameter`, `depth`, and `dimensions` in the JSON, then re-upload it in the App.
The shared 24-block remains the canonical
`opentrons_24_aluminumblock_nest_2ml_snapcap`.

Because the 4-way rack can overhang the slot 2 footprint, slots 1 and 3 are left
empty by default. Reservoir steps use slot 5.

## Physical Placement Guide

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
| C5 | Slurry in Step 1, then Norgen elution buffer in Step 5b |

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

Upload `labware/custom_4way_8x15ml_tuberack.json`, then upload and run:

```bash
opentrons_execute test_4way_15ml_positions_water.py
```

The test protocol is now a no-liquid safety check. It moves the p300 over
A1/B1/A2/B2/A3/B3/A4/B4 at `top(10.0)` only, pauses, then repeats the hover
path in reverse. It does not aspirate, dispense, or enter the tubes.

## Calibration Notes

All tube and filter-column heights are centralized in `config.py` and can be overridden with environment variables. Before wet sample runs, validate the provisional heights with water or dyed water:

- 15 mL conical tube aspiration and decant heights
- Norgen column dispense/elution heights
- Zymo column dispense/elution heights
- final p20 15 uL elution placement

This tube pilot defaults to `bottom(1.0)` for most 24-block LoBind reagent sources. Prior OT2 scripts used `bottom(1.5)` for those reagent sources, `bottom(2)` for slurry, and `bottom(5)` / `bottom(8)` for p20 DNase dispense/blowout into 2 mL wells.

Common height overrides:

```bash
NORGEN_COLUMN_DISPENSE_FROM_TOP=10 \
ZYMO_COLUMN_DISPENSE_FROM_TOP=10 \
NORGEN_ELUTE_FROM_BOTTOM=5 \
ZYMO_ELUTE_FROM_BOTTOM=5 \
REAGENT_TUBE_ASPIRATE_H=1.0 \
opentrons_execute 5_norgen_wash_tube.py
```
