# Pilot Experiment: 15 mL Tube OT-2 cfRNA Extraction, 4 Samples

Author: Peter Lu  
Date: 2026-05-16

This pilot run uses the tube-based OT-2 workflow only. There is no matched manual arm in this run. The goal is to validate the 15 mL tube workflow, column handling, transfer heights, and final eluate recovery on four inputs:

1. Plasma sample 1
2. Plasma sample 2
3. Water negative extraction control
4. Positive control mouse tissue extract

## Objective

Evaluate whether the current tube-based OT-2 protocol can complete the full Norgen extraction, DNase digestion, and Zymo cleanup workflow without transfer failure, column placement failure, or obvious sample loss.

Primary questions:

1. Do all four 15 mL tube positions align reliably in the 3D-printed rack?
2. Does Step 3 decant remove supernatant while preserving pellet/slurry material?
3. Does Step 4 transfer the mixed slurry into Norgen columns without major residual liquid?
4. Do Norgen and Zymo column dispense/elution heights deliver liquid into the column opening?
5. Is the final Zymo eluate volume close to the expected 15 uL per sample?

## Sample Map

Preserve this order through all 15 mL tubes, Norgen columns, Norgen eluates, DNase digestion, Zymo columns, and final eluates.

| Sample index | 15 mL tube | Waste tube | Shared rack Norgen / eluate | Shared rack Zymo column | Sample type | Sample ID |
|---|---|---|---|---|---|---|
| 1 | A1 | C1 | A1 | A2 | Plasma | Plasma-1 |
| 2 | A2 | C2 | B1 | B2 | Plasma | Plasma-2 |
| 3 | A3 | C3 | C1 | C2 | Water negative control | Water-NTC |
| 4 | A4 | C4 | D1 | D2 | Positive control | Mouse-tissue-extract-PC |

Default environment mapping:

```bash
N_SAMPLES=4
SAMPLE_TUBES=A1,A2,A3,A4
TRASH_TUBES=C1,C2,C3,C4
```

## Required Setup

Use the operating protocol in `extraction_OT2_protocol_15mL_tube.md`.

Custom labware required:

- `labware/3dprinted_15_tuberack_15000ul.json`

Hardware:

- `p300_single_gen2` on left mount
- `p20_single_gen2` on right mount
- 3D-printed 15 mL tube rack in slot 2
- `opentrons_24_aluminumblock_nest_2ml_snapcap` in slot 4
- p20 tip rack in slot 7
- p300 tip rack in slot 8, with slot 9 available when needed

## Current Height Settings

These settings reflect the current tube scripts. Step 1, Step 3 and Step 4 currently have 2-sample standalone fallbacks for the active water-test path; Steps 5-6 remain set up for A1-D1 / A2-D2.

| Operation | Setting |
|---|---|
| Step 1 slurry/lysis dispense into 15 mL tubes | `SAMPLE_TOP_DISPENSE_OFFSET=5.0`, so blowout at `tube.top(5)` |
| Step 3 EtOH/re-lysis/wash dispense into 15 mL tubes | `SAMPLE_TOP_DISPENSE_OFFSET=-10.0`, so additions use `tube.top(-10)` |
| Step 3 decant waste dispense | `TRASH_DISPENSE_H=50.0` |
| Step 3 staged decant | `DECANT_HEIGHTS=45,41,37,33,29,25,21,17,13,11,8.5,6.5` |
| Step 4 15 mL sample aspirate for Norgen transfer | `SAMPLE_ASPIRATE_H=0.5` |
| Reagent tube aspiration | `REAGENT_TUBE_ASPIRATE_H=1.0` |
| DNase-treated eluate aspiration into Zymo | `ZYMO_INPUT_ASPIRATE_H=2.0` |
| DNase dispense / blowout | `DNASE_DISPENSE_H=5.0`, `DNASE_BLOWOUT_H=8.0` |
| Step 5/5b/6 shared 24-block safe travel after low tube/column moves | `SHARED_BLOCK_SAFE_TRAVEL_FROM_TOP=25.0` |
| Norgen column load/wash dispense / blowout | `NORGEN_COLUMN_DISPENSE_FROM_TOP=-3.0`, `NORGEN_COLUMN_BLOWOUT_FROM_TOP=0.0` |
| Norgen elution / blowout | `NORGEN_ELUTE_FROM_TOP=-12.0`, `NORGEN_ELUTE_BLOWOUT_FROM_TOP=-8.0` |
| Step 6 binding/EtOH dispense into DNase-treated eluate tubes | `SAMPLE_DISPENSE_H=30.0` |
| Zymo column load/wash dispense / blowout | `ZYMO_COLUMN_DISPENSE_FROM_TOP=0.0`, `ZYMO_COLUMN_BLOWOUT_FROM_TOP=0.0` |
| Zymo final elution / blowout | `ZYMO_ELUTE_FROM_TOP=-12.0`, `ZYMO_ELUTE_BLOWOUT_FROM_TOP=-8.0` |

## OT-2 Run Settings

Tip starts assume one continuous p300 tip sequence across extraction and one p20 sequence for DNase and final elution.

| Step | Script | N_SAMPLES | TIP_START | P20_TIP_START | Notes |
|---|---|---:|---:|---:|---|
| 1 | `1_add_slurry_lysis_tube.py` | 2 | 49 | N/A | Current active standalone fallback: A1,A2 |
| 3 | `3_etoh_centrifuge_tube.py` | 2 | 50 | N/A | Current active standalone fallback: A1,A2 to C1,C2 waste |
| 4 | `4_transfer_to_norgen_column_tube.py` | 2 | 54 | N/A | Current active standalone fallback: A1,A2 to A1,B1 Norgen columns |
| 5 | `5_norgen_wash_tube.py` | 4 | 32 | N/A | Norgen wash and dry spin |
| 5b | `5b_norgen_elute_tube.py` | 4 | 33 | N/A | Norgen elution |
| 5c | `5c_dnase_digestion_tube.py` | 4 | N/A | 0 | DNase addition |
| 6 | `6_zymo_clean_conc_tube.py` | 4 | 40 | 0 | Zymo cleanup and final elution |

Example commands:

```bash
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TRASH_TUBES=C1,C2 TIP_START=49 opentrons_execute 1_add_slurry_lysis_tube.py
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TRASH_TUBES=C1,C2 TIP_START=50 opentrons_execute 3_etoh_centrifuge_tube.py
N_SAMPLES=2 SAMPLE_TUBES=A1,A2 TIP_START=54 opentrons_execute 4_transfer_to_norgen_column_tube.py
N_SAMPLES=4 TIP_START=32 opentrons_execute 5_norgen_wash_tube.py
N_SAMPLES=4 TIP_START=33 opentrons_execute 5b_norgen_elute_tube.py
N_SAMPLES=4 P20_TIP_START=0 opentrons_execute 5c_dnase_digestion_tube.py
N_SAMPLES=4 TIP_START=40 P20_TIP_START=0 opentrons_execute 6_zymo_clean_conc_tube.py
```

Do not put spaces in comma-separated tube lists. Use `SAMPLE_TUBES=A1,A2`, not `SAMPLE_TUBES=A1, A2`.

## Workflow

1. Upload or confirm `3dprinted_15_tuberack_15000ul` in the Opentrons App.
2. Confirm deck calibration and labware offsets for the slot 2 rack and slot 4 aluminum block.
3. Run the 15 mL tube position check if the rack or deck offset changed.
4. Label 15 mL tubes A1-A4 and waste tubes C1-C4.
5. Add slurry and lysis buffer with Step 1.
6. Add the two plasma samples, water control, and positive control to A1-A4 in the sample map order.
7. Incubate at 60 C for 10 min.
8. Run Steps 3, 4, 5, 5b, 5c, and 6 using the commands above.
9. Keep eluates in A1-D1 order after Norgen and in final sample order after Zymo.

## Run Checklist

| Workflow step | Completed | Notes |
|---|---|---|
| Sample map and tube labels confirmed | [ ] |  |
| 3D-printed 15 mL rack JSON uploaded and offset calibrated | [ ] |  |
| Step 1 slurry and lysis added | [ ] |  |
| Samples and controls added in A1-A4 order | [ ] |  |
| 60 C incubation complete | [ ] |  |
| Step 3 EtOH addition, decant, re-lysis, and EtOH wash complete | [ ] |  |
| Step 4 Norgen transfer complete | [ ] |  |
| Step 5 Norgen washes and dry spin complete | [ ] |  |
| Step 5b Norgen elution complete | [ ] |  |
| Step 5c DNase digestion complete | [ ] |  |
| Step 6 Zymo cleanup and final elution complete | [ ] |  |
| Final eluate volume recorded | [ ] |  |

## Data to Record

| Field | Plasma-1 | Plasma-2 | Water-NTC | Mouse-tissue-extract-PC |
|---|---|---|---|---|
| Input volume |  |  |  |  |
| Step 3 pellet/slurry observation |  |  |  |  |
| Step 3 residual liquid after decant |  |  |  |  |
| Step 4 residual liquid after transfer |  |  |  |  |
| Norgen flow-through/clogging |  |  |  |  |
| Norgen eluate volume observed |  |  |  |  |
| Zymo flow-through/clogging |  |  |  |  |
| Final Zymo eluate volume |  |  |  |  |
| Bioanalyzer / downstream QC result |  |  |  |  |
| Operational notes |  |  |  |  |

## Acceptance Notes

This pilot is primarily a workflow and height validation run. Treat a successful run as one where all four samples complete the full workflow, liquid enters the intended tubes/columns at every dispense, and final eluate is recovered for all four samples.
