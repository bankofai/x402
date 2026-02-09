"""
AgentWalletFacilitatorSigner - Facilitator signer backed by agent-wallet provider.

Accepts an agent-wallet ``TronProvider`` or ``FlashProvider`` and extracts
the private key via ``TronProviderAdapter``.
"""

from __future__ import annotations

import logging
from typing import Any

from x402_tron.signers.adapter import TronProviderAdapter
from x402_tron.signers.facilitator.tron_signer import TronFacilitatorSigner

logger = logging.getLogger(__name__)


class AgentWalletFacilitatorSigner(TronFacilitatorSigner):
    """Facilitator signer that takes an agent-wallet provider directly.

    Usage::

        from wallet import TronProvider
        from x402_tron.signers.facilitator import AgentWalletFacilitatorSigner

        provider = TronProvider(private_key="deadbeef...")
        signer = AgentWalletFacilitatorSigner(provider, network="tron:nile")
    """

    def __init__(self, provider: Any, network: str | None = None) -> None:
        adapter = TronProviderAdapter(provider)
        super().__init__(private_key=adapter.get_private_key(), network=network)
        self._provider = provider
        logger.info(
            "AgentWalletFacilitatorSigner initialized: address=%s",
            self._address,
        )
