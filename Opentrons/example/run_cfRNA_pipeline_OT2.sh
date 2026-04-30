#!/bin/bash
# =============================================================================
# run_cfRNA_pipeline_OT2.sh
#
# Orchestrates the cfRNA extraction pipeline on an OT-2 via SSH.
#
# Usage:
#   bash run_cfRNA_pipeline_OT2.sh <expt_prefix>
#
# Requirements:
#   - OT-2 reachable at $ROBOT_IP (default: 169.254.56.55)
#   - SSH key or password-less SSH configured:
#       ssh-keygen -t ed25519
#       ssh-copy-id root@<ROBOT_IP>
#   - Scripts synced to robot at /data/user_storage/cfRNA/
#   - config.py present at /data/user_storage/cfRNA/ on robot
#
# Env vars you can override:
#   ROBOT_IP    - OT-2 IP address (default 169.254.56.55 = USB)
#   LYSIS_VOL   - µL lysis buffer per column  (default 1800)
#   ETOH_VOL    - µL EtOH per column          (default 3000)
#
# Tip: to run over Wi-Fi, set ROBOT_IP to the robot's Wi-Fi IP shown in the
#      Opentrons App (Device > Network).
# =============================================================================

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────
ROBOT_IP="${ROBOT_IP:-169.254.56.55}"
ROBOT_USER="root"
SCRIPTS_DIR="/data/user_storage/cfRNA"

LYSIS_VOL="${LYSIS_VOL:-1800}"
ETOH_VOL="${ETOH_VOL:-3000}"

# ── Argument check ────────────────────────────────────────────────────────
if [ $# -eq 0 ]; then
    echo "Usage: bash $0 <expt_prefix>"
    echo "  expt_prefix : label prepended to log file, e.g. 'expt1'"
    exit 1
fi

EXPT_PREFIX="$1"
DATETIME=$(date "+%Y_%m_%d_%H_%M_%S")
LOG_DIR="$(dirname "$0")/../logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${EXPT_PREFIX}.${DATETIME}.log"

# Helper: run a script on the robot, stream output here, tee to log
run_on_robot() {
    local script="$1"
    shift
    # Pass extra env vars as KEY=VALUE arguments
    ssh "${ROBOT_USER}@${ROBOT_IP}" \
        "cd ${SCRIPTS_DIR}/OT2 && $* opentrons_execute ${script}" \
        2>&1 | tee -a "$LOG_FILE"
}

# Helper: sync local OT2 scripts to robot
sync_scripts() {
    echo "[sync] Copying OT2 scripts to robot..." | tee -a "$LOG_FILE"
    scp -r "$(dirname "$0")/../scripts/OT2" \
        "${ROBOT_USER}@${ROBOT_IP}:${SCRIPTS_DIR}/"
}

# ── Start ─────────────────────────────────────────────────────────────────
echo "=====================================================" | tee -a "$LOG_FILE"
echo "  cfRNA OT-2 pipeline  |  ${EXPT_PREFIX}  |  ${DATETIME}" | tee -a "$LOG_FILE"
echo "=====================================================" | tee -a "$LOG_FILE"

sync_scripts

# =============================================================================
# ── BATCH 1 (first 48 samples) ───────────────────────────────────────────
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "─── BATCH 1 / 48 samples ────────────────────────────" | tee -a "$LOG_FILE"

# Step 1 – slurry + lysis
echo "[Step 1] Add slurry + lysis buffer" | tee -a "$LOG_FILE"
run_on_robot 1_add_slurry_lysis.py \
    "LYSIS_VOL=${LYSIS_VOL} START_COL=0 STOP_COL=6"

read -rp "Step 2 (manual): Transfer samples, mix, seal, incubate 60°C 10 min. Press ENTER when done. "

# Step 3 – EtOH, centrifuge, decant, re-lysis
echo "[Step 3] EtOH / centrifuge / decant / re-lysis" | tee -a "$LOG_FILE"
run_on_robot 3_etoh_centrifuge.py \
    "LYSIS_VOL=${LYSIS_VOL} ETOH_VOL=${ETOH_VOL} START_COL=0 STOP_COL=6"

# Step 4 – transfer to Norgen filter plate
# Batch 1 always starts at filter column 1 (0-indexed: 0)
FILTER_COL_BATCH1=0

echo "[Step 4] Transfer to Norgen filter plate (col offset ${FILTER_COL_BATCH1})" | tee -a "$LOG_FILE"
run_on_robot 4_transfer_to_filter.py \
    "N_SAMPLES=48 WELL_START=0 FILTER_COL_START=${FILTER_COL_BATCH1} TIP_START=0"

# Step 5 – wash on kit collection plate, then elute into 2 mL deep-well plate
echo "[Step 5] Norgen wash on kit collection plate (batch 1)" | tee -a "$LOG_FILE"
run_on_robot 5_norgen_wash.py \
    "N_SAMPLES=48 FILTER_COL_START=${FILTER_COL_BATCH1} TIP_START=0"

echo "[Step 5b] Norgen elution into 2 mL deep-well plate (batch 1)" | tee -a "$LOG_FILE"
run_on_robot 5b_norgen_elute.py \
    "N_SAMPLES=48 FILTER_COL_START=${FILTER_COL_BATCH1} TIP_START=3"

# Batch 1 done – refrigerate eluate, decide whether to do Zymo now
echo "" | tee -a "$LOG_FILE"
read -rp "Batch 1 complete. Seal and refrigerate elution plate. Proceed to BATCH 2? (y/n): " yn
while [[ ! "$yn" =~ ^[Yy]$ ]]; do
    echo "Waiting... Press y to continue."
    read -rp "" yn
done

# =============================================================================
# ── BATCH 2 (second 48 samples) ──────────────────────────────────────────
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "─── BATCH 2 / second 48 samples ─────────────────────" | tee -a "$LOG_FILE"

echo "[Step 1] Add slurry + lysis buffer (batch 2)" | tee -a "$LOG_FILE"
run_on_robot 1_add_slurry_lysis.py \
    "LYSIS_VOL=${LYSIS_VOL} START_COL=0 STOP_COL=6"

read -rp "Step 2 (manual): Transfer samples, mix, seal, incubate 60°C 10 min. Press ENTER when done. "

echo "[Step 3] EtOH / centrifuge / decant / re-lysis (batch 2)" | tee -a "$LOG_FILE"
run_on_robot 3_etoh_centrifuge.py \
    "LYSIS_VOL=${LYSIS_VOL} ETOH_VOL=${ETOH_VOL} START_COL=0 STOP_COL=6"

echo "[Step 4] Transfer to Norgen filter plate (batch 2, col offset 6)" | tee -a "$LOG_FILE"
run_on_robot 4_transfer_to_filter.py \
    "N_SAMPLES=48 WELL_START=0 FILTER_COL_START=6 TIP_START=0"

echo "[Step 5] Norgen wash on kit collection plate (batch 2, cols 7–12)" | tee -a "$LOG_FILE"
run_on_robot 5_norgen_wash.py \
    "N_SAMPLES=48 FILTER_COL_START=6 TIP_START=0"

echo "[Step 5b] Norgen elution into 2 mL deep-well plate (batch 2, cols 7–12)" | tee -a "$LOG_FILE"
run_on_robot 5b_norgen_elute.py \
    "N_SAMPLES=48 FILTER_COL_START=6 TIP_START=3"

# =============================================================================
# ── DNase digestion (manual) ─────────────────────────────────────────────
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "─── DNase digestion (manual) ────────────────────────" | tee -a "$LOG_FILE"
echo "Mix 1,320 µL 10× DNase buffer + 240 µL Baseline-ZERO DNase." | tee -a "$LOG_FILE"
echo "Add 13 µL master mix to each of the 96 sample wells (P20 multichannel)." | tee -a "$LOG_FILE"
echo "Seal plate, vortex lightly, incubate 20 min at 37°C." | tee -a "$LOG_FILE"
read -rp "Press ENTER when DNase incubation is complete. "

# =============================================================================
# ── ZYMO clean & concentrate (Step 6) ────────────────────────────────────
# =============================================================================
echo "" | tee -a "$LOG_FILE"
read -rp "Proceed to Zymo clean & concentrate? (y/n): " if_zymo
if [[ "$if_zymo" =~ ^[Yy]$ ]]; then
    read -rp "Process how many samples? Enter 48 or 96: " n_samples
    if [[ "$n_samples" == "48" ]]; then
        ZYMO_STOP=6
    else
        ZYMO_STOP=12
    fi

    echo "[Step 6] Zymo clean & concentrate (cols 1–${ZYMO_STOP})" | tee -a "$LOG_FILE"
    run_on_robot 6_zymo_clean_conc.py \
        "START_COL=0 STOP_COL=${ZYMO_STOP}"

    echo "" | tee -a "$LOG_FILE"
    echo "MANUAL FINAL STEP: add 15 µL nuclease-free H2O per well." | tee -a "$LOG_FILE"
    echo "Centrifuge 5 min at 3,000–5,000 g. Aliquot 4 µL into labelled plates. Freeze at -80°C." | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "=====================================================" | tee -a "$LOG_FILE"
echo "  All done! Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "=====================================================" | tee -a "$LOG_FILE"
