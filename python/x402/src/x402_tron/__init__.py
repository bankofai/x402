"""
x402 - Payment Protocol SDK for Python

Supports Client, Server, and Facilitator functionality for multi-chain payments.
"""

__version__ = "0.1.0"

from x402_tron.types import (
    PaymentPermit,
    PaymentPayload,
    PaymentRequirements,
    PaymentRequired,
    VerifyResponse,
    SettleResponse,
)
from x402_tron.exceptions import (
    X402Error,
    SignatureError,
    SignatureVerificationError,
    AllowanceError,
    SettlementError,
    TransactionError,
    TransactionTimeoutError,
    ValidationError,
    PermitValidationError,
    ConfigurationError,
    UnsupportedNetworkError,
    UnknownTokenError,
)
from x402_tron.address import (
    AddressConverter,
    EvmAddressConverter,
    TronAddressConverter,
)
from x402_tron.tokens import TokenInfo, TokenRegistry

__all__ = [
    "__version__",
    # Types
    "PaymentPermit",
    "PaymentPayload",
    "PaymentRequirements",
    "PaymentRequired",
    "VerifyResponse",
    "SettleResponse",
    # Exceptions
    "X402Error",
    "SignatureError",
    "SignatureVerificationError",
    "AllowanceError",
    "SettlementError",
    "TransactionError",
    "TransactionTimeoutError",
    "ValidationError",
    "PermitValidationError",
    "ConfigurationError",
    "UnsupportedNetworkError",
    "UnknownTokenError",
    # Address converters
    "AddressConverter",
    "EvmAddressConverter",
    "TronAddressConverter",
    # Token registry
    "TokenInfo",
    "TokenRegistry",
]
