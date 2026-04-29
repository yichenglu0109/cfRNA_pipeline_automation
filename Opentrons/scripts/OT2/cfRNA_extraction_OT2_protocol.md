# Semi-Automated cfRNA Extraction on OT-2

Author: Peter Lu  
Date: 2026-04-25

The operating protocol for the OT-2 scripts in this directory. It is intended to be used by an operator standing at the robot. The OT-2 performs repetitive liquid handling; the user adds reagents, moves plates, centrifuges plates, seals/unseals plates, vortexes samples and verifies setup at each pause.

## Overview

The cfRNA workflow is divided into three stages:

1. RNA extraction from 48-well deep-well plates.
2. DNase digestion of the Norgen eluate.
3. RNA cleanup and concentration using a Zymo filter plate.

For a 96-sample experiment, process two 48-sample batches through Norgen
extraction. The first 48-sample eluate can be sealed and refrigerated while the
second 48-sample batch is processed. After both batches are eluted into the
96-well plate, proceed with DNase digestion and Zymo cleanup.

Current production scripts and timing:

| Stage | Section | Current script or operation | Purpose | Current total time | If refactored to p300 multichannel |
|---|---|---|---|---|---|
| RNA extraction | Step 1 | `1_add_slurry_lysis.py` | Add slurry and lysis buffer | about 35 min | about 25-40 min |
| RNA extraction | Step 2 | manual | Add sample, mix, incubate | 15-25 min | unchanged |
| RNA extraction | Step 3 | `3_etoh_centrifuge.py` | Add EtOH, vortex, pellet, decant, re-lysis, EtOH wash | about 8 h | about 1-1.5 h if multi-channel decant is validated |
| RNA extraction | Step 4 | `4_transfer_to_filter.py` | Transfer sample to Norgen filter plate | about 1 h | about 15-25 min |
| RNA extraction | Step 5/5b | `5_norgen_wash.py` + `5b_norgen_elute.py` | Wash Norgen filter, then swap to 2 mL deep-well receiver and elute cfRNA | about 1.5 h | about 30-45 min |
| DNA digestion | Step 5c | `5c_dnase_digestion.py` or manual P20 | Add DNase master mix and incubate | about 1 h | p300 multichannel not applicable; use p20/manual P20 multichannel |
| Cleanup | Step 6 | `6_zymo_clean_conc.py` | Zymo bind, wash and elute | about 1 h | about 1-1.5 h; final elution still p20/manual |
| Summary | RNA extraction, one 48-sample batch | Steps 1-5 | Norgen extraction through first elution | about 11-11.5 h | about 2.5-4 h |
| Summary | RNA extraction, two 48-sample batches | Steps 1-5 twice | Two 48-well batches into one 96-well layout | about 22-23 h | about 5-8 h |
| Summary | Full 96-sample OT-2 run | Steps 1-6 | Extraction, DNase and Zymo cleanup | about 24-25 h | about 6.5-10 h |


## Timing

The table above summarizes the current timing recorded in the scripts and the
expected total time for each operating section. The p300 multichannel column is
a rewrite estimate and has not been validated on the current scripts. Sample
and reagent preparation is not included and typically adds 10-20 min.

The current scripts are not yet optimized for the available `p1000_single +
p300_multi` hardware. Robot time can be reduced substantially by refactoring
high-volume operations to p1000 single and column operations to p300 multi.
The Nature Protocols timing of about 4.5 h for 96 samples should be treated as
an optimized semi-automated target, not as the expected runtime of the current
single-channel OT-2 scripts.

## Experimental Design

The current scripts assume 48-well extraction followed by 96-well filter plate
cleanup. A full 96-sample run is handled as two 48-sample batches:

- Batch 1 fills Norgen/Zymo/filter columns 1-6 (`FILTER_COL_START=0`).
- Batch 2 fills columns 7-12 (`FILTER_COL_START=6`).

For multi-channel use, samples must be arranged in complete columns of eight
wells. If fewer than eight samples are present in the final column, either add
blank wells, handle the partial column manually, or use a single-channel
script.

## Hardware Configuration

### Current script assumptions

Most current scripts use:

- `p300_single_gen2` on the left mount
- `p20_single_gen2` on the right mount for DNase and final 12.5 uL elution

### Available hardware configuration

If the robot only has:

- `p1000_single_gen2`
- `p300_multi_gen2`

then the current scripts should be refactored before production. Recommended
division of labor:

- p1000 single: 1.8 mL lysis, 3 mL EtOH, high-volume 48-well additions and conservative decant/removal.
- p300 multi: full-column additions and transfers in 48-well, Norgen and Zymo filter plates.
- Manual P20 multichannel: DNase 13 uL/well and final 12.5 uL/well nuclease-free water addition.

**Critical step:** do not run a script with a pipette configuration that does not
match the script. The robot will not automatically translate p300-single logic
to p300-multi or p1000-single logic.

## Required Labware

Custom labware must be installed on the OT-2:

- `custom_48_wellplate_7000ul`
- `custom_norgen_96filterplate`
- `custom_zymo_96filterplate` with the current 60 mm stack height definition

Standard labware used by scripts:

- `nest_1_reservoir_195ml`
- `thermoscientificnunc_96_wellplate_2000ul`
- `opentrons_96_tiprack_300ul`
- `opentrons_96_tiprack_20ul`, only for p20 scripts

## Reagent Setup

Prepare reagents according to the extraction kit instructions and sample input
volume. The current scripts use the following defaults:

| Reagent | Current amount used in script |
|---|---|
| Slurry | **200 uL/well** |
| Lysis buffer | **1800 uL/well** |
| EtOH for extraction | **3000 uL/well** |
| Re-lysis buffer | **300 uL/well** |
| EtOH wash after re-lysis | **300 uL/well** |
| Norgen wash buffer | **400 uL/well/wash, 3 washes** |
| Norgen elution buffer | **100 uL/well** in current script |
| DNase master mix | **13 uL/well** |
| Zymo binding buffer | **226 uL/well** |
| Zymo EtOH | **339 uL/well** |
| RNA prep buffer | **400 uL/well** |
| Zymo wash 1 | **700 uL/well** |
| Zymo wash 2 | **400 uL/well** |
| Final nuclease-free water | **12.5 uL/well** |

**Critical step:** pre-warmed slurry and lysis buffer can crystallize or clog tips
if cooled. Work promptly after vortexing and loading these reagents.

## Robot and Labware Calibration

Before processing clinical or precious samples:

1. Confirm pipette offset and tip length calibration.
2. Confirm deck calibration.
3. Confirm custom labware offsets in the exact slots used by these scripts.
4. Run a dry positioning check for every custom labware and low aspiration height.
5. Run a water or mock-liquid test for transfer recovery and decant behavior.

**Critical step:** `well.bottom(0)` is the mathematical bottom from the labware
definition. It is not a guaranteed physical clearance. Calibration error, tip
length variation and plastic tolerance can make `bottom(0)` hit the labware.

Validate these low/sensitive positions before production:

| Step | Operation | Position |
|---|---|---|
| Step 1 | slurry aspiration | reservoir **`bottom(2)`** |
| Step 3 | decant | 48-well staged heights down to **`bottom(3)`** |
| Step 4 | sample transfer | 48-well **`bottom(1.7)`** |
| Step 6 | Zymo transfer source | Thermo Scientific Nunc 2 mL plate **`bottom(0)`** |

## Procedure

### RNA Extraction

**Timing:** about 11-11.5 h per 48-sample batch with the current scripts. Step 3
is the major bottleneck.
**Estimated p300 multichannel version:** about 2.5-4 h per 48-sample batch,
assuming full columns and validated 48-well/filter plate alignment.

#### Step 1 (`1_add_slurry_lysis.py`): Slurry and lysis buffer addition

Script: `1_add_slurry_lysis.py`

**Timing:** about 35 min for 48 samples with the current p300 single-channel
script.
**Estimated p300 multichannel version:** about 25-40 min for 48 samples, assuming
full columns and validated slurry/lysis handling.

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 1 | `nest_1_reservoir_195ml` | lysis buffer A + 1.2% B-ME |
| 2 | `custom_48_wellplate_7000ul` | 48-well plate for lysis step |
| 4 | `nest_1_reservoir_195ml` | slurry, about 10.5 mL |
| 5 | `custom_48_wellplate_7000ul` | 48-well plate for slurry step |
| 9 | `opentrons_96_tiprack_300ul` | p300 tips |

1. Place the 48-well plate at slot 5.
2. Vortex preheated slurry thoroughly.
3. Add about **10.5 mL slurry** to the reservoir at slot 4.
4. Start or resume `1_add_slurry_lysis.py`.
5. The robot adds **200 uL slurry** to each target well. The current script aspirates slurry from **`bottom(2)`** at slow rate and dispenses near the top of each 48-well.
6. When prompted, move the 48-well plate to slot 2.
7. Add about **40 mL preheated lysis buffer plus 1.2% B-ME** to the slot 1 reservoir. Refill in about **40 mL** batches if needed.
8. Resume the robot.
9. The robot adds **1800 uL lysis buffer per well**, split into serial p300 dispenses.

**Pause point:** after lysis buffer addition, proceed manually to sample addition.

#### Step 2 (manual): Sample addition and incubation

No OT-2 script.

**Timing:** 15-25 min.

10. Add samples manually to the lysis/slurry plate.
11. Mix each column **at least 5 times** with a P1000 multichannel.
12. Seal the plate.
13. Incubate at **60 C for 10 min**.
14. Return the plate to the robot area for Step 3.

**Critical step:** keep the plate sealed except during active pipetting. Move
quickly after vortexing or mixing so slurry does not settle.

#### Step 3 (`3_etoh_centrifuge.py`): EtOH addition, pellet, decant, re-lysis and EtOH wash

Script: `3_etoh_centrifuge.py`

**Timing:** about 8 h for 48 samples with the current p300 single-channel script.
**Estimated p300 multichannel version:** about 1-1.5 h if EtOH addition, re-lysis,
EtOH wash and decant are all converted to column-wise operations and
multi-channel decant is validated with mock slurry.

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 1 | `nest_1_reservoir_195ml` | 200-proof EtOH, about 150 mL |
| 2 | `custom_48_wellplate_7000ul` | 48-well sample plate |
| 3 | `nest_1_reservoir_195ml` | re-lysis buffer, later EtOH wash |
| 5 | `custom_48_wellplate_7000ul` | open liquid waste container |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |
| 9 | `opentrons_96_tiprack_300ul` | p300 tips |

15. Place the sealed 48-well sample plate at slot 2.
16. Add about **150 mL 200-proof EtOH** to the slot 1 reservoir.
17. Load p300 tip racks at slots 8 and 9.
18. Remove the plate seal.
19. Resume the robot.
20. The current script adds **3000 uL EtOH per well** with p300, split into **12 transfers of 250 uL**.
21. When prompted, **seal the plate and vortex at least 30 s** to mix EtOH with sample. Briefly spin or tap down if liquid remains on the seal or well walls.

**Optimization note:** with `p1000_single_gen2`, the 3000 uL EtOH addition should
be refactored to about 3-4 transfers per well. This is one of the largest speed
gains available.

22. Centrifuge **30 sec at 1,000g** at room temperature to pellet slurry.
23. Return the plate to slot 2 unsealed.
24. Place an open liquid-waste container at slot 5.
25. Resume the robot.
26. The robot decants supernatant from each target well using staged heights: **37, 34, 30, 26, 22, 18, 14, 10, 8, 6, 4 and 3 mm above bottom**. Each height is used for **two 250 uL aspirations at rate 0.5**.

**Critical step:** decant is pellet-sensitive. If using a modified p1000 or
multi-channel decant, validate with mock slurry first. Do not optimize this step
purely for speed.

27. Remove the liquid-waste container from slot 5.
28. Add **20 mL preheated lysis buffer** to the slot 3 reservoir.
29. Resume the robot. The robot adds **300 uL re-lysis buffer per well**.
30. **Seal the plate and vortex at least 30 s**.
31. Incubate at **60 C for 10 min**.
32. If this is the first 48-sample batch, keep the incubator at **60 C**. If this is the second 48-sample batch, set the incubator to **37 C** for DNase.
33. Empty the slot 3 reservoir and add **20 mL 200-proof EtOH**.
34. Remove the seal from the plate and return it to slot 2.
35. Resume the robot. The robot adds **300 uL EtOH wash per well**.
36. **Seal the plate and vortex 1 min**.

**Pause point:** proceed immediately to Norgen transfer, or keep the plate sealed
briefly while preparing Step 4.

#### Step 4 (`4_transfer_to_filter.py`): Transfer to Norgen filter plate

Script: `4_transfer_to_filter.py`

**Timing:** about 1 h for 48 samples with the current p300 single-channel script.
**Estimated p300 multichannel version:** about 15-25 min for 48 samples, assuming
full columns and validated 48-well to Norgen filter alignment.

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `custom_48_wellplate_7000ul` | vortexed 48-well sample plate |
| 5 | `custom_norgen_96filterplate` | Norgen filter plate on collection plate |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |

37. Place the vortexed 48-well plate at slot 2.
38. Place the Norgen filter plate on its collection plate at slot 5. Confirm A1 is top-left in the expected orientation.
39. Set `FILTER_COL_START=0` for batch 1 or `FILTER_COL_START=6` for batch 2.
40. Start or resume `4_transfer_to_filter.py`.
41. At each source-column prompt, **vortex the 48-well plate briefly**, focusing on the active column.
42. **Remove the seal only from the active source column**.
43. Resume the robot.
44. For each well, the current script mixes **3 x 250 uL at `bottom(2)`**, then transfers **3 x 230 uL = 690 uL** from source **`bottom(1.7)`** into Norgen filter **`top(-5)`** with a **10 uL air gap** each time.
45. Repeat the prompt/resume process until all target wells are transferred.
46. Centrifuge the Norgen filter plate with collection plate underneath for **2 min at maximum speed or 2,000 RPM** at room temperature.

**Critical step:** the Norgen filter plate must sit squarely on its collection
plate. Verify orientation before centrifugation and before returning to the
robot.

#### Step 5 (`5_norgen_wash.py`): Norgen filter wash on kit collection plate

Script: `5_norgen_wash.py`

**Timing:** about 1.5 h for 48 samples with the current p300 single-channel script.
**Estimated p300 multichannel version:** about 30-45 min for 48 samples.

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 1 | `nest_1_reservoir_195ml` | Norgen wash buffer |
| 2 | `custom_norgen_96filterplate` | Norgen filter plate on collection plate |
| 9 | `opentrons_96_tiprack_300ul` | p300 tips |

47. Place the centrifuged Norgen filter plate on its collection plate at slot 2.
48. Add **24 mL Norgen wash buffer** to the slot 1 reservoir.
49. Resume Wash 1. The robot adds **400 uL wash buffer per well**.
50. Centrifuge **2 min at maximum speed or 2,000 RPM** at room temperature.
51. Discard flow-through.
52. Repeat Steps 48-52 for Wash 2.
53. Repeat the wash addition once more for Wash 3.
54. After Wash 3, centrifuge **5 min at 2,000 RPM** at room temperature for dry spin.
55. Discard flow-through.
56. Discard flow-through.

#### Step 5b (`5b_norgen_elute.py`): Norgen elution into 2 mL deep-well plate

Script: `5b_norgen_elute.py`

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `custom_norgen_96filterplate_on_2ml_deep` | Norgen filter plate on clean 2 mL deep-well elution plate |
| 4 | `nest_1_reservoir_195ml` | Norgen elution buffer |
| 9 | `opentrons_96_tiprack_300ul` | p300 tips |

57. **Replace the kit collection plate with a clean NEST 96-well 2 mL deep-well elution plate. Align A1 over A1.**
58. Add **10 mL elution buffer** to the single-channel reservoir at slot 4.
59. Place filter plus 2 mL deep-well elution plate at slot 2.
60. Resume `5b_norgen_elute.py`. The robot adds **100 uL elution buffer per well**.
61. Centrifuge filter plus elution plate for **2 min at maximum speed or 2,000 RPM** at room temperature.
62. Confirm approximately **100 uL eluate** in each expected elution well.

**Pause point:** if processing a 96-sample run and this is batch 1, seal the
elution plate and refrigerate it while processing batch 2. Continue with the
second 48-sample batch from Step 1, using `FILTER_COL_START=6` for Step 4 and
Step 5.

### DNA Digestion

#### Step 5c (`5c_dnase_digestion.py` or manual P20): DNase addition and incubation

Script: `5c_dnase_digestion.py`, or manual P20 multichannel if no p20 is
mounted.

**Timing:** about 1 h with the current p20 single-channel script.
**Estimated p300 multichannel version:** not applicable; DNase addition is 13 uL
per well and should remain p20 single, p20 multichannel or manual P20
multichannel.

Current deck layout for robot p20 mode:

| Slot | Labware | Contents |
|---|---|---|
| 2 | `thermoscientificnunc_96_wellplate_2000ul` | Norgen elution plate |
| 4 | `nest_1_reservoir_195ml` | DNase master mix |
| 6 | `opentrons_96_tiprack_20ul` | p20 tips |

62. Prepare DNase master mix on ice. Each sample requires **11 uL 10x DNase buffer and 2 uL DNase**. Include **10% excess**.
63. If using robot p20 mode, add master mix to the single-channel reservoir at slot 4.
64. Place the Norgen elution plate at slot 2.
65. Resume `5c_dnase_digestion.py`. The robot adds **13 uL master mix per well** and performs a high blowout in the same well to clear droplets.
66. If using manual mode, add **13 uL DNase master mix** to each sample well with a P20 multichannel pipette.
67. **Seal the plate and vortex lightly**.
68. Incubate **20 min at 37 C**.

**Pause point:** during the DNase incubation, prepare Zymo filter plate, collection
plate, binding buffer, EtOH, RNA prep buffer, wash buffer and nuclease-free
water for Step 6.

### RNA Cleaning and Concentration

**Timing:** about 1 h for 48 samples with the current p300/p20 single-channel
script.
**Estimated p300 multichannel version:** about 1-1.5 h for 48 samples, assuming
binding, EtOH, Zymo loading, prep buffer and wash additions are converted to
column-wise operations. Final 12.5 uL elution still requires p20 or manual P20
multichannel.

#### Step 6 (`6_zymo_clean_conc.py`): Zymo cleanup

Script: `6_zymo_clean_conc.py`

Current deck layout:

| Slot | Labware | Contents |
|---|---|---|
| 1 | `nest_1_reservoir_195ml` | replace between RNA prep buffer, wash buffer and nuclease-free water |
| 2 | `custom_zymo_96filterplate` | Zymo filter plate on collection/elution plate |
| 3 | `thermoscientificnunc_96_wellplate_2000ul` | post-DNase sample plate |
| 4 | `nest_1_reservoir_195ml` | replace between binding buffer and EtOH |
| 6 | `opentrons_96_tiprack_20ul` | p20 tips |
| 8 | `opentrons_96_tiprack_300ul` | p300 tips |
| 9 | `opentrons_96_tiprack_300ul` | p300 tips |

69. Place the post-DNase sample plate at slot 3.
70. Place a 195 mL single-channel reservoir containing the **binding buffer volume prompted by `6_zymo_clean_conc.py`** at slot 4. For one 8-well column, this is about **2.2 mL including excess**.
71. Load p300 tip racks at slots 8 and 9.
72. Press Resume in the Opentrons App. The robot adds **226 uL binding buffer per well** and performs a high blowout in each well.
73. Replace the slot 4 reservoir with a 195 mL single-channel reservoir containing the **100% EtOH volume prompted by `6_zymo_clean_conc.py`**. For one 8-well column, this is about **3.3 mL including excess**.
74. Press Resume in the Opentrons App. The robot adds **339 uL EtOH per well** and performs a high blowout in each well.
75. Remove the sample plate from slot 3.
76. **Seal and vortex at least 30 s**.
77. Return sample plate to slot 3.
78. Place Zymo filter plate on collection plate at slot 2.
79. Press Resume in the Opentrons App. The current script transfers **3 x 226 uL per well** from the Thermo Scientific Nunc 2 mL sample plate to the Zymo filter plate, dispensing to the Zymo filter at **`top(-5)`** with high blowout.

**Critical step:** the current Step 6 transfer aspirates from `bottom(0)`. Validate
this height physically before production. If the tip touches the bottom or flow
is restricted, raise the final aspiration height and accept a small residual
volume.

80. Centrifuge the Zymo filter plate for **5 min at 3,000-5,000g** at room temperature.
81. Discard flow-through and reassemble the filter plate with the collection plate.
82. Place a 195 mL single-channel reservoir containing the **RNA prep buffer volume prompted by `6_zymo_clean_conc.py`** at slot 1. For one 8-well column, this is about **3.8 mL including excess**.
83. Place the filter plate at slot 2 and press Resume in the Opentrons App. The robot adds **400 uL RNA prep buffer per well** and performs a high blowout in each well.
84. Centrifuge **5 min at 3,000-5,000g**.
85. Discard flow-through and reassemble the plate.
86. Replace the slot 1 reservoir with a 195 mL single-channel reservoir containing the **wash buffer volume prompted by `6_zymo_clean_conc.py`**. For one 8-well column, this is about **6.7 mL including excess**.
87. Press Resume in the Opentrons App. The robot adds **700 uL wash buffer per well** and performs a high blowout in each well.
88. Centrifuge **5 min at 3,000-5,000g**.
89. Discard flow-through and replace the collection plate with a new one.
90. Replace the slot 1 reservoir with a 195 mL single-channel reservoir containing the **wash buffer volume prompted by `6_zymo_clean_conc.py`**. For one 8-well column, this is about **3.8 mL including excess**.
91. Press Resume in the Opentrons App. The robot adds **400 uL wash buffer per well** and performs a high blowout in each well.
92. Centrifuge **5 min at 3,000-5,000g**.
93. Discard flow-through and dispose of the collection plate.
94. **Place the Zymo filter plate on a new final elution plate. Align A1 over A1.**
95. Replace the slot 1 reservoir with a 195 mL single-channel reservoir containing **1 mL nuclease-free water**.
96. If using robot p20 mode, press Resume in the Opentrons App. The robot adds **12.5 uL water per well** and performs a high blowout in each well.
97. If using manual mode, add **12.5 uL nuclease-free water** to each sample well with a P20 multichannel pipette. Wet the filter membrane and avoid splashing the side walls.
98. Centrifuge filter plus elution plate for **5 min at 3,000-5,000g**.
99. Confirm approximately **12 uL eluate per well**.
100. Aliquot eluted cfRNA as needed and freeze at **-80 C**.

## Post-Run Quality Control

**RNA quality check:** after cfRNA extraction from plasma samples, estimate isolated RNA concentrations using the Bioanalyzer RNA 6000 Pico Kit (5067-1513, Agilent) according to the manufacturer's instructions.

Recommended checks:

1. Confirm expected eluate volumes after Norgen elution and final Zymo elution.
2. For production samples, select wells across rows and columns for RNA quality assessment.
3. For validation runs, include blank wells and spike-in controls to monitor cross-contamination and recovery.
4. Record any wells with visible filter failure, clogging, low eluate volume or pipetting abnormality.
