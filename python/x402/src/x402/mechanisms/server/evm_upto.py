"""
UptoEvmServerMechanism - "upto" 支付方案的 EVM 服务器机制
"""

from typing import Any

from x402.mechanisms.server.base import ServerMechanism
from x402.types import PaymentRequirements, PaymentRequirementsExtra


EVM_KNOWN_TOKENS: dict[str, dict[str, Any]] = {
    "eip155:1": {
        "USDC": {
            "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "decimals": 6,
            "name": "USD Coin",
            "version": "1",
        },
        "USDT": {
            "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "decimals": 6,
            "name": "Tether USD",
            "version": "1",
        },
    },
    "eip155:8453": {
        "USDC": {
            "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "decimals": 6,
            "name": "USD Coin",
            "version": "1",
        },
    },
    "eip155:11155111": {
        "USDC": {
            "address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "decimals": 6,
            "name": "USD Coin",
            "version": "1",
        },
    },
}


class UptoEvmServerMechanism(ServerMechanism):
    """"upto" 支付方案的 EVM 服务器机制"""

    def scheme(self) -> str:
        return "exact"

    async def parse_price(self, price: str, network: str) -> dict[str, Any]:
        """将价格字符串如 "100 USDC" 解析为资产金额

        Args:
            price: 价格字符串（例如 "100 USDC"）
            network: 网络标识符（例如 "eip155:8453"）

        Returns:
            包含 amount、asset、decimals 的字典
        """
        parts = price.strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid price format: {price}")

        amount_str, symbol = parts
        amount = float(amount_str)

        tokens = EVM_KNOWN_TOKENS.get(network, {})
        token_info = tokens.get(symbol.upper())

        if token_info is None:
            raise ValueError(f"Unknown token {symbol} on network {network}")

        decimals = token_info["decimals"]
        amount_smallest = int(amount * (10 ** decimals))

        return {
            "amount": amount_smallest,
            "asset": token_info["address"],
            "decimals": decimals,
            "symbol": symbol.upper(),
            "name": token_info["name"],
            "version": token_info["version"],
        }

    async def enhance_payment_requirements(
        self,
        requirements: PaymentRequirements,
        kind: str,
    ) -> PaymentRequirements:
        """Enhance payment requirements with token metadata"""
        if requirements.extra is None:
            requirements.extra = PaymentRequirementsExtra()

        tokens = EVM_KNOWN_TOKENS.get(requirements.network, {})
        for symbol, info in tokens.items():
            if info["address"].lower() == requirements.asset.lower():
                requirements.extra.name = info["name"]
                requirements.extra.version = info["version"]
                break

        return requirements

    def validate_payment_requirements(self, requirements: PaymentRequirements) -> bool:
        """Validate EVM payment requirements"""
        if not requirements.network.startswith("eip155:"):
            return False

        if not requirements.asset.startswith("0x") or len(requirements.asset) != 42:
            return False

        if not requirements.pay_to.startswith("0x") or len(requirements.pay_to) != 42:
            return False

        try:
            amount = int(requirements.amount)
            if amount <= 0:
                return False
        except ValueError:
            return False

        return True
