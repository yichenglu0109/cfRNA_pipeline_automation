# OT-2 Setup Checklist

Author: Peter Lu  
Date: 2026-04-25

Use this checklist before running an OT-2 protocol, after changing pipettes or labware, after moving the robot, or when troubleshooting positioning errors.

## 1. Connect and Update

1. Turn on the OT-2 and open the Opentrons App on the lab computer.
2. Go to Devices and select the OT-2.
3. If the App reports a software mismatch or update warning, update the robot software before running protocols.
4. If the App itself needs an update, update the App first, reconnect to the OT-2, then update the robot software if prompted.
5. Wait for the OT-2 to restart and reconnect after updates.

Do not run a protocol if the App and robot software versions do not match.

## 2. Clear the Deck

Before calibration or setup:

1. Remove old labware, reservoirs, plates, tubes and loose tips.
2. Empty and reinstall the trash bin.
3. Wipe any spills from the deck.
4. Keep only the required calibration items on the deck during calibration.
5. Confirm the robot is on a stable bench and has not been moved since the last deck calibration.

## 3. Confirm Pipettes

1. Check the protocol for `load_instrument()` and confirm the required pipette models and mounts.
2. If attaching or changing pipettes, use the App workflow: Devices -> OT-2 -> Pipettes and Modules -> mount -> three-dot menu -> Attach pipette.
3. Follow the App instructions to attach and calibrate the pipette.
4. Confirm the physical pipettes match the script before importing or running the protocol.

For the current cfRNA scripts, some scripts assume `p300_single_gen2` and `p20_single_gen2`. If the robot has `p1000_single_gen2` and `p300_multi_gen2`, do not run the existing production scripts without refactoring and testing.

## 4. Calibrate the Robot

Run calibration when setting up a new OT-2, moving the robot, changing pipettes, using a new tip type, or seeing tip pickup/scraping/positioning errors.

Calibration order:

1. Deck calibration.
2. Tip length calibration for each pipette and tip type.
3. Pipette offset calibration for each installed pipette.

During calibration:

1. Remove unrelated labware from the deck.
2. Use the correct trash bin, tip rack and pipette for the guided calibration.
3. Seat tips firmly during tip length calibration.
4. Use small jog increments near the deck or calibration point.
5. Stop if the pipette touches or pushes into the deck, tip rack or labware.

After calibration, confirm the App shows current timestamps for deck, tip length and pipette offsets.

## 5. Install Required Labware

For standard labware:

1. Search https://labware.opentrons.com/.
2. Copy the API load name exactly.
3. Confirm the script uses the same name in `protocol.load_labware()`.

For custom labware:

1. Import the required `.json` file into the Opentrons App.
2. Confirm every computer/operator running the protocol has the same custom labware file installed.
3. Confirm the physical labware matches the JSON definition.

Custom labware for this repo:

| Load name | JSON file |
|---|---|
| `custom_48_wellplate_7000ul` | `cfRNA_pipeline_automation/Opentrons/labware/custom_48_wellplate_7000ul.json` |
| `custom_norgen_96filterplate` | `cfRNA_pipeline_automation/Opentrons/labware/custom_norgen_96filterplate.json` |
| `custom_norgen_96filterplate_on_2ml_deep` | `cfRNA_pipeline_automation/Opentrons/labware/custom_norgen_96filterplate_on_2ml_deep.json` |
| `custom_zymo_96filterplate` | `cfRNA_pipeline_automation/Opentrons/labware/custom_zymo_96filterplate.json` |

## 6. Upload Protocol and Run Labware Position Check

1. Upload the `.py` protocol in the Opentrons App.
2. Confirm the protocol imports without simulation errors.
3. Confirm the App deck map matches the physical deck.
4. Confirm pipettes, labware, tip racks and modules match the protocol.
5. Place all labware in the exact slots shown in the App.
6. Open the Setup tab.
7. Expand Labware Offsets.
8. Click Run Labware Position Check.
9. Follow the App prompts and align the pipette to each checked labware.
10. Complete Labware Position Check before adding samples or expensive reagents.

Offsets are specific to a labware-and-slot combination. Recheck offsets after changing labware, slots, adapters or protocol files.

## 7. Run Water Tests

Run water/mock-liquid tests before production samples, after calibration changes, or when using a new pipette, tip type or custom labware.

Test scripts in this folder:

- `test_water_transfer.py`
- `test_multi_transfer.py`

Procedure:

1. Run `test_water_transfer.py` for single-channel transfer checks.
2. Run `test_multi_transfer.py` for multi-tube positional checks with the p300 single-channel pipette.
3. Watch tip pickup, tip seating, aspiration height, dispense location and droplet behavior.
4. Stop and fix calibration or labware offsets if the pipette scrapes, misses wells, fails tip pickup or dispenses outside the target.

## 8. Set Starting Tips

Before every script:

1. Confirm which tip racks are loaded.
2. Confirm which tips have already been used.
3. Set `p300.starting_tip`, `p20.starting_tip`, `TIP_START` or the script-specific starting-tip variable before running.
4. Replace the tip rack if the used-tip state is uncertain.

Do not assume a new script knows which tips were used by a previous script.

## References

- Opentrons App installation: https://docs.opentrons.com/ot-2/opentrons-app/installation/
- Robot software update: https://docs.opentrons.com/ot-2/opentrons-app/update/
- OT-2 calibration: https://docs.opentrons.com/ot-2/calibration/robot-calibration/
- Labware offsets: https://docs.opentrons.com/ot-2/calibration/labware-offsets/
- Labware API names: https://docs.opentrons.com/python-api/labware/
- Labware Library: https://labware.opentrons.com/
