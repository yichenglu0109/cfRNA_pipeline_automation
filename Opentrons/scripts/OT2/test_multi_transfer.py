"""
Multi-tube transfer test – verify positional accuracy across multiple wells.

Transfers 200 µL from each source tube (row A) to destination tube (row B).
New tip used for each transfer to also test tip pickup/drop sequence.

Deck layout
-----------
Slot 1 : opentrons_24_aluminumblock_nest_2ml_snapcap
         A1–A4 = source tubes (fill each with ~400 µL water before starting)
         B1–B4 = destination tubes (leave empty)
Slot 2 : opentrons_96_tiprack_300ul

Pipettes
--------
Left : p300_single_gen2
"""

from opentrons import protocol_api

metadata = {
    'protocolName': 'Multi-Tube Transfer Test',
    'author': 'Lab Test',
    'apiLevel': '2.13',
}

TRANSFER_VOL = 200   # µL per transfer
N_TUBES      = 4     # number of source/destination pairs to test


def run(protocol: protocol_api.ProtocolContext):

    # ── Labware ───────────────────────────────────────────────────────────
    block    = protocol.load_labware('opentrons_24_aluminumblock_nest_2ml_snapcap', 1)
    tips_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

    # ── Pipette ───────────────────────────────────────────────────────────
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips_300])

    src_wells = [block.wells_by_name()[f'A{i+1}'] for i in range(N_TUBES)]
    dst_wells = [block.wells_by_name()[f'B{i+1}'] for i in range(N_TUBES)]

    protocol.pause(
        f"Fill tubes A1–A{N_TUBES} each with ~400 µL water. "
        f"Leave tubes B1–B{N_TUBES} empty. Resume when ready."
    )

    for i, (src, dst) in enumerate(zip(src_wells, dst_wells)):
        protocol.comment(f"Transfer {i+1}/{N_TUBES}: A{i+1} → B{i+1}")
        p300.pick_up_tip()
        p300.aspirate(TRANSFER_VOL, src.bottom(2))
        protocol.delay(seconds=1)
        p300.dispense(TRANSFER_VOL, dst.bottom(2))
        p300.blow_out(dst.bottom(5))
        p300.drop_tip()

    protocol.comment(
        f"Test complete. "
        f"Each B1–B{N_TUBES} tube should contain ~{TRANSFER_VOL} µL water."
    )
