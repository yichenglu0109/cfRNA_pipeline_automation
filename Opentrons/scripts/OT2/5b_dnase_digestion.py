"""
Deprecated compatibility stub.

DNase digestion is now Step 5c because Step 5b is reserved for Norgen elution
into the 2 mL deep-well plate.

Use:
  1. 5_norgen_wash.py
  2. 5b_norgen_elute.py
  3. 5c_dnase_digestion.py
"""

from opentrons import protocol_api

metadata = {
    'protocolName': 'DEPRECATED cfRNA Step 5b – Use 5c_dnase_digestion.py',
    'author': 'Peter Lu',
    'apiLevel': '2.13',
}


def run(protocol: protocol_api.ProtocolContext):
    protocol.pause(
        "5b_dnase_digestion.py is deprecated. Run 5b_norgen_elute.py for "
        "Norgen elution, then run 5c_dnase_digestion.py for DNase digestion."
    )
