# OT-2 cfRNA Pipeline – Progress Notes

## Status: First draft complete, pending lab validation

---

## Completed files

| File | Description | Status |
|------|-------------|--------|
| `scripts/OT2/config.py` | Shared labware names, volumes, env-var overrides | ✅ Done |
| `scripts/OT2/1_add_slurry_lysis.py` | Add slurry (200 µL) + lysis buffer (9×200 µL) to 48-well plate | ✅ Done |
| `scripts/OT2/3_etoh_centrifuge.py` | EtOH addition (15×200 µL) → mix → decant supernatant → re-lysis → EtOH wash | ✅ Done |
| `scripts/OT2/4_transfer_to_filter.py` | Transfer sample from 48-well → Norgen 96-well filter plate | ✅ Done |
| `scripts/OT2/5_norgen_wash_elute.py` | 3× Norgen wash (2×200 µL each) + elution (120 µL) | ✅ Done |
| `scripts/OT2/6_zymo_clean_conc.py` | Zymo binding, EtOH, RNA prep, 2× wash; transfer to Zymo filter | ✅ Done |
| `example/run_cfRNA_pipeline_OT2.sh` | Bash orchestrator: SSH into OT-2, run scripts in order, prompt user at manual steps | ✅ Done |

Original OT-1 scripts in `scripts/48_format/` are untouched.

---

## Key OT-1 → OT-2 differences implemented

| Aspect | OT-1 | OT-2 (this code) |
|--------|------|-----------------|
| Lysis buffer (1800 µL) | 2 × 900 µL (P1200 8ch) | 9 × 200 µL (P300 8ch) |
| EtOH (3000 µL) | 3 × 1000 µL (P1200 8ch) | 15 × 200 µL (P300 8ch) |
| Mixing after EtOH | P1200 8ch per row | P1000 single per well |
| Supernatant decant | P1200 8ch per row | P1000 single per well |
| Sample transfer (Step 4) | P1200 8ch per row | P1000 single per well |
| Wash / elute | P1200 8ch 1 dispense | P300 8ch 2 dispenses |
| Execution | Serial port + `opentrons==2.5.2` | SSH + `opentrons_execute` (API v2) |
| Deck slot naming | Letter+number (A1, B2…) | Number (1–11) |

---

## Before first run: items to complete

### 1. Custom labware JSON files (critical)
Three custom labware definitions need to be created in **Opentrons Labware Creator**
(https://labware.opentrons.com/create/) and uploaded to the robot at `/data/labware/`:

| `config.py` name | Physical item | Key dimensions to measure |
|-----------------|---------------|--------------------------|
| `custom_48_wellplate_7000ul` | Thomas Scientific 1149Q15 | 8 rows × 6 cols, 9 mm col spacing, 18 mm row spacing, depth 65 mm |
| `custom_norgen_96filterplate` | Norgen filter plate (kit 29500) | 96-well, 8.8 mm spacing |
| `custom_zymo_96filterplate` | Zymo filter plate (kit R1080) | 96-well, 8.8 mm spacing |

### 2. SSH setup
```bash
# On your Mac, generate key if you don't have one
ssh-keygen -t ed25519

# Copy key to robot (USB connection: robot IP = 169.254.56.55)
ssh-copy-id root@169.254.56.55
```

### 3. Sync config to robot
```bash
scp Opentrons/scripts/OT2/config.py root@169.254.56.55:/data/user_storage/cfRNA/
```
The bash script handles syncing the other scripts automatically on each run.

### 4. Validate tip counting in Script 5
Script 5 assumes P300 starts at **row F (index 5)** because rows A–E were used in Script 3.
If Script 3 uses fewer tips than expected, adjust this line in `5_norgen_wash_elute.py`:
```python
p300.starting_tip = tips_200.rows()[5][0]   # row F
```

### 5. Centrifuge speed validation
Paper says **1,000 g** for the first slurry pellet spin (Step 3B prompt in script).  
OT-1 code used "2000 RPM" — verify your centrifuge's RPM-to-g conversion before first run.

### 6. Tip rack capacity check (Script 3)
Script 3 uses the P1000 single for mixing (48 tips) + decanting (48 tips) = 96 tips total.
A single tip rack has 96 tips. The script prompts to replace the rack at column 3 (after 24 wells).
Confirm this timing is correct for your tip rack brand.

---

## How to run

```bash
# First time: set up SSH key (see above)

# Sync scripts and run pipeline
cd Opentrons
bash example/run_cfRNA_pipeline_OT2.sh expt1

# Override volumes if needed (e.g. 500 µL plasma samples)
LYSIS_VOL=900 ETOH_VOL=1500 bash example/run_cfRNA_pipeline_OT2.sh expt2
```

Log files are saved to `Opentrons/logs/<expt_prefix>.<datetime>.log`.
