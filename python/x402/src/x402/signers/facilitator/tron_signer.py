"""
TronFacilitatorSigner - TRON facilitator 签名器实现
"""

import json
import time
from typing import Any

from x402.signers.facilitator.base import FacilitatorSigner


class TronFacilitatorSigner(FacilitatorSigner):
    """TRON facilitator 签名器实现"""

    def __init__(self, private_key: str, network: str | None = None) -> None:
        clean_key = private_key[2:] if private_key.startswith("0x") else private_key
        self._private_key = clean_key
        self._address = self._derive_address(clean_key)
        self._network = network
        self._tron_client: Any = None

    @classmethod
    def from_private_key(cls, private_key: str, network: str | None = None) -> "TronFacilitatorSigner":
        """从私钥创建签名器"""
        return cls(private_key, network)

    def _ensure_tron_client(self) -> Any:
        """延迟初始化 tron_client"""
        if self._tron_client is None and self._network:
            try:
                from tronpy import Tron
                self._tron_client = Tron(network=self._network)
            except ImportError:
                pass
        return self._tron_client

    @staticmethod
    def _derive_address(private_key: str) -> str:
        """从私钥派生 TRON 地址"""
        try:
            from tronpy.keys import PrivateKey
            pk = PrivateKey(bytes.fromhex(private_key))
            return pk.public_key.to_base58check_address()
        except ImportError:
            return f"T{private_key[:33]}"

    def get_address(self) -> str:
        return self._address

    async def verify_typed_data(
        self,
        address: str,
        domain: dict[str, Any],
        types: dict[str, Any],
        message: dict[str, Any],
        signature: str,
    ) -> bool:
        """验证 EIP-712 签名"""
        try:
            from eth_account import Account
            from eth_account.messages import encode_typed_data

            full_types = {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                ],
                **types,
            }

            typed_data = {
                "types": full_types,
                "primaryType": "PaymentPermit",
                "domain": domain,
                "message": message,
            }

            signable = encode_typed_data(full_data=typed_data)
            
            sig_bytes = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
            recovered = Account.recover_message(signable, signature=sig_bytes)

            tron_address = self._evm_to_tron_address(recovered)
            return tron_address.lower() == address.lower()
        except Exception:
            return False

    def _evm_to_tron_address(self, evm_address: str) -> str:
        """Convert EVM address to TRON address"""
        try:
            from tronpy.keys import to_base58check_address
            hex_addr = "41" + evm_address[2:].lower()
            return to_base58check_address(hex_addr)
        except ImportError:
            return evm_address

    async def write_contract(
        self,
        contract_address: str,
        abi: str,
        method: str,
        args: list[Any],
    ) -> str | None:
        """在 TRON 上执行合约交易"""
        client = self._ensure_tron_client()
        if client is None:
            raise RuntimeError("tronpy client required for contract calls")

        try:
            contract = client.get_contract(contract_address)
            
            func = getattr(contract.functions, method)
            txn = (
                func(*args)
                .with_owner(self._address)
                .fee_limit(1_000_000_000)
                .build()
                .sign(self._private_key)
            )
            
            result = txn.broadcast()
            return result.get("txid")
        except Exception as e:
            print(f"Contract call failed: {e}")
            return None

    async def wait_for_transaction_receipt(
        self,
        tx_hash: str,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """等待 TRON 交易确认"""
        client = self._ensure_tron_client()
        if client is None:
            raise RuntimeError("tronpy client required")

        start = time.time()
        while time.time() - start < timeout:
            try:
                info = client.get_transaction_info(tx_hash)
                if info and info.get("blockNumber"):
                    return {
                        "hash": tx_hash,
                        "blockNumber": str(info.get("blockNumber")),
                        "status": "confirmed" if info.get("receipt", {}).get("result") == "SUCCESS" else "failed",
                    }
            except Exception:
                pass
            time.sleep(3)

        raise TimeoutError(f"Transaction {tx_hash} not confirmed within {timeout}s")
