"""
OT-2 tube pilot test: safe custom 4-way 8-position 15 mL rack position test.

Upload labware/custom_4way_8x15ml_tuberack.json in the Opentrons App before
uploading this protocol.
"""

from opentrons import protocol_api


metadata = {
    "protocolName": "cfRNA tube pilot test - safe 4-way 15 mL rack position hover",
    "author": "Peter Lu",
    "apiLevel": "2.13",
}


CUSTOM_RACK = "custom_4way_8x15ml_tuberack"
TIPS_300 = "opentrons_96_tiprack_300ul"

SLOT_15ML_RACK = 2
SLOT_TIPS_300 = 8

SOURCE_WELLS = ["A1", "B1", "A2", "B2"]
DEST_WELLS = ["A3", "B3", "A4", "B4"]

HOVER_FROM_TOP = 10.0


def run(protocol: protocol_api.ProtocolContext):
    rack = protocol.load_labware(CUSTOM_RACK, SLOT_15ML_RACK)
    tips = protocol.load_labware(TIPS_300, SLOT_TIPS_300)

    p300 = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tips])
    sources = [rack.wells_by_name()[name] for name in SOURCE_WELLS]
    dests = [rack.wells_by_name()[name] for name in DEST_WELLS]

    protocol.pause(
        f"Load custom 8-well 15 mL rack in SLOT {SLOT_15ML_RACK}. "
        f"Place empty 15 mL tubes in {', '.join(SOURCE_WELLS + DEST_WELLS)}. "
        f"Resume to move the p300 above each tube at top({HOVER_FROM_TOP}). "
        "This test does not aspirate, dispense, or enter the tubes."
    )

    p300.pick_up_tip()
    for well in sources + dests:
        p300.move_to(well.top(HOVER_FROM_TOP))
        protocol.delay(seconds=0.5)
    p300.drop_tip()

    protocol.pause(
        "Hover position check complete. If all positions looked centered and safe, "
        "resume to repeat the same hover path in reverse."
    )

    p300.pick_up_tip()
    for well in reversed(sources + dests):
        p300.move_to(well.top(HOVER_FROM_TOP))
        protocol.delay(seconds=0.5)
    p300.drop_tip()

    protocol.comment(
        "Test complete. This was a no-liquid, top-only position check. "
        "If hover positions are off-center, edit x/y in the custom labware JSON."
    )
