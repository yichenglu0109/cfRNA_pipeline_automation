"""
Simple water transfer test – verify robot calibration and pipette function.

Deck layout
-----------
Slot 1 : opentrons_24_aluminumblock_nest_2ml_snapcap
         A1 = source tube (fill with ~500 µL water before starting)
         B1 = destination tube (empty)
Slot 2 : opentrons_96_tiprack_300ul

Pipettes
--------
Left : p300_single_gen2
"""

from opentrons import protocol_api

metadata = {
    'protocolName': 'Water Transfer Test',
    'author': 'Lab Test',
    'apiLevel': '2.13',
}


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    block    = protocol.load_labware('opentrons_24_aluminumblock_nest_2ml_snapcap', 1)
    tips_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

    # ── Pipette ───────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])

    src = block.wells_by_name()['A1']   # water source
    dst = block.wells_by_name()['B1']   # destination (empty)

    protocol.pause(
        "Place aluminum block at SLOT 1. "
        "Fill tube A1 with ~500 µL water. "
        "Leave tube B1 empty. Resume when ready."
    )

    p300.starting_tip = tips_300.wells_by_name()['A2']

    # Transfer 200 µL from A1 → B1
    p300.pick_up_tip()
    p300.aspirate(200, src.bottom(2))
    protocol.delay(seconds=1)
    p300.dispense(200, dst.bottom(2))
    p300.blow_out(dst.bottom(5))
    p300.drop_tip()

    protocol.comment("Test complete. Check that ~200 µL water moved from A1 to B1.")
