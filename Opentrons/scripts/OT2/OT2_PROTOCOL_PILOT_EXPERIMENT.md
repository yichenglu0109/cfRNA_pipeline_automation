# Pilot Experiment: Manual vs Semi-Automated OT-2 cfRNA Extraction

Author: Peter Lu  
Date: 2026-05-02

This pilot experiment compares the current semi-automated OT-2 cfRNA extraction workflow against manual extraction using matched aliquots from the same source samples. To conserve kit plates, the pilot is designed as a same-plate performance comparison using the same Norgen and Zymo plate workflow. The goal is to evaluate extraction performance and reproducibility, not total protocol runtime.

## Objective

Evaluate whether the current OT-2 protocol produces cfRNA yield and quality comparable to manual extraction when starting from the same input material.

Primary questions:

1. Does the OT-2 workflow recover similar RNA concentration compared with manual extraction?
2. Is replicate variability similar between OT-2 and manual extraction?
3. Are there obvious OT-2-specific failures, such as low eluate volume, clogging, poor transfer or well-to-well inconsistency?

## Experimental Design

Use two source samples:

1. Fake cfRNA mimic sample from previous mouse tissue extraction.
2. Human blood/plasma sample purchased from a blood bank.

Each source sample is split into matched aliquots and assigned to manual or semi-automated extraction. Both the fake cfRNA mimic source and the human plasma source use two extraction sample wells per method. The remaining wells are filled with water negative controls so each method has a 1:1 sample-to-water layout. Sample and water wells are alternated by row to help assess contamination.

| Source sample | Manual extraction | OT-2 semi-automated extraction | Total |
|---|---:|---:|---:|
| Fake cfRNA mimic | 2 replicates + 2 water controls | 2 replicates + 2 water controls | 8 wells |
| Human blood/plasma | 2 replicates + 2 water controls | 2 replicates + 2 water controls | 8 wells |
| Total | 8 wells | 8 wells | 16 wells |

## Primary Endpoint

Analytical performance and reproducibility:

- RNA concentration after extraction.
- Bioanalyzer RNA profile.
- Replicate coefficient of variation within each method.
- OT-2/manual recovery ratio for each source sample.
- Visible or operational failures during extraction.

Runtime should be recorded only as a descriptive note because manual and OT-2 samples share plates, centrifugation and downstream processing.

## Sample Aliquoting

For the fake cfRNA mimic source sample:

1. Thaw or prepare the source sample consistently.
2. Mix thoroughly before aliquoting.
3. Prepare 4 equal-volume sample aliquots for extraction.
4. Randomly assign 2 aliquots to manual extraction and 2 aliquots to OT-2 extraction.
5. Prepare two water negative-control wells for each method.

For the human blood/plasma source sample:

1. Thaw or prepare the source sample consistently.
2. Mix thoroughly before aliquoting.
3. Prepare 4 equal-volume aliquots for extraction.
4. Randomly assign 2 aliquots to manual extraction and 2 aliquots to OT-2 extraction.
5. Prepare two water negative-control wells for each method to fill the remaining human plasma block wells.
6. Keep aliquots on the same temperature schedule before extraction.

Do not assign the first aliquots to one method and the last aliquots to the other method. Randomization reduces bias from mixing, settling or aliquot order.

Suggested labeling:

| Source | Manual replicates | OT-2 replicates |
|---|---|---|
| Fake cfRNA mimic | Mimic-M1, Mimic-M2, M-NTC1, M-NTC2 | Mimic-O1, Mimic-O2, O-NTC1, O-NTC2 |
| Human blood/plasma | Human-M1, Human-M2, M-NTC3, M-NTC4 | Human-O1, Human-O2, O-NTC3, O-NTC4 |

## Plate Strategy

Use one shared Norgen filter plate and one shared Zymo filter plate for this pilot. This conserves kit components and reduces reagent lot, centrifuge, incubation and downstream batch effects.

Recommended layout:

| Plate well | Sample ID | Method | Source |
|---|---|---|---|
| A1 | Mimic-O1 | OT-2 | Fake cfRNA mimic |
| B1 | O-NTC1 | OT-2 | Water negative control |
| C1 | Mimic-O2 | OT-2 | Fake cfRNA mimic |
| D1 | O-NTC2 | OT-2 | Water negative control |
| E1 | Human-O1 | OT-2 | Human blood/plasma |
| F1 | O-NTC3 | OT-2 | Water negative control |
| G1 | Human-O2 | OT-2 | Human blood/plasma |
| H1 | O-NTC4 | OT-2 | Water negative control |
| A3 | Mimic-M1 | Manual | Fake cfRNA mimic |
| B3 | M-NTC1 | Manual | Water negative control |
| C3 | Mimic-M2 | Manual | Fake cfRNA mimic |
| D3 | M-NTC2 | Manual | Water negative control |
| E3 | Human-M1 | Manual | Human blood/plasma |
| F3 | M-NTC3 | Manual | Water negative control |
| G3 | Human-M2 | Manual | Human blood/plasma |
| H3 | M-NTC4 | Manual | Water negative control |

Column 1 is reserved for the OT-2 workflow. Column 2 is intentionally left empty as a spacer column. Column 3 is reserved for the manual workflow. To compare manual versus OT-2 liquid handling while limiting manual influence on the OT-2 column, the OT-2 scripts process column 1 only; process column 3 manually through the matching Norgen wash/elution, DNase and Zymo cleanup steps.

Use only unused wells for each condition. Do not reuse wells that have already received sample, buffer, wash or elution liquid. The remaining unused wells on the same plates may be reserved for same-day optimization or additional pilot samples, but should not be used later for precious production samples.

Keep centrifugation and downstream QC batch timing matched whenever possible, but do not let the OT-2 add downstream reagents to the manual column if the goal is full manual versus OT-2 workflow comparison.

## Controls

1. Water negative controls for the fake cfRNA mimic source-method block: M-NTC1, M-NTC2, O-NTC1 and O-NTC2.
2. Water negative controls for the human plasma source-method block: M-NTC3, M-NTC4, O-NTC3 and O-NTC4.
3. Optional spike-in or positive control if available.
4. No-template control for downstream qPCR, if used.

Water negative controls should receive the same extraction reagents and plate handling as the corresponding sample wells. They are extraction/process controls, not just downstream PCR controls.

## OT-2 Pilot Run Settings

Use these environment variable settings for the OT-2 column of the pilot layout above. The values assume the OT-2 extraction wells occupy `A1-H1` of the 48-well plate and column 1 of the Norgen/Zymo workflow. Column 2 is unused as a spacer. The manual column (`A3-H3`) is processed manually.

| Step | Script | N_SAMPLES | WELL_START | FILTER_COL_START | TIP_START | P20_TIP_START | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | `1_add_slurry_lysis.py` | 8 | 0 | 0 | 0 | N/A | Start a fresh p300 tip box; uses 2 p300 tips |
| 3 | `3_etoh_centrifuge.py` | 8 | 0 | 0 | 2 | N/A | Continue p300 box after Step 1; uses 11 p300 tips |
| 4 | `4_transfer_to_filter.py` | 8 | 0 | 0 | 13 | N/A | Continue p300 box after Step 3; uses 8 p300 tips |
| 5 | `5_norgen_wash.py` | 8 | ignored | 0 | 21 | N/A | Continue p300 box after Step 4; uses 3 p300 tips |
| 5b | `5b_norgen_elute.py` | 8 | ignored | 0 | 24 | N/A | Continue p300 box after Step 5; uses 1 p300 tip |
| 5c | `5c_dnase_digestion.py` | 8 | ignored | 0 | 0 | N/A | Start a fresh p20 tip box; uses 1 p20 tip |
| 6 | `6_zymo_clean_conc.py` | 8 | ignored | 0 | 25 | 1 | Continue p300 box after Step 5b and p20 box after Step 5c |

Example commands:

```bash
N_SAMPLES=8 WELL_START=0 TIP_START=0 opentrons_execute 1_add_slurry_lysis.py
N_SAMPLES=8 WELL_START=0 TIP_START=2 opentrons_execute 3_etoh_centrifuge.py
N_SAMPLES=8 WELL_START=0 FILTER_COL_START=0 TIP_START=13 opentrons_execute 4_transfer_to_filter.py
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=21 opentrons_execute 5_norgen_wash.py
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=24 opentrons_execute 5b_norgen_elute.py
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=0 opentrons_execute 5c_dnase_digestion.py
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=25 P20_TIP_START=1 opentrons_execute 6_zymo_clean_conc.py
```

For `N_SAMPLES=8`, Step 5c will prompt for **114 µL DNase master mix** in LoBind tube A1 of a 24-well aluminum block at slot 4. Step 6 uses the prompted slot 4 dynamic reagent source for small-volume reagents; Wash 1 still uses the slot 1 reservoir.

Manual extraction wells should be loaded into Norgen column 3 and processed manually through the corresponding Norgen, DNase and Zymo steps. Keep column 2 empty as a spacer. Confirm the manual column preserves the same well order across all plates.

Use the same reagent lot, elution volume and downstream QC method for both extraction methods.

## Workflow

1. Prepare the OT-2 using `OT2_SETUP.md`.
2. Confirm labware offsets and run water/mock tests if calibration or labware has changed.
3. Prepare matched aliquots from each source sample.
4. Randomize aliquots into manual and OT-2 groups.
5. Run manual and OT-2 extraction on unused wells of the same Norgen/Zymo plate workflow using the same reagent lot and same final elution volume.
6. Record any pipetting, clogging, aspiration, transfer, centrifugation or elution issues.
7. Run Bioanalyzer RNA 6000 Pico Kit for all final eluates in the same batch.
8. If available, run qPCR on all samples in the same downstream batch.

## Workflow Completion Checklist

Use this table during the run to track whether the manual column and OT-2 column have completed the same workflow stage. The step grouping follows the current script workflow without splitting every robot pause into a separate record.

| Workflow step | Manual completed | OT-2 completed | Notes |
|---|---|---|---|
| Plate map, labels, aliquots and water controls confirmed | [ ] | [ ] |  |
| Step 1/2: slurry, lysis, sample/water loading and 60 °C incubation (`1_add_slurry_lysis.py` for OT-2) | [ ] | [ ] |  |
| Step 3A-B: EtOH added, mixed, centrifuged and slurry pelleted (`3_etoh_centrifuge.py`) | [ ] | [ ] |  |
| Step 3C-E: supernatant removed, re-lysis buffer added and EtOH wash added (`3_etoh_centrifuge.py`) | [ ] | [ ] |  |
| Step 4: sample/slurry transferred to Norgen filter plate and centrifuged (`4_transfer_to_filter.py`) | [ ] | [ ] |  |
| Step 5: Norgen wash steps completed (`5_norgen_wash.py`) | [ ] | [ ] |  |
| Step 5b: Norgen elution into 2 mL elution plate completed (`5b_norgen_elute.py`) | [ ] | [ ] |  |
| Step 5c: DNase master mix added and incubation completed (`5c_dnase_digestion.py`) | [ ] | [ ] |  |
| Step 6A-C: binding/RNA prep buffer, EtOH and Zymo loading completed (`6_zymo_clean_conc.py`) | [ ] | [ ] |  |
| Step 6D-F: Zymo washes, dry spin and final elution completed (`6_zymo_clean_conc.py`) | [ ] | [ ] |  |
| Final eluate volume and operational notes recorded | [ ] | [ ] |  |

## Data to Record

For each replicate:

| Field | Notes |
|---|---|
| Sample ID | Mimic-M1, Mimic-O1, Human-M1, Human-O1, etc. |
| Source sample | Fake cfRNA mimic or human blood/plasma |
| Method | Manual or OT-2 |
| Input volume | Same across all replicates if possible |
| Elution volume | Same across all replicates |
| Final eluate volume observed | Record low-volume wells |
| RNA concentration | Bioanalyzer RNA 6000 Pico Kit |
| Bioanalyzer profile notes | Smear, peak pattern, degradation or abnormal trace |
| Operational notes | Clog, pellet disturbance, tip issue, low transfer, etc. |

## Notes on Runtime

Because manual and OT-2 samples are processed on the same plate workflow, elapsed runtime is not a fair endpoint. The two methods will wait for each other.

Record time descriptively:

- OT-2 robot active time.
- Manual active pipetting time.
- Total elapsed time.
- Waiting time caused by shared centrifuge, incubation or plate handling.

For this pilot, use runtime notes only to identify bottlenecks. A true runtime comparison would require independent manual and OT-2 workflows with separate timing and no forced waiting between methods.
