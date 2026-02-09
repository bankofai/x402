"""
KeyProvider Protocol - abstraction for private key management.

Any key management backend (agent-wallet, HSM, remote signer, etc.)
can be used with x402 signers by implementing this protocol.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class KeyProvider(Protocol):
    """Minimal interface that a key management backend must satisfy.

    agent-wallet's TronProvider / FlashProvider can be adapted via
    ``TronProviderAdapter``.
    """

    def get_address(self) -> str:
        """Return the TRON base58check address."""
        ...

    def get_private_key(self) -> str:
        """Return the hex-encoded private key (without 0x prefix)."""
        ...
