"""
x402 Mechanisms - Payment mechanisms for different chains

Structure:
    _base/                  - ABC interfaces (ClientMechanism, FacilitatorMechanism, ServerMechanism)
    _exact_permit_base/     - Shared base classes for "exact_permit" scheme
    _native_exact_base/     - Shared base classes for "native_exact" scheme
    evm/                    - EVM chain implementations
        exact_permit/       - exact_permit scheme (client, facilitator, server)
        native_exact/       - native_exact scheme (adapter, client, facilitator, server)
    tron/                   - TRON chain implementations
        exact_permit/       - exact_permit scheme (client, facilitator, server)
        native_exact/       - native_exact scheme (adapter, client, facilitator, server)
"""

from x402_tron.mechanisms import evm, tron
from x402_tron.mechanisms._base import ClientMechanism, FacilitatorMechanism, ServerMechanism
from x402_tron.mechanisms._exact_permit_base import (
    BaseExactPermitClientMechanism,
    BaseExactPermitFacilitatorMechanism,
    BaseExactPermitServerMechanism,
)
from x402_tron.mechanisms._native_exact_base import (
    ChainAdapter,
    NativeExactBaseClientMechanism,
    NativeExactBaseFacilitatorMechanism,
    NativeExactBaseServerMechanism,
)
from x402_tron.mechanisms.evm import (
    ExactPermitEvmClientMechanism,
    ExactPermitEvmFacilitatorMechanism,
    ExactPermitEvmServerMechanism,
    NativeExactEvmClientMechanism,
    NativeExactEvmFacilitatorMechanism,
    NativeExactEvmServerMechanism,
)
from x402_tron.mechanisms.tron import (
    ExactPermitTronClientMechanism,
    ExactPermitTronFacilitatorMechanism,
    ExactPermitTronServerMechanism,
    NativeExactTronClientMechanism,
    NativeExactTronFacilitatorMechanism,
    NativeExactTronServerMechanism,
)

__all__ = [
    # Base interfaces
    "ClientMechanism",
    "FacilitatorMechanism",
    "ServerMechanism",
    # ExactPermit base
    "BaseExactPermitClientMechanism",
    "BaseExactPermitFacilitatorMechanism",
    "BaseExactPermitServerMechanism",
    # Native exact base
    "ChainAdapter",
    "NativeExactBaseClientMechanism",
    "NativeExactBaseFacilitatorMechanism",
    "NativeExactBaseServerMechanism",
    # EVM
    "ExactPermitEvmClientMechanism",
    "ExactPermitEvmFacilitatorMechanism",
    "ExactPermitEvmServerMechanism",
    "NativeExactEvmClientMechanism",
    "NativeExactEvmFacilitatorMechanism",
    "NativeExactEvmServerMechanism",
    # TRON
    "ExactPermitTronClientMechanism",
    "ExactPermitTronFacilitatorMechanism",
    "ExactPermitTronServerMechanism",
    "NativeExactTronClientMechanism",
    "NativeExactTronFacilitatorMechanism",
    "NativeExactTronServerMechanism",
    # Subpackages
    "evm",
    "tron",
]
