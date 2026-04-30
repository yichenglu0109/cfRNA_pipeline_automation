# Used Plate Water QC for OT-2 cfRNA Pilot

Author: Peter Lu  
Date: 2026-04-27

This is a low-cost process rehearsal using used Norgen/Zymo filter plates and water or dyed water. It checks plate alignment, well mapping, liquid handling, centrifuge handoffs, flow-through and tip-start logic before spending fresh kit wells or real samples.

Do not use used filter plates for real pilot samples. This QC only validates the physical workflow.

## Goal

Confirm that the current OT-2 pilot workflow can run through the expected 2-column layout without obvious mechanical or operator-handling failures.

Primary checks:

1. OT-2 dispenses into the intended wells.
2. Norgen and Zymo filter wells are centered after the custom labware offset changes.
3. Transfer, wash and elution liquids flow through the used filter plates.
4. Centrifuge and plate-swap pauses are understandable.
5. Tip usage follows the pilot tip-start map.

## Materials

| Item | Purpose |
|---|---|
| Used Norgen 96 filter plate + collection plate | Step 4/5 transfer and flow-through rehearsal |
| Used Zymo 96 filter plate + collection plate | Step 6 flow-through rehearsal |
| 48-well deep-well plate | Mock extraction plate |
| NEST 96-well 2 mL deep-well plate | Norgen elution / DNase / Zymo input plate |
| 96-well PCR plate or clean receiver plate | Final Zymo elution receiver |
| p300 tip racks | Same locations as pilot protocol |
| p20 tip rack | Same location as pilot protocol |
| Water or nuclease-free water | Mock reagent/sample |
| Food dye or tracking dye, optional | Visual confirmation of liquid placement |
| Plate seals | Vortex/centrifuge handling rehearsal |
| Camera or phone | Photo documentation |

Optional: use real Norgen slurry in 2-4 wells if you specifically want to test pellet/decant behavior. Do not use real samples for this QC.

## Test Layout

Use the same layout as the 16-well pilot, but with water or dyed water.

| Column | Meaning | Wells |
|---|---|---|
| Column 1 | OT-2 path | A1-H1 |
| Column 2 | Manual path | A2-H2 |

Run OT-2 scripts on column 1. Process column 2 manually with matching water additions, plate moves and centrifugation steps so the rehearsal reflects manual versus OT-2 workflow comparison.

## Run Settings

Use the same pilot defaults:

| Step | Script | N_SAMPLES | WELL_START | FILTER_COL_START | TIP_START | P20_TIP_START |
|---|---|---:|---:|---:|---:|---:|
| 1 | `1_add_slurry_lysis.py` | 8 | 0 | 0 | 0 | N/A |
| 3 | `3_etoh_centrifuge.py` | 8 | 0 | 0 | 2 | N/A |
| 4 | `4_transfer_to_filter.py` | 8 | 0 | 0 | 0 | N/A |
| 5 | `5_norgen_wash_elute.py` | 8 | ignored | 0 | 13 | N/A |
| 5b | `5b_dnase_digestion.py` | 8 | ignored | 0 | 0 | 0 |
| 6 | `6_zymo_clean_conc.py` | 8 | ignored | 0 | 17 | 1 |

## Procedure

### 1. Setup Check

1. Install the updated custom Norgen labware definition on the OT-2.
2. Place used Norgen and Zymo plates on their matching collection/receiver plates.
3. Mark A1 clearly on every plate.
4. Confirm plates sit flat on adapters, collection plates and centrifuge buckets.
5. Prepare water or lightly dyed water in the reservoirs used by the scripts.

Record:

| Check | Pass/Fail | Notes |
|---|---|---|
| Norgen plate sits flat |  |  |
| Zymo plate sits flat |  |  |
| A1 orientation clear |  |  |
| No visibly broken pilot-column wells |  |  |

### 2. Step 1 Water Addition

Run:

```bash
N_SAMPLES=8 WELL_START=0 TIP_START=0 opentrons_execute 1_add_slurry_lysis.py
```

Use water instead of slurry and lysis buffer.

Check:

- A1-H1 in the 48-well plate receive liquid.
- No liquid appears in unintended wells.
- Dispense height does not splash or hit the well wall badly.
- Tip pickup starts at A1 and then B1.

### 3. Step 3 Decant Rehearsal

Run:

```bash
N_SAMPLES=8 WELL_START=0 TIP_START=2 opentrons_execute 3_etoh_centrifuge.py
```

Use water or dyed water in place of EtOH/re-lysis/EtOH wash. If testing pellet behavior, add real Norgen slurry to 2-4 wells before running this step.

Check:

- Added liquid does not overflow the 48-well plate.
- After centrifuge pause, the plate can be returned without orientation confusion.
- Decant removes liquid from A1-H1 only.
- Residual volume after decant is consistent across wells.
- Tip does not visibly scrape the bottom or disturb pellet/mock pellet.
- Liquid trash does not splash.

Record:

| Well | Residual liquid low/medium/high | Pellet disturbed? | Notes |
|---|---|---|---|
| A1 |  |  |  |
| B1 |  |  |  |
| C1 |  |  |  |
| D1 |  |  |  |
| E1 |  |  |  |
| F1 |  |  |  |
| G1 |  |  |  |
| H1 |  |  |  |

### 4. Step 4 Transfer to Used Norgen Plate

Run:

```bash
N_SAMPLES=8 WELL_START=0 FILTER_COL_START=0 TIP_START=0 opentrons_execute 4_transfer_to_filter.py
```

Check:

- A1-H1 of the used Norgen plate receive liquid.
- Tip is centered in Norgen wells after the labware x/y offset change.
- Liquid lands in the well/membrane area, not on the edge.
- No visible splash or cross-well contamination.

Photo targets:

| Position | Photo taken? | Centered? | Notes |
|---|---|---|---|
| Norgen A1 |  |  |  |
| Norgen H1 |  |  |  |
| Norgen A2 |  |  |  |
| Norgen H2 |  |  |  |

Before Step 5, manually load matching water volume into Norgen column 2. From this point onward, keep column 2 manual: add wash, elution, DNase and Zymo reagents by hand while the OT-2 scripts process column 1.

### 5. Step 5 Norgen Wash/Elute Rehearsal

Run:

```bash
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=13 opentrons_execute 5_norgen_wash_elute.py
```

Use water instead of Norgen wash buffer and elution buffer.

Check:

- OT-2 wash additions go to column 1 only.
- Manual wash additions go to column 2 only.
- Used Norgen filter wells flow through after centrifugation.
- Collection plate wells match the expected columns.
- No obvious clogged wells or liquid retained in only one row.
- OT-2 elution water is added to column 1 and manual elution water is added to column 2.
- Elution receiver plate preserves the same well map.

Record:

| Column | Flow-through present? | Retained liquid? | Notes |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |

### 6. Step 5b DNase Addition Mock

Run:

```bash
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=0 opentrons_execute 5b_dnase_digestion.py
```

Use water instead of DNase master mix.

Check:

- p20 aspirates from reservoir A1.
- OT-2 13 uL additions are visible or traceable in column 1.
- Manual 13 uL additions are visible or traceable in column 2.
- Tip does not touch the well bottom aggressively.
- p20 uses A1.

### 7. Step 6 Zymo Rehearsal

Run:

```bash
N_SAMPLES=8 FILTER_COL_START=0 TIP_START=17 P20_TIP_START=1 opentrons_execute 6_zymo_clean_conc.py
```

Use water or dyed water instead of binding buffer, EtOH, RNA prep buffer, wash buffer and nuclease-free water.

Check:

- OT-2 sample plate additions go to column 1 only; manual additions go to column 2 only.
- Transfer from sample plate to used Zymo filter plate preserves the map for both workflows.
- OT-2 Zymo filter additions go to column 1 only; manual additions go to column 2 only.
- Used Zymo wells flow through after centrifugation.
- Final 15 uL p20 water addition lands near the membrane center.
- Final receiver plate is correctly aligned.
- p300 starts at expected tip and p20 starts at B1 if the Step 5b rack is reused.

## Pass/Fail Criteria

Pass the rehearsal if all are true:

1. All intended wells in columns 1-2 receive liquid by the intended method.
2. No unintended wells receive liquid.
3. Norgen and Zymo filter targets are visually centered.
4. No major splash, overflow or cross-well contamination is observed.
5. Used filter plates show flow-through in the expected collection wells.
6. Decant does not visibly scrape or disturb the bottom/pellet region.
7. Tip usage follows the expected tip-start map.
8. Operator pauses are understandable and plate orientation remains clear.

If any item fails, record the exact well, step, photo and suspected cause before changing scripts or labware definitions.

## Photo Log

| Step | Required photo | Done? | Notes |
|---|---|---|---|
| Setup | Norgen and Zymo A1 orientation |  |  |
| Step 3 | 48-well plate after decant |  |  |
| Step 4 | Norgen A1-H1 after transfer |  |  |
| Step 5 | Norgen collection plate after spin |  |  |
| Step 6 | Zymo filter plate after transfer |  |  |
| Step 6 | Final receiver plate after elution mock |  |  |
