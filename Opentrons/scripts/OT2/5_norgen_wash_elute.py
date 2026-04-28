"""
Deprecated compatibility stub.

Step 5 is intentionally split because Norgen wash uses the kit collection plate
under the filter, while Norgen elution uses a 2 mL deep-well receiver under the
filter. Those two physical stacks need different labware definitions and should
be run as separate protocols.

Use:
  1. 5_norgen_wash.py
  2. 5b_norgen_elute.py
  3. 5c_dnase_digestion.py
"""

from opentrons import protocol_api

metadata = {
    'protocolName': 'DEPRECATED cfRNA Step 5 – Use split Norgen wash/elute scripts',
    'author': 'Peter Lu',
    'apiLevel': '2.13',
}


def run(protocol: protocol_api.ProtocolContext):
    protocol.pause(
        "5_norgen_wash_elute.py is deprecated. Run 5_norgen_wash.py first, "
        "then replace the kit collection plate with a clean 2 mL deep-well "
        "elution plate and run 5b_norgen_elute.py."
    )
