"""
服务器机制基础接口
"""

from abc import ABC, abstractmethod
from typing import Any

from x402.types import PaymentRequirements


class ServerMechanism(ABC):
    """
    服务器支付机制的抽象基类

    负责解析价格和增强支付要求
    """

    @abstractmethod
    def scheme(self) -> str:
        """获取支付方案名称"""
        pass

    @abstractmethod
    async def parse_price(self, price: str, network: str) -> dict[str, Any]:
        """
        将价格字符串解析为资产金额

        Args:
            price: 价格字符串（例如 "100 USDC"、"0.01 ETH"）
            network: 网络标识符

        Returns:
            包含 amount、asset、decimals 的字典
        """
        pass

    @abstractmethod
    async def enhance_payment_requirements(
        self,
        requirements: PaymentRequirements,
        kind: str,
    ) -> PaymentRequirements:
        """
        使用元数据增强支付要求

        Args:
            requirements: 基础支付要求
            kind: 交付模式（PAYMENT_ONLY 或 PAYMENT_AND_DELIVERY）

        Returns:
            增强后的 PaymentRequirements
        """
        pass

    @abstractmethod
    def validate_payment_requirements(self, requirements: PaymentRequirements) -> bool:
        """
        验证支付要求

        Args:
            requirements: 要验证的支付要求

        Returns:
            如果有效则返回 True
        """
        pass
