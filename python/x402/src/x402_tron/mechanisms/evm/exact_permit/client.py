"""
ExactPermitEvmClientMechanism - "exact_permit" payment scheme EVM client mechanism
"""

from x402_tron.address import AddressConverter, EvmAddressConverter
from x402_tron.mechanisms._exact_permit_base.client import BaseExactPermitClientMechanism


class ExactPermitEvmClientMechanism(BaseExactPermitClientMechanism):
    def _get_address_converter(self) -> AddressConverter:
        return EvmAddressConverter()
