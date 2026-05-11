# OT-2 cfRNA Pipeline – Session Notes
Date: 2026-04-21

## Robot Setup
- OT-2 with **p300_single_gen2** (left mount) and **p20_single_gen2** (right mount, unused in this protocol)
- Calibration completed

## What Was Done This Session

### 1. Fixed App simulation errors
- `apiLevel` changed from imported variable `API_LEVEL` to literal `'2.13'` in all scripts
- Added `try/except ImportError` fallback so scripts simulate locally without `config.py`
- Replaced custom labware names with `nest_96_wellplate_2ml_deep` in fallback for simulation

### 2. Rewrote all scripts for p300_single_gen2
All scripts originally used `p300_multi_gen2` + `p1000_single_gen2`.
Rewritten to use only `p300_single_gen2` (left mount):

| Script | Key volume changes |
|--------|-------------------|
| Step 1 | Slurry 190µL/well; Lysis 8×225µL/well |
| Step 3 | EtOH 12×250µL/well; Decant 4×250µL×6 heights/well |
| Step 4 | Transfer 4×250µL/well |
| Step 5 | Wash 2×200µL/well; Elution 120µL/well |
| Step 6 | Dispense max 250µL/aspirate; Transfer 4×250µL/well |

### 3. Replaced nest_12_reservoir_15ml → nest_1_reservoir_195ml
- Lab does not have 12-well reservoir
- Script 1 and 5 updated to use single-well 195mL reservoir
- Well reference changed from `wells_by_name()['A9']` to `wells()[0]`

### 4. Added N_SAMPLES parameter
- All scripts now support `N_SAMPLES` env var (default 48)
- Set `N_SAMPLES=2` for initial testing with 2 sample wells

### 5. B-ME (beta-mercaptoethanol) steps → manual + fume hood
OT-2 cannot fit in fume hood. B-ME steps replaced with `protocol.pause()`:

| Script | Step | Change |
|--------|------|--------|
| Script 1 | Step 1B – add lysis buffer + B-ME | Robot pauses → user adds manually at hood |
| Script 3 | Step 3C end – discard B-ME waste | Robot pauses → user disposes at hood |
| Script 3 | Step 3D – add re-lysis buffer + B-ME | Robot pauses → user adds manually at hood |

Original robot dispensing code preserved as commented-out blocks with `# TO AUTOMATE LATER` note.

### 6. Added test scripts
- `test_water_transfer.py` – single transfer A1→B1, 200µL (robot validation)
- `test_multi_transfer.py` – 4 transfers A1-A4→B1-B4, new tip each (positional accuracy test)
- Both tests passed successfully ✅

### 7. Added TIPS_300 to config
```python
TIPS_300 = 'opentrons_96_tiprack_300ul'
```

---

## Current Labware Status

### Available
- p300_single_gen2 ✅
- opentrons_96_tiprack_300ul ✅
- opentrons_24_aluminumblock_nest_2ml_snapcap ✅

### Need to Order
- `nest_1_reservoir_195ml` × 3 (lysis buffer, EtOH, wash/elution)
- `opentrons_96_tiprack_300ul` × more boxes (Steps 3 and 6 need 2 racks each)

### Need Custom Labware JSON + Physical Plates
| Labware | Physical item | Used in |
|---------|--------------|---------|
| `custom_48_wellplate_7000ul` | Thomas Scientific 1149Q15 | Steps 1, 3, 4 |
| `custom_norgen_96filterplate` | Norgen kit 29500 filter plate | Steps 4, 5 |
| `custom_zymo_96filterplate` | Zymo kit R1080 filter plate | Step 6 |

---

## Pending Tasks

- [ ] Simulate scripts 3–6 in Opentrons App to verify no errors
- [ ] Order `nest_1_reservoir_195ml` reservoirs
- [ ] Obtain Thomas Scientific 1149Q15 and create labware JSON
- [ ] Obtain Norgen kit 29500 and Zymo kit R1080 (filter plate JSONs)
- [ ] Water-test Script 1 once reservoir arrives
- [ ] Rewrite Scripts 3–6 to full p300 (decant is slow but feasible)
- [ ] Decide if p1000 can be added to robot for Step 3 mixing/decanting efficiency

---

## Volume Safety Check (per well, 48-well plate, 7mL max)
| Step | Added | Cumulative |
|------|-------|-----------|
| Slurry | 190 µL | 190 µL |
| Lysis buffer | 1800 µL | 1990 µL |
| Sample (plasma) | ~1000 µL | ~2990 µL |
| EtOH (Step 3) | 3000 µL | ~5990 µL ✅ |

⚠️ If plasma sample > 1 mL, cumulative volume approaches 7 mL limit.

---

## B-ME Safety Note
Beta-mercaptoethanol (1.2%) is used in:
- **Step 1B**: lysis buffer (first exposure)
- **Step 3D**: re-lysis buffer

All B-ME handling must be done at **fume hood**. OT-2 pauses at these steps.
