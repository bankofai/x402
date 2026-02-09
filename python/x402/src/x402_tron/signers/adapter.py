"""
Adapter that bridges agent-wallet providers to the KeyProvider protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wallet import BaseProvider


class TronProviderAdapter:
    """Adapt agent-wallet's ``TronProvider`` (or ``FlashProvider``) to ``KeyProvider``.

    Reads ``address`` and ``_private_key_hex`` from the provider instance.

    Normally you don't use this directly — ``AgentWalletClientSigner`` and
    ``AgentWalletFacilitatorSigner`` wrap it automatically::

        from wallet import TronProvider
        from x402_tron.signers.client import AgentWalletClientSigner

        provider = TronProvider(private_key="deadbeef...")
        signer = AgentWalletClientSigner(provider, network="tron:nile")
    """

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    def get_address(self) -> str:
        addr = getattr(self._provider, "address", None)
        if not addr:
            raise ValueError("Provider has no address (private key not set?)")
        return addr

    def get_private_key(self) -> str:
        pk = getattr(self._provider, "_private_key_hex", None)
        if not pk:
            raise ValueError("Provider has no private key")
        return pk[2:] if pk.startswith("0x") else pk
