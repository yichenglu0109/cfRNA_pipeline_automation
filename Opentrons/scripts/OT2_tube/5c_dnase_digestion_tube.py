"""
OT-2 tube pilot Step 5c: add DNase master mix to Norgen eluates.
"""

import os

try:
    from config import *
except ImportError:
    import math

    API_LEVEL = "2.13"
    N_SAMPLES = int(os.environ.get("N_SAMPLES", "4"))
    TIP_START = int(os.environ.get("TIP_START", "34"))
    P20_TIP_START = int(os.environ.get("P20_TIP_START", "0"))

    LYSIS_VOL = float(os.environ.get("LYSIS_VOL", "1800"))
    ETOH_VOL = float(os.environ.get("ETOH_VOL", "3000"))
    SLURRY_VOL = 200
    RELYSIS_VOL = 300
    ETOH_WASH_VOL = 300
    NORGEN_WASH_VOL = 400
    NORGEN_ELU_VOL = 100
    DNASE_VOL = 13
    ZYMO_BIND_VOL = 226
    ZYMO_ETOH_VOL = 339
    ZYMO_PREP_VOL = 400
    ZYMO_WASH1_VOL = 700
    ZYMO_WASH2_VOL = 400
    ZYMO_LOAD_VOL = 226
    ZYMO_LOAD_REPS = 3
    ZYMO_FINAL_ELU_VOL = 15

    REAGENT_EXCESS = 1.2
    DNASE_EXCESS = 1.1
    P300_MAX = 250
    P20_MAX = 18

    TIPS_300 = "opentrons_96_tiprack_300ul"
    TIPS_20 = "opentrons_96_tiprack_20ul"
    TUBE_BLOCK_2ML = "opentrons_24_aluminumblock_nest_2ml_snapcap"
    RESERVOIR_1 = "nest_1_reservoir_195ml"
    SAMPLE_TUBE_RACK = os.environ.get("SAMPLE_TUBE_RACK", "3dprinted_15_tuberack_15000ul")

    USE_CUSTOM_15ML_RACK = os.environ.get("USE_CUSTOM_15ML_RACK", "0") == "1"
    CUSTOM_15ML_RACK_LOAD_NAME = os.environ.get("CUSTOM_15ML_RACK_LOAD_NAME", "3dprinted_15_tuberack_15000ul")
    CUSTOM_15ML_RACK_X0 = float(os.environ.get("CUSTOM_15ML_RACK_X0", "13.88"))
    CUSTOM_15ML_RACK_Y0 = float(os.environ.get("CUSTOM_15ML_RACK_Y0", "69.24"))
    CUSTOM_15ML_RACK_X_SPACING = float(os.environ.get("CUSTOM_15ML_RACK_X_SPACING", "25.0"))
    CUSTOM_15ML_RACK_Y_SPACING = float(os.environ.get("CUSTOM_15ML_RACK_Y_SPACING", "-25.0"))
    CUSTOM_15ML_RACK_WELL_Z = float(os.environ.get("CUSTOM_15ML_RACK_WELL_Z", "8.0"))
    CUSTOM_15ML_RACK_DIAMETER = float(os.environ.get("CUSTOM_15ML_RACK_DIAMETER", "14.9"))
    CUSTOM_15ML_RACK_DEPTH = float(os.environ.get("CUSTOM_15ML_RACK_DEPTH", "117.5"))
    CUSTOM_15ML_RACK_TOTAL_X = float(os.environ.get("CUSTOM_15ML_RACK_TOTAL_X", "127.76"))
    CUSTOM_15ML_RACK_TOTAL_Y = float(os.environ.get("CUSTOM_15ML_RACK_TOTAL_Y", "85.48"))
    CUSTOM_15ML_RACK_TOTAL_Z = float(os.environ.get("CUSTOM_15ML_RACK_TOTAL_Z", "125.5"))

    SLOT_REAGENT_A = 5
    SLOT_SAMPLE_TUBES = 2
    SLOT_REAGENT_B = 3
    SLOT_SHARED_2ML = 4
    SLOT_TRASH = 6  # reserved; Step 3 uses the same 15 mL rack for waste by default
    SLOT_TIPS_20 = 7
    SLOT_TIPS_300_A = 8
    SLOT_TIPS_300_B = 9

    SAMPLE_TUBES = os.environ.get("SAMPLE_TUBES", "A1,A2,A3,A4").split(",")
    TRASH_TUBES = os.environ.get("TRASH_TUBES", "C1,C2,C3,C4").split(",")
    ELUATE_TUBES = ["A1", "B1", "C1", "D1"]
    ZYMO_INPUT_TUBES = ELUATE_TUBES
    NORGEN_COLUMN_TUBES = ["A1", "B1", "C1", "D1"]
    ZYMO_COLUMN_TUBES = ["A2", "B2", "C2", "D2"]
    DNASE_MIX_TUBE = "A4"
    ZYMO_BIND_TUBE = "B4"
    ZYMO_ETOH_TUBE = "C4"
    ZYMO_PREP_TUBE = "D4"
    ZYMO_WASH2_TUBE = "A5"
    ZYMO_WATER_TUBE = "B5"
    NORG_ELU_TUBE = "C5"

    SAMPLE_ASPIRATE_H = float(os.environ.get("SAMPLE_ASPIRATE_H", "1.0"))
    SAMPLE_MIX_LOW_H = float(os.environ.get("SAMPLE_MIX_LOW_H", "2.0"))
    SAMPLE_MIX_HIGH_H = float(os.environ.get("SAMPLE_MIX_HIGH_H", "12.0"))
    SAMPLE_DISPENSE_H = float(os.environ.get("SAMPLE_DISPENSE_H", "25.0"))
    SAMPLE_TOP_DISPENSE_OFFSET = float(os.environ.get("SAMPLE_TOP_DISPENSE_OFFSET", "-5"))
    TRASH_DISPENSE_H = float(os.environ.get("TRASH_DISPENSE_H", "35.0"))
    REAGENT_TUBE_ASPIRATE_H = float(os.environ.get("REAGENT_TUBE_ASPIRATE_H", "1.0"))
    SLURRY_TUBE_ASPIRATE_H = float(os.environ.get("SLURRY_TUBE_ASPIRATE_H", "2.0"))
    DNASE_DISPENSE_H = float(os.environ.get("DNASE_DISPENSE_H", "5.0"))
    DNASE_BLOWOUT_H = float(os.environ.get("DNASE_BLOWOUT_H", "8.0"))
    NORGEN_COLUMN_DISPENSE_FROM_TOP = float(os.environ.get("NORGEN_COLUMN_DISPENSE_FROM_TOP", "-3.0"))
    NORGEN_COLUMN_BLOWOUT_FROM_TOP = float(os.environ.get("NORGEN_COLUMN_BLOWOUT_FROM_TOP", "0.0"))
    NORGEN_ELUTE_FROM_TOP = float(os.environ.get("NORGEN_ELUTE_FROM_TOP", "-12.0"))
    NORGEN_ELUTE_BLOWOUT_FROM_TOP = float(os.environ.get("NORGEN_ELUTE_BLOWOUT_FROM_TOP", "-8.0"))
    ZYMO_COLUMN_DISPENSE_FROM_TOP = float(os.environ.get("ZYMO_COLUMN_DISPENSE_FROM_TOP", "5.0"))
    ZYMO_COLUMN_BLOWOUT_FROM_TOP = float(os.environ.get("ZYMO_COLUMN_BLOWOUT_FROM_TOP", "5.0"))
    ZYMO_ELUTE_FROM_BOTTOM = float(os.environ.get("ZYMO_ELUTE_FROM_BOTTOM", "5.0"))
    ZYMO_ELUTE_BLOWOUT_FROM_BOTTOM = float(os.environ.get("ZYMO_ELUTE_BLOWOUT_FROM_BOTTOM", "6.0"))

    DECANT_HEIGHTS = [45, 41, 37, 33, 29, 25, 21, 17, 13, 11, 9, 7.5]
    DECANT_VOL = 250
    DECANT_REPS = 2

    def sample_count():
        return max(1, min(N_SAMPLES, len(SAMPLE_TUBES), len(TRASH_TUBES), len(ELUATE_TUBES)))

    def format_ul(ul):
        return f"{ul / 1000:.1f} mL ({ul:.0f} uL)" if ul >= 1000 else f"{ul:.0f} uL"

    def split_volume(volume_ul, max_transfer=P300_MAX):
        n = max(1, math.ceil(volume_ul / max_transfer))
        return n, round(volume_ul / n, 1)

    def wells_by_names(labware, names):
        by_name = labware.wells_by_name()
        return [by_name[name] for name in names]

    def custom_15ml_rack_definition():
        rows = ["A", "B", "C"]
        cols = ["1", "2", "3", "4", "5"]
        wells = {}
        ordering = []
        for col_index, col in enumerate(cols):
            col_wells = []
            for row_index, row in enumerate(rows):
                name = f"{row}{col}"
                wells[name] = {
                    "depth": CUSTOM_15ML_RACK_DEPTH,
                    "totalLiquidVolume": 15000,
                    "shape": "circular",
                    "diameter": CUSTOM_15ML_RACK_DIAMETER,
                    "x": CUSTOM_15ML_RACK_X0 + col_index * CUSTOM_15ML_RACK_X_SPACING,
                    "y": CUSTOM_15ML_RACK_Y0 + row_index * CUSTOM_15ML_RACK_Y_SPACING,
                    "z": CUSTOM_15ML_RACK_WELL_Z,
                }
                col_wells.append(name)
            ordering.append(col_wells)
        return {
            "ordering": ordering,
            "wells": wells,
            "groups": [{"metadata": {"wellBottomShape": "v"}, "wells": [name for col in ordering for name in col]}],
            "metadata": {"displayName": "3D-printed 15 mL tube rack", "displayCategory": "tubeRack", "displayVolumeUnits": "uL"},
            "parameters": {"format": "irregular", "isTiprack": False, "loadName": CUSTOM_15ML_RACK_LOAD_NAME},
            "namespace": "custom_beta",
            "version": 1,
            "schemaVersion": 2,
            "cornerOffsetFromSlot": {"x": 0, "y": 0, "z": 0},
            "dimensions": {"xDimension": CUSTOM_15ML_RACK_TOTAL_X, "yDimension": CUSTOM_15ML_RACK_TOTAL_Y, "zDimension": CUSTOM_15ML_RACK_TOTAL_Z},
            "brand": {"brand": "custom"},
        }

    def load_sample_tube_rack(protocol, slot):
        if USE_CUSTOM_15ML_RACK:
            return protocol.load_labware_from_definition(custom_15ml_rack_definition(), slot)
        return protocol.load_labware(SAMPLE_TUBE_RACK, slot)

    def load_shared_2ml_block(protocol, slot=SLOT_SHARED_2ML):
        return protocol.load_labware(TUBE_BLOCK_2ML, slot)

    def sample_wells(labware):
        return wells_by_names(labware, SAMPLE_TUBES[:sample_count()])

    def trash_wells(labware):
        return wells_by_names(labware, TRASH_TUBES[:sample_count()])

    def shared_eluate_wells(shared_rack):
        return wells_by_names(shared_rack, ELUATE_TUBES[:sample_count()])

    def norgen_column_wells(shared_rack):
        return wells_by_names(shared_rack, NORGEN_COLUMN_TUBES[:sample_count()])

    def zymo_column_wells(shared_rack):
        return wells_by_names(shared_rack, ZYMO_COLUMN_TUBES[:sample_count()])

    def reagent_well(shared_rack, name):
        return shared_rack.wells_by_name()[name]

    def load_p300(protocol, tip_racks=None):
        return protocol.load_instrument("p300_single_gen2", "left", tip_racks=tip_racks or [])

    def load_p20(protocol, tip_racks=None):
        return protocol.load_instrument("p20_single_gen2", "right", tip_racks=tip_racks or [])

    def total_with_excess(per_sample_ul, excess=REAGENT_EXCESS):
        return sample_count() * per_sample_ul * excess

    class ReagentSource:
        def __init__(self, wells, volumes_ul, aspiration_height=REAGENT_TUBE_ASPIRATE_H):
            self.wells = wells
            self.remaining = list(volumes_ul)
            self.index = 0
            self.aspiration_height = aspiration_height

        def aspiration_location(self, volume_ul):
            while self.index < len(self.wells) - 1 and self.remaining[self.index] <= 0:
                self.index += 1
            if self.index < len(self.wells) - 1 and self.remaining[self.index] < volume_ul:
                self.index += 1
            self.remaining[self.index] -= volume_ul
            return self.wells[self.index].bottom(self.aspiration_height)

    def make_single_source(well, total_ul, aspiration_height=REAGENT_TUBE_ASPIRATE_H):
        return ReagentSource([well], [total_ul], aspiration_height=aspiration_height)

from opentrons import protocol_api

metadata = {
    "protocolName": "cfRNA tube pilot Step 5c - DNase Digestion",
    "author": "Peter Lu",
    "apiLevel": "2.13",
}


def run(protocol: protocol_api.ProtocolContext):
    n = sample_count()
    master_mix_total = round(n * DNASE_VOL * DNASE_EXCESS)

    tips = protocol.load_labware(TIPS_20, SLOT_TIPS_20)
    shared = load_shared_2ml_block(protocol)

    p20 = load_p20(protocol, [tips])
    p20.starting_tip = tips.wells()[P20_TIP_START]

    eluates = shared_eluate_wells(shared)
    dnase_src = make_single_source(reagent_well(shared, DNASE_MIX_TUBE), master_mix_total)

    protocol.pause(
        f"STEP 5c: Place Norgen eluates in shared rack positions "
        f"{', '.join(ELUATE_TUBES[:n])}. Prepare {format_ul(master_mix_total)} DNase "
        f"master mix in tube {DNASE_MIX_TUBE}. Resume to add 13 uL per eluate."
    )

    p20.pick_up_tip()
    for tube in eluates:
        p20.aspirate(DNASE_VOL, dnase_src.aspiration_location(DNASE_VOL))
        p20.dispense(DNASE_VOL, tube.bottom(DNASE_DISPENSE_H))
        p20.blow_out(tube.bottom(DNASE_BLOWOUT_H))
    p20.drop_tip()

    protocol.comment(
        "Step 5c complete. Cap tubes, vortex lightly, incubate at 37 C for 20 min, "
        "then proceed to Zymo cleanup."
    )
