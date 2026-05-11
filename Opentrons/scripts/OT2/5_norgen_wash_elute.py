"""
Deprecated compatibility stub.

Step 5 is intentionally split so the wash/dry-spin receiver can be discarded
before Norgen elution. Both Step 5 wash and Step 5b elution use the Norgen
filter plate on a 2 mL deep-well plate stack.

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
        "then replace the 2 mL deep-well collection plate with a clean 2 mL "
        "deep-well elution plate and run 5b_norgen_elute.py."
    )
