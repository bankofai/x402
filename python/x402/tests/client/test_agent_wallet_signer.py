"""
Tests for AgentWalletClientSigner and AgentWalletFacilitatorSigner.

Signer takes a provider directly (TronProvider / FlashProvider).
Provider handles keystore internally — signer doesn't know about it.
"""

import pytest

from x402_tron.signers.key_provider import KeyProvider
from x402_tron.signers.adapter import TronProviderAdapter
from x402_tron.signers.client import AgentWalletClientSigner
from x402_tron.signers.facilitator import AgentWalletFacilitatorSigner


TEST_PRIVATE_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class MockTronProvider:
    """Mimics agent-wallet's TronProvider for adapter testing."""

    def __init__(self, private_key: str):
        self._private_key_hex = private_key
        from tronpy.keys import PrivateKey

        clean = private_key[2:] if private_key.startswith("0x") else private_key
        pk = PrivateKey(bytes.fromhex(clean))
        self.address = pk.public_key.to_base58check_address()


# --- TronProviderAdapter ---


def test_adapter_satisfies_protocol():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    adapter = TronProviderAdapter(mock)
    assert isinstance(adapter, KeyProvider)


def test_adapter_get_address():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    adapter = TronProviderAdapter(mock)
    assert adapter.get_address().startswith("T")


def test_adapter_get_private_key():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    adapter = TronProviderAdapter(mock)
    assert adapter.get_private_key() == TEST_PRIVATE_KEY


def test_adapter_strips_0x_prefix():
    mock = MockTronProvider("0x" + TEST_PRIVATE_KEY)
    adapter = TronProviderAdapter(mock)
    assert adapter.get_private_key() == TEST_PRIVATE_KEY


def test_adapter_raises_on_missing_address():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    mock.address = None
    adapter = TronProviderAdapter(mock)
    with pytest.raises(ValueError, match="no address"):
        adapter.get_address()


def test_adapter_raises_on_missing_key():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    mock._private_key_hex = None
    adapter = TronProviderAdapter(mock)
    with pytest.raises(ValueError, match="no private key"):
        adapter.get_private_key()


# --- AgentWalletClientSigner ---


def test_client_signer_from_provider():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    signer = AgentWalletClientSigner(mock)
    assert signer.get_address().startswith("T")
    assert signer.get_address() == mock.address


def test_client_signer_same_address_as_tron_signer():
    from x402_tron.signers.client import TronClientSigner

    mock = MockTronProvider(TEST_PRIVATE_KEY)
    tron_signer = TronClientSigner(TEST_PRIVATE_KEY)
    agent_signer = AgentWalletClientSigner(mock)
    assert agent_signer.get_address() == tron_signer.get_address()


def test_client_signer_with_network():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    signer = AgentWalletClientSigner(mock, network="tron:nile")
    assert signer.get_address() == mock.address


# --- AgentWalletFacilitatorSigner ---


def test_facilitator_signer_from_provider():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    signer = AgentWalletFacilitatorSigner(mock)
    assert signer.get_address().startswith("T")
    assert signer.get_address() == mock.address


def test_facilitator_signer_same_address_as_tron_signer():
    from x402_tron.signers.facilitator import TronFacilitatorSigner

    mock = MockTronProvider(TEST_PRIVATE_KEY)
    tron_signer = TronFacilitatorSigner(TEST_PRIVATE_KEY)
    agent_signer = AgentWalletFacilitatorSigner(mock)
    assert agent_signer.get_address() == tron_signer.get_address()


def test_facilitator_signer_with_network():
    mock = MockTronProvider(TEST_PRIVATE_KEY)
    signer = AgentWalletFacilitatorSigner(mock, network="tron:nile")
    assert signer.get_address() == mock.address
